# Research — Lesson Display (Q1) and Bank/Lesson Markdown Editor (Q2)

---
date: 2026-08-09
topic: "Brief Q1 (lesson display 2026) and Q2 (bank/lesson markdown editor)"
brief: .planning/RESEARCH-BRIEF-learning-platform-2026-08-09.md (sections 1-3 binding)
confidence:
  q1_typography: HIGH (web-verified against gwern.net, Tufte CSS, Stripe/Markdoc, KaTeX docs, readability literature)
  q1_transfer_map: HIGH (checked directly against UI-SPEC.md sections 7-8 tokens)
  q2_editor_matrix: HIGH for CodeMirror 6 / Monaco / Tiptap / Milkdown / OverType facts; MEDIUM for cost estimates
  q2_recommendation: HIGH (grounded in model.py lint() LintError shape, read this session)
---

**Binding context honored:** runtime decides what reaches the learner; one parser/scorer/evidence
store; additive format changes; UI-SPEC §7 tokens and §8 accessibility gates (DOM rendering, WCAG AA,
keyboard-first, no answer leakage in DOM/ARIA). Constraints relaxed per brief §1: npm/bundlers allowed,
packaged app is a goal — but everything below still ships vendored/local, no CDN.

**Provenance note:** `[VERIFIED: …]` = confirmed via tool this session; `[CITED: url]` = official docs
referenced; `[ASSUMED]` = training knowledge, needs confirmation before it becomes a locked decision.

---

## Q1 — What an excellent lesson display looks like in 2026

Sources studied: [gwern.net/design + /sidenote](https://gwern.net/sidenote), [Tufte CSS](https://edwardtufte.github.io/tufte-css/),
Stripe docs / [Markdoc](https://www.stripay.io/blog/markdoc.html) teardowns, MDN, Execute Program
([spaced-repetition page](https://www.executeprogram.com/spaced-repetition)), Brilliant (ustwo/Koto case
studies), Distill.pub (distill format docs), Mathigon, KaTeX official docs, CSS-Tricks/Sara Soueidan
scrollspy patterns, readability literature (45–90ch measure, 66ch ideal).

The 2026 consensus among the best lesson/long-form surfaces is **not** a house look — it is a shared set
of block-level mechanics: constrained measure with wide-element escape, spaced (not indented) paragraphs,
anchored shallow headings, code blocks that are labeled + copyable + keyboard-reachable, display math that
scrolls rather than shrinks, notes kept adjacent to their reference, and orientation via a live TOC rather
than a gamified progress meter.

### D-Q1-1 · Heading hierarchy: three rendered levels, anchored, spacing-asymmetric — CONVENTION, ~0.5 day, Phase 03.1

- Render at most **h1 (lesson title) / h2 (section) / h3 (subsection)**. Every studied surface (MDN,
  Stripe, Distill) flattens beyond three levels; deeper nesting becomes lists or callouts. [ASSUMED —
  cross-site observation]
- **Anchor every h2/h3** with an id. We already have this for free: `model.py` computes `lesson_slug`
  for headings [VERIFIED: model.py:56-57, `"lesson_slug": lesson_slug(lesson_ref) if lesson_ref else ""` — the
  slugging machinery exists in the parser]. Show a link affordance on hover **and on focus** (MDN pattern);
  it must be a real `<a>` for keyboard users.
- **Spacing asymmetry**: much more space above a heading than below (≈ `space-6` 48px above h2,
  `space-3` 16px below; `space-5`/`space-2` for h3). This is what visually groups a section with its own
  content; every studied doc site does it. Fits our `space-1..7` scale exactly. **Transfers.**
- **Token mapping**: our type ramp is text-display 32 / text-heading 20 / text-body 16 / text-xs 12 with
  exactly two weights [VERIFIED: UI-SPEC.md §7 read this session]. So: h1 = text-display 32/700,
  h2 = text-heading 20/700, h3 = **text-body 16/700** (bold-body headings, the MDN/GitHub-docs move).
  No new size, no semibold tier needed. **Transfers cleanly; do not add a fifth size.**
- No automatic section numbering (gwern numbers sections; it reads as academic apparatus and adds
  cross-reference maintenance we don't need). **Conflicts with gwern, deliberately.**

### D-Q1-2 · Measure and paragraph rhythm: 68–72ch, spaced paragraphs, no indent — CONVENTION, ~0.25 day, Phase 03.1

- Body measure **max-width: 72ch** — already LOCKED in UI-SPEC §8 ("72ch maximum readable prose
  measure") and inside the research consensus of 45–90ch with ~66 ideal
  [CITED: uxpin.com/studio/blog/optimal-line-length-for-readability, webtypography.net/2.1.2]. **Transfers.**
- **Paragraph separation by space, not first-line indentation**: web-native; indentation is a print
  convention none of the studied surfaces use. Gap ≈ 0.75em–1em (use `space-3` 16px at 16px body).
  **Transfers.**
- Body 16px/1.5 per token. **Tension to record**: every dedicated long-form reading surface studied
  (gwern, Quanta, Distill, iA) sets long-form body at 18–21px [ASSUMED]. UI-SPEC locks text-body 16.
  Recommendation: keep 16 for the tracer; add a *reader text-size preference* in Settings later that
  scales the lesson column only (a derived token, not a fifth literal size). Flag for discuss-phase —
  this is a token-system decision, not a plan-level one. **Partially conflicts; resolvable additively.**
- Keep `system-ui` stack. Gwern/Quanta/Distill use serif body faces for identity [ASSUMED]; adopting a
  vendored serif is a Phase-4-token decision and pure preference. Do not spend the budget in 03.1.

### D-Q1-3 · Lists and tables: lists hold the measure, tables may escape it — RENDERER, ~0.5 day, Phase 03.1

- Lists: markers outside the text block with hanging indent (`padding-inline-start` ≈ `space-4`),
  item spacing ≈ half paragraph gap. Nested lists max 2 deep before the linter should warn (a
  LESSON-STYLE.md rule, machine-checkable). [ASSUMED — convention synthesis]
- Tables: the Distill/Tufte move that transfers directly — **wide elements may exceed the 72ch prose
  measure** up to the full activity column. Style: header row bold + `--line` bottom border, row
  separators only (no zebra, no vertical rules), `th` left-aligned, numeric columns right-aligned,
  `text-xs` for dense cells. Narrow viewport: labeled horizontal-scroll wrapper or definition rows —
  already LOCKED in UI-SPEC §3/§8. **Transfers.**

### D-Q1-4 · Code blocks: label tab, raw-copy button, focusable pre, NO line numbers in prose — RENDERER, ~1 day, Phase 03.1 (learner editor stays Phase 5)

Synthesis of Stripe/Markdoc + MkDocs-Material + a11y guidance
[CITED: mintlify.com/blog/stripe-docs; squidfunk.github.io/mkdocs-material/reference/code-blocks/;
whitep4nth3r.com/blog/how-to-build-a-copy-code-snippet-button/]:

- **Filename/label tab** rendered from the fence info string when authored (` ```python title=airway.py `
  or our own additive attribute) — a small `text-xs` chip on the block's top edge. Additive format change.
- **Copy button** that copies the raw source only — never line numbers, never highlight markup. Keep the
  raw text as the `<code>` content and decorations out-of-band, so copy = `textContent`. Button is a real
  `<button>`, keyboard reachable, gives visible "Copied" feedback via the existing `role=status` region.
  With JS off the button is absent and the text remains selectable — honest degradation.
- **`tabindex="0"` on the scrollable `<pre>`** so keyboard users can scroll overflowed code — a WCAG
  operability failure nearly everyone misses [CITED: Utah DS / a11y guidance in search results].
  `overflow-x: auto`, never wrap logical lines (UI-SPEC §8 already requires this for the editor).
- **No line numbers in lesson prose blocks.** Line numbers belong only where lines are referenced: the
  Phase 5 learner code editor (gutter already contracted in UI-SPEC §4 CodeEditor) and runnable `check`
  blocks. Stripe and MDN prose code omits them; they add copy hazards and noise. **Transfers; conflicts
  with "always number" doc-tool defaults, deliberately.**
- Syntax highlighting: defer. Ship monochrome code first (gwern ships near-monochrome). If added later,
  a build-time/daemon-side highlighter keeps JS out of the page. [ASSUMED]

### D-Q1-5 · Math: KaTeX inline in-flow; display blocks centered with x-scroll; numbering only when referenced — RENDERER, ~0.5 day on top of Phase 9 vendoring, Phase 09 (rules recorded in 03.1 style contract)

[CITED: katex.org/docs/issues.html; github.com/KaTeX/KaTeX/discussions/2942]

- Inline math (`$…$`) renders in text flow at text size, textstyle (no stacked limits), and may line-break
  after relations/binary operators — KaTeX's default. Never scale inline math above body size.
- Display math (`$$…$$`) is its own centered block; wrap with
  `.katex-display { overflow-x: auto; overflow-y: hidden; }` on the **containing** element to avoid the
  phantom vertical scrollbar — the documented KaTeX fix. Never shrink math to fit; scroll it.
- Equation numbers via CSS counters on `.katex-display` **only for equations the prose actually
  references**; unreferenced numbering is apparatus without a reader.
- Failure state: readable raw LaTeX source disclosure — already LOCKED (UI-SPEC §8.6). **Transfers.**

### D-Q1-6 · Figures: semantic figure/figcaption, captions below in text-xs, wide-escape allowed — RENDERER + FORMAT (alt required), ~0.5 day, Phase 03.1

- `<figure>` + `<figcaption>`, caption below the image, `text-xs`/12px with `--ink` at reduced emphasis,
  measure-width caption even when the figure escapes to column width (Distill's layout signature)
  [CITED: rstudio.github.io/distill — figure-wider-than-text layouts].
- **Alt text is a lint rule, not a hope**: a lesson image without alt is a lint *error* (additive check in
  `lint()` — it already accepts lesson data [VERIFIED: model.py:593-617, `def lint(questions, lesson=LESSON_UNCHECKED)`]).
  FORMAT change, additive.

### D-Q1-7 · Footnotes: inline disclosure notes, NOT margin sidenotes — RENDERER, ~1 day, Phase 03.1

The one place I recommend **against** the most beautiful pattern studied. Gwern/Tufte margin sidenotes
are the gold standard for wide screens [CITED: gwern.net/sidenote; edwardtufte.github.io/tufte-css], but:

- Our desktop layout already spends the right third on Contextual Support (UI-SPEC §3 LOCKED workspace).
  There is no free margin; sidenotes would fight the hint ladder for the same real estate. **Conflicts —
  structurally, not aesthetically.**
- Tufte CSS's own small-screen fallback is the pattern to adopt *everywhere*: the note collapses to a
  toggled inline expansion between paragraphs [CITED: github.com/edwardtufte/tufte-css/issues/11].
- Implementation: `<details class="note">` (or superscript `<a>` → inline `<details>`), which is
  keyboard-native, screen-reader-native, and works with JS off. Hover **popovers** for footnotes (gwern's
  other mode) are a JS enhancement to add later, and only with focus-triggered equivalents; they are the
  same machinery D1 key-term `<dfn>` hovers need, so build once in 03.1.

### D-Q1-8 · Reading progress: TOC scrollspy for orientation; NO progress bar — RENDERER, ~1 day, Phase 03.1

- A percentage progress bar is decorative pressure; UI-SPEC principle 5 (calm progress, LOCKED) and the
  context line's "3 of 8" already cover orientation. **Skip the bar — conflicts with Brilliant/Duolingo
  affordances, deliberately.**
- Instead: **section navigation with a live current-section marker**. Desktop: TOC in the support column
  (a labeled `<nav>`, above hints, collapsible). Tablet/narrow: the same `<nav>` inside the existing
  "Help and evidence" disclosure or top-of-lesson.
- Mechanism: IntersectionObserver toggling `aria-current="true"` on the active TOC link — the MDN
  pattern; style via `[aria-current]`, so the state is announced, not merely painted
  [CITED: css-tricks.com/table-of-contents-with-intersectionobserver/; MDN aria-current styling hook].
  Degraded (JS off): the TOC is still a plain anchor list — full function, no highlight.
- Long-lesson chunking: Execute Program and Brilliant both interleave short prose with a check rather
  than paginating [CITED: executeprogram.com/spaced-repetition — reviewable examples embedded per
  lesson]. That is the 06.2 executable-textbook loop, not a 03.1 scroll affordance; don't paginate
  lessons in 03.1.

### Q1 transfer/conflict summary against our token system

| Decision | Verdict vs UI-SPEC §7 tokens |
|---|---|
| 72ch measure, spaced paragraphs, spacing-asymmetric headings | Transfers as-is (space-1..7 covers all gaps) |
| 3-level headings on 4-size/2-weight ramp (h3 = bold body) | Transfers — requires discipline, no new tokens |
| Wide-escape tables/figures beyond 72ch | Transfers (activity column bound) |
| Code label tab + copy + focusable pre | Transfers; copy feedback uses existing `role=status` |
| KaTeX inline/display + x-scroll | Transfers; Phase 9 owns vendoring |
| 18px+ long-form body (gwern/Quanta/Distill) | **Conflicts** with text-body 16 — propose derived reader-size preference, decide in discuss-phase |
| Serif identity face | Conflicts with system-ui stack — defer, Phase 4 token decision |
| Margin sidenotes (Tufte/gwern) | **Conflicts** with support-column layout — adopt inline `<details>` notes instead |
| Progress bar / celebratory motion (Brilliant) | **Conflicts** with LOCKED calm-progress — rejected |
| Section auto-numbering (gwern) | Rejected as apparatus |

---

## Q2 — What the bank/lesson markdown editor should be

**Ground truth about our lint contract** [VERIFIED: model.py:593-607, read this session]:
`lint()` returns `(errors, warnings)` as **LintError records** where "`str(record)` reproduces the
historical 'Qn: message' text exactly; the code and field are additive machine-readable fields an
authoring agent can branch on without a lookup table." So diagnostics already carry `code` + `field`;
what they lack is **source positions**. Any editor choice that surfaces inline diagnostics needs the
daemon's lint endpoint to add `line`/`col` (or block char ranges) to each record — an **additive**
change, cheap because `parse_bank` splits on `^Q\d+\.` markers [VERIFIED: model.py:27-36] so block
start offsets fall out of the existing split.

### Candidate matrix

| Candidate | Inline diagnostics | Split preview + scroll sync | Markdown-native? | Bundle | License | Editor a11y / IME | Daemon integration effort | Verdict |
|---|---|---|---|---|---|---|---|---|
| **CodeMirror 6** | First-class: `@codemirror/lint` `Diagnostic{from,to,severity,message}` + lintGutter + tooltips; async lint sources designed for HTTP linters [CITED: codemirror.net/examples/lint/] | Editor pane + our own preview iframe/pane; CM gives per-line coords for sync | Yes — source stays plain text; our non-CommonMark item grammar is untouched | ~300KB core, tree-shakeable toward ~50KB min [CITED: npm-compare / pkgpulse comparisons] | MIT | contenteditable-based; explicitly supports screen readers, keyboard-only, IME composition state [CITED: codemirror.net] | Low: `linter(async doc => POST /lint)` debounced; map returned line/col to `from/to` | **RECOMMENDED** |
| Monaco | VS-Code-grade markers | Yes | Yes | **5–10MB** + worker infra [CITED: npm-compare.com/codemirror,monaco-editor] | MIT | Strong SR support; weak mobile/touch | Medium (loader/worker plumbing in a packaged app) | Reject: 20–100× the payload for LSP features we will never use against a bespoke grammar |
| Tiptap (ProseMirror) | Awkward: diagnostics against *markdown source* don't map to a rich-doc tree | WYSIWYG ≠ preview; no source pane | **No** — document-model-first; serializing back to our `Qn. / [TYPE:] / CORRECT:` grammar is lossy round-trip risk | Core moderate, tree-shakeable | Core MIT; pro extensions open-core/paid cloud [CITED: tiptap.dev/blog/release-notes/were-open-sourcing-more-of-tiptap] | A11y "left to the implementer" per 2025 framework review [CITED: liveblocks.io 2025 editor review] | High: custom node schema for every item construct | Reject — brief §3 already warns block editors cost a document model, selection model, and IME story |
| Milkdown | Same tree-mapping problem | Typora-style inline WYSIWYG | Markdown-first **but remark-based** — remark normalizes/reflows text it doesn't recognize; our item grammar is not CommonMark, so a save could rewrite `CORRECT:` blocks | Moderate | MIT | ProseMirror-inherited, thin docs | High: custom remark plugins for the whole bank grammar | Reject — "markdown-first" here means CommonMark-first, which we are not |
| Plain textarea + overlay (**OverType**, 2025) | **None inline** — a transparent textarea cannot underline ranges; diagnostics become a separate list | Overlay *is* the preview (styled div under textarea) [CITED: overtype.dev; github.com/panphora/overtype] | Yes | ~82KB, zero deps | MIT [ASSUMED — repo license not read this session] | Native textarea: best-in-class IME/undo/mobile by construction | Trivial | Attractive minimal fallback, but no inline lint = gives up our best authoring feature |
| **External editor + watch** (VS Code/Obsidian edit; we render+lint) | Their problem (or none) — we show the lint list on reload | Our reader *is* the preview; daemon watches mtime, SSE/poll refresh | Yes — file on disk is the single source of truth | 0 | — | The user's own editor: best possible | Trivial: mtime poll + `GET /lint?path=` | **Keep as first-class co-path**, not the only answer |
| 2025–26 successors (Lexical, etc.) | Lexical is rich-text-model-first — same objections as Tiptap | — | No | — | MIT | — | High | No new entrant changes the calculus; OverType is the only notable 2025 arrival [ASSUMED] |

### Recommendation — CodeMirror 6, with external-editor-plus-watch as a supported peer path and a server-rendered textarea as the degraded floor

**RUNTIME + RENDERER + PACKAGING · cost ≈ 4–6 days total · tech adoption in Phase 5, authoring surface in Phase 11 (see phase note below)**

Why CM6 over each alternative, in one line each:

- **Over Monaco**: same MIT license and diagnostics quality at 1/20th the size, with mobile/IME support
  Monaco lacks; Monaco's differentiator (LSP ecosystem) is worthless against a grammar only our
  `lint()` understands.
- **Over Tiptap/Milkdown/WYSIWYG**: the bank file on disk is the contract — one parser (`model.py`)
  must remain the only thing that interprets it. A WYSIWYG interposes a *second* document model that
  must round-trip our non-CommonMark item grammar losslessly on every save; that is a standing threat
  to "one parser" and to additive-format guarantees. The brief itself (§3, Notion weakness) says only
  adopt a block editor if raw markdown proves to be a real barrier. It has not.
- **Over textarea+overlay**: OverType is genuinely clever, but inline diagnostics are the whole reason
  to embed an editor at all. Our lint errors are positional and structured (`code`, `field`, Qn); an
  editor that can only show them in a side list is barely better than the CLI the user already has.
- **Over external-editor-only**: external-editor-plus-watch must exist anyway (it is the power-user
  path and the packaged app's escape hatch), but alone it fails B1 cold start — a new learner should
  not need VS Code configured to fix their first lint error — and it gives lint-on-save, not
  lint-as-you-type.

**Integration design (all additive):**

1. Daemon endpoint `POST /api/lint` — body: bank text; response: `[{line, col, endLine, endCol, code,
   field, severity, message}]`. Line ranges computed from `parse_bank`'s existing `^Q\d+\.` block split
   plus per-field regex spans; `str(record)` compatibility untouched.
2. CM6 `linter(async view => fetch('/api/lint'))`, debounced ~500ms, + `lintGutter()`. Diagnostics
   map 1:1 onto CM6's `Diagnostic` shape [CITED: codemirror.net/examples/lint/]. Daemon unreachable →
   editor stays usable, a typed StatusNotice says lint is offline — degrade, never block.
3. **Split preview with exact scroll sync**: because our own renderer is the preview (one parser — no
   second markdown engine ever), emit `data-line` on each rendered block and sync by nearest-line
   interpolation — the approach VS Code and Joplin converged on
   [CITED: dev.to/woai3c dual-pane sync writeup; joplin PR #5512]. Percentage sync is known-bad with
   images/math. Our preview is *authoritative* in a way no competitor's is: preview = the real lesson
   renderer, so authors see exactly what learners will (minus keys when previewing learner view).
4. **Packaging**: `npm` + esbuild produce one vendored JS asset served by the daemon — build step now
   allowed (brief §1), output committed/vendored so runtime stays offline-capable and CDN-free.
5. **Degraded path** (JS off / asset failed): server-rendered `<textarea>` + submit → daemon runs
   `lint()` → page re-renders with the classic `Qn: message` list above the textarea, each message an
   anchor. Full function, zero JS — the same guarantee as the quiz surface.
6. **Watch path**: `itembank edit --watch <bank>` (CLI twin) + daemon mtime poll; editing in
   VS Code/Obsidian live-refreshes preview+lint in the browser. ~0.5 day; ship it first.

**Phase note — partial disagreement with the task's assignment.** The *dependency decision* (CM6, npm,
esbuild, vendoring pipeline) belongs in **Phase 5**, which already owns "code editor" and where UI-SPEC
§4 currently contracts a plain textarea+gutter for the learner code editor. Options: (a) keep the
learner editor as the contracted textarea (small programs; contract already approved) and use CM6 only
for authoring, or (b) revise UI-SPEC to CM6 for both. Either way the **authoring editor surface** —
diff/approval, agent co-writing, the surface Q2 is really about — belongs in **Phase 11** (authoring
loop), with the watch path cheap enough to land in Phase 5 alongside the dependency. Recommend (b)
long-term (one editor dependency, two uses) but (a) is the low-risk tracer answer; this is a
discuss-phase decision because UI-SPEC §4's CodeEditor contract is currently LOCKED-adjacent.

### Q2 cost roll-up

| Item | Tag | Cost | Phase |
|---|---|---|---|
| `LintError` line/col fields + `/api/lint` | RUNTIME (additive) | 1 day | 5 |
| Watch mode (external editor path) | RUNTIME | 0.5 day | 5 |
| CM6 vendored build pipeline (npm+esbuild, committed asset) | PACKAGING | 1 day | 5 |
| CM6 editor + lint + split preview + data-line sync | RENDERER | 2–3 days | 11 (surface), tech proven in 5 |
| No-JS textarea + server-rendered lint floor | RENDERER | 0.5 day | 5 or 11 |

---

## Assumptions log

| # | Claim | Risk if wrong |
|---|---|---|
| A1 | 18–21px long-form body sizes on gwern/Quanta/Distill (not re-measured this session) | Low — the token tension exists regardless; resolve in discuss-phase |
| A2 | OverType MIT license | Low — only affects a rejected-anyway fallback |
| A3 | No 2025–26 editor entrant beats CM6 for source-editing + diagnostics | Low — CM6 facts verified; a better entrant would still face the same one-parser argument |
| A4 | Three-level heading flattening as cross-site consensus | Low — reversible CONVENTION |

## Sources

Primary: [gwern.net/sidenote](https://gwern.net/sidenote) · [Tufte CSS](https://edwardtufte.github.io/tufte-css/) ·
[KaTeX common issues](https://katex.org/docs/issues.html) · [CodeMirror lint example](https://codemirror.net/examples/lint/) ·
[codemirror.net](https://codemirror.net/) · [Tiptap open-sourcing notes](https://tiptap.dev/blog/release-notes/were-open-sourcing-more-of-tiptap) ·
[Milkdown](https://github.com/Milkdown/milkdown) · [OverType](https://overtype.dev/) · model.py (read this session).
Secondary: [Stripe docs teardown (Mintlify)](https://www.mintlify.com/blog/stripe-docs) · [Markdoc at Stripe](https://www.stripay.io/blog/markdoc.html) ·
[Execute Program spaced repetition](https://www.executeprogram.com/spaced-repetition) · [Brilliant × ustwo](https://ustwo.com/work/brilliant/) ·
[Distill R Markdown format](https://rstudio.github.io/distill/) · [Liveblocks 2025 editor review](https://liveblocks.io/blog/which-rich-text-editor-framework-should-you-choose-in-2025) ·
[npm-compare CM/Monaco](https://npm-compare.com/codemirror,monaco-editor) · [CSS-Tricks TOC + IntersectionObserver](https://css-tricks.com/table-of-contents-with-intersectionobserver/) ·
[dual-pane scroll sync](https://dev.to/woai3c/implementing-synchronous-scrolling-in-a-dual-pane-markdown-editor-5d75) · [Joplin sync-scroll PR](https://github.com/laurent22/joplin/pull/5512) ·
[MkDocs-Material code blocks](https://squidfunk.github.io/mkdocs-material/reference/code-blocks/) · [copy-button practice](https://whitep4nth3r.com/blog/how-to-build-a-copy-code-snippet-button/) ·
[optimal line length](https://www.uxpin.com/studio/blog/optimal-line-length-for-readability/) · [Tufte small-screen notes issue](https://github.com/edwardtufte/tufte-css/issues/11).
