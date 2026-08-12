---
phase: "14"
slug: reading-teaching-surface-quality-pass
status: draft
shadcn_initialized: false
preset: none
created: 2026-08-12
primary_input: ".planning/ROADMAP.md §Phase 14; browser session 2026-08-12; direct measurement of the vendored woff2 files"
constraint_basis: .planning/PLANNING-DIRECTIVES.md §4, §4a
inherits: [".planning/UI-SPEC.md", "03.1-UI-SPEC.md", "06-UI-SPEC.md", "06.2-UI-SPEC.md", "09-UI-SPEC.md"]
---

# Phase 14 — UI Design Contract: the Reading & Teaching Surface Quality Pass

> **This phase writes almost no new design. It makes the design that already exists actually
> render.** Four of the six ROADMAP criteria are failing not because a decision is missing but
> because a decision was made against a surface that never rendered it: the reader's spacing tokens
> resolve to nothing, the quiz page never joined the token system at all, the gloss popover has no
> position rule, and the hint ladder — the product's entire differentiator, fully specified and
> LOCKED in `06-UI-SPEC.md` — has no route to the browser. "Feels designed rather than assembled"
> is, here, mostly a matter of connecting the design to the pixels.

## 0. Authority, legend, and what this document may not do

| Label | Meaning |
|---|---|
| **INHERITED** | Restated from a prior LOCKED contract for the executor's convenience. Not a new decision. Cited to its source. If this document and its source ever disagree, the source wins. |
| **LOCKED (new)** | Settled here. Later phases build against it. |
| **DEFAULT** | This contract's decision, revisitable with a recorded reason and equal-or-better accessibility. |
| **BOTH** | Two defensible options shipped behind one named setting (Directive §3). Not arbitrated. |
| **MEASURED** | A number taken from the shipped font binaries or the shipped stylesheet this session, not from memory or from a style guide. Reproducible; the method is in §1. |
| **DEFECT** | A live, verified fault in shipped code. Fixing it is in scope; it is not a redesign. |
| **OPEN** | Deliberately not settled here. Named in §17 with a default so nothing blocks. |

**Authority order.** `ROADMAP.md` Phase 14 criteria 1–6 → `PLANNING-DIRECTIVES.md` §4 (the five
non-negotiables) → `.planning/UI-SPEC.md` (§7 copy and §8.1–8.9 accessibility gates are LOCKED) →
`03.1-UI-SPEC.md` (the reading surface) → `06-UI-SPEC.md` (the hint ladder) → this document.

**What this document may not do.**

1. It may not weaken §4.1 — *"The **runtime**, not a model, decides what reaches the learner."*
   Nothing below draws an affordance for a disclosure the runtime has not already released. The
   tier gate stays D-09's.
2. It may not restate the nine accessibility gates as a competing set. `.planning/UI-SPEC.md`
   §8.1–8.9 bind unchanged; §13 below names which bite hardest here and why.
3. It may not make a format change that is not additive. A bank with no `## TERMS` and no
   `## LESSON` must render byte-identically to today, proven by fixture (§15 gate 7).
4. It may not re-litigate the type scale, the weight pair, the palette source, the popover
   mechanism, the ladder card designs, or the copywriting contract. Those are LOCKED elsewhere and
   are INHERITED here.
5. It may not introduce a mechanic that assumes an audience: no streak, no celebration, no
   progress-to-answer countdown. Brilliant is the reference for craft only
   (`06-UI-SPEC.md` §6.4 already records this rejection against Brilliant by name).

---

## 1. Evidence — what was measured, and how

Everything numeric below is reproducible. Three measurements were taken this session.

**(a) The shipped stylesheet.** `theme.theme_css(DEFAULT_THEME_CONFIG) + presentation.SHARED_CSS`
was rendered and searched for custom-property definitions.

**(b) The vendored typefaces.** The four `fonts/**/*.woff2` files were parsed directly (WOFF2 table
directory → brotli stream → `head`, `hhea`, `OS/2`, `cmap` format 4, `hmtx`). Every type number in
§4 comes from these bytes, not from a specimen page.

| Face | upm | x-height | cap-height | glyph box (hhea) | `0` advance | freq-weighted avg char incl. space |
|---|---:|---:|---:|---:|---:|---:|
| Source Serif 4 Regular | 1000 | **475** (0.475 em) | 670 | **1.371 em** | **500** (0.500 em) | **447** (0.447 em) |
| Source Serif 4 Semibold | 1000 | 479 | 670 | 1.371 em | — | — |
| iA Writer Quattro S Regular | 1000 | **516** (0.516 em) | 698 | **1.300 em** | **600** (0.600 em) | **537** (0.537 em) |
| iA Writer Quattro S Bold | 1000 | 516 | 698 | 1.300 em | — | — |

Reference points for the same measurement on the faces the design was previously judged against:
Georgia x-height ≈ 0.484 em; Segoe UI (`system-ui` on this machine) x-height 0.500 em.

**(c) Contrast.** Every colour pair below was run through `theme.contrast_ratio`. Results in §3.3.

### 1.1 Four verified DEFECTs this phase is scoped to fix

| # | DEFECT | Evidence | Consequence |
|---|---|---|---|
| **D-A** | **`--space-1` … `--space-7` are referenced 64 times in `surfaces/lesson.py` and defined nowhere in the repository.** | Repo-wide search for `--space-N:` returns zero definitions. The rendered `theme_css() + SHARED_CSS` contains none. | Every `margin`/`padding`/`gap` declaration in `LESSON_CSS` is invalid at computed-value time and resolves to the initial value. **The reader has no paragraph rhythm, no callout padding, no side gutter, and no section spacing.** Criterion 2 cannot be judged until this is fixed. |
| **D-B** | **`surfaces/quiz_page.py` includes neither `presentation.SHARED_CSS` nor any `@font-face` rule.** | `TEMPLATE` substitutes `__THEME__` only. | The sat quiz has **never** rendered in Source Serif 4 or iA Writer Quattro and cannot today. The font-404 fix of 2026-08-12 repaired the reader; it did not reach the quiz. The quiz also names `system-ui` and `ui-monospace` literally, which `.planning/UI-SPEC.md` §7 forbids ("No surface may name a font family literally"). |
| **D-C** | **The gloss popover sets `position-anchor` but never uses it.** | `_gloss_anchor_css` emits `position:absolute; position-anchor:--anchor-<slug>; position-try-fallbacks:…` and no `position-area` or `anchor()` inset. | `position-anchor` alone positions nothing. The UA `[popover]` default (`inset:0; margin:auto`) wins, so the panel opens **centred in the viewport**, detached from the term that summoned it. The 2026-08-12 fix made it visible; it did not make it land anywhere. |
| **D-D** | **The authored hint ladder is unreachable from the browser.** | `runtime.teaching_transition` accepts `hint`/`stumped`; `session.do_hint(stumped=…)` still routes them; the daemon's `/api/hint` never passes `stumped`, and `quiz_page.py` contains no occurrence of the string `stumped`. | The six-tier ladder specified and LOCKED in `06-UI-SPEC.md` §5–§6 **does not exist on any browser surface**. The only "help" a sitting learner can reach is the Phase 8 model gate. This is the whole of criterion 5. |

Four further findings, recorded so they are not rediscovered:

- `RUNNABLE_CSS` (`lesson.py:418`) uses `var(--panel)` twice. No `--panel` token exists; the palette
  ships `--card` and `--chip`. Runnable code blocks render with no background. **Fix: `--chip`.**
- `ASSIST_COPY["lock_label"]` = `"Optional guidance is locked"` and the `&#128274;` padlock glyph
  appear **nowhere** in `.planning/`. They were invented at execution time, are not a LOCKED row of
  any copy table, and §9.5 rule 3 retires both.
- `lesson.py:411` documents that run-request errors are announced with `role="alert"`. **The code
  never sets it.** Full analysis and the binding fix are in §13.1, because the correct disposition
  depends on the live-region rule.
- A served quiz page can hold **three concurrent polite live regions** on a visual item, and a
  runnable lesson **five**, against gate §8.7's one. Inventory and dispositions: §13.1.

---

## 2. Design System — INHERITED, unchanged

| Property | Value |
|---|---|
| Tool | **None.** Python-emitted HTML/CSS with vanilla JS. No shadcn, no registry, no npm, no CDN. |
| Component approach | Native semantic HTML first. Popover API + CSS Anchor Positioning for the gloss (03.1 §8.1, LOCKED). Vendored KaTeX for Math (Phase 9). Vendored CodeMirror 6 for `check` items (Phase 5). |
| Icon library | None. Inline SVG, `aria-hidden`, paired with a text label (`.planning/UI-SPEC.md` §7.3). |
| Fonts | Vendored OFL 1.1: **Source Serif 4** 4.005R (Paper), **iA Writer Quattro S** (Ledger), served from `/assets/fonts/`. `system-ui` stack = Chrome voice; `ui-monospace` stack = Code voice. Manifest, SHA-256s and licences: `fonts/MANIFEST.json`, `fonts/REGISTRY-SAFETY.md`. |
| Font access rule | **A surface may never name a family literally.** Only `var(--font-paper)`, `var(--font-ledger)`, `var(--font-chrome)`, `var(--font-code)`. INHERITED, `.planning/UI-SPEC.md` §7. |
| Motion | 150 ms maximum functional transitions. No entrance animation on tier arrival, no celebration, no autoplay. `prefers-reduced-motion: reduce` removes all transitions and sets `scroll-behavior:auto`. INHERITED. |

**Voice assignment — INHERITED, `.planning/UI-SPEC.md` §7.1 and §7.3, LOCKED.** Voice is assigned by
*who authored the string*, never by visual preference.

| Voice | Token | Belongs to | In this phase |
|---|---|---|---|
| Paper | `--font-paper` | the author | lesson prose, **item stems**, **options**, **rationales**, `[!KEY]`/`[!EXAMPLE]` bodies, gloss definitions, shown-tier bodies |
| Ledger | `--font-ledger` | the runtime | verdicts, tier headers, locked-tier unlock sentences, `Hints` region label, callout small-caps labels, provenance ids, `StatusNotice` copy |
| Chrome | `--font-chrome` | the tool | nav, buttons, form labels, disclosure summaries, the section-nav list, figure captions |
| Code | `--font-code` | the machine under study | code blocks, learner code, canonical responses |
| *(none)* | — | **a model** | generated text renders in **Chrome** voice inside its labelled container. A model gets no voice. INHERITED §7.2.3. |

---

## 3. The token repair — the precondition for every other section

Nothing in §4–§11 can be implemented or judged until this lands. It is small, mechanical, and
introduces **no new scale, no new size, and no second palette**.

### 3.1 Spacing, radius — add to `presentation.py` SHARED_CSS `:root` — LOCKED (new), fixes D-A

The values are exactly `.planning/UI-SPEC.md` §7's 8-point scale and `03.1-UI-SPEC.md` §3's
assignments. This defines what 64 existing declarations already assume.

```css
:root{
  --space-1:4px; --space-2:8px; --space-3:16px; --space-4:24px;
  --space-5:32px; --space-6:48px; --space-7:64px;
  --r-1:6px;  /* --r-2:8px and --r-3:12px already ship */
}
```

| Token | Value | Canonical use (INHERITED, 03.1 §3) |
|---|---:|---|
| `--space-1` | 4px | icon-to-label gap; gloss inner tight gap |
| `--space-2` | 8px | popover offset from its trigger; list-item rhythm; sub-heading bottom margin |
| `--space-3` | 16px | side gutter; callout inner padding; heading bottom margin |
| `--space-4` | 24px | **paragraph rhythm (retuned, §5.1)**; callout block margin; glossary entry separation |
| `--space-5` | 32px | `h3` top margin; appendix top rule |
| `--space-6` | 48px | `h2` top margin (the asymmetric ramp) |
| `--space-7` | 64px | lesson foot padding; breathing before the glossary appendix |

**Exceptions — the complete list, so a spacing fixture has nothing left to flag.** The first four are
INHERITED unchanged from `03.1-UI-SPEC.md` §3; the fifth is added by this contract.

1. **44px minimum interactive target** everywhere **except** the inline `[[term]]` trigger
   (WCAG 2.2 §2.5.8 inline exception, compensated by the ≥44px glossary-appendix entry).
2. **`ch` measures** (`--measure-prose`, `--measure-wide`) are character measures, not pixel spacing,
   and are deliberately off the scale.
3. **1px `--line` and `--edge` hairlines** are borders, not spacing.
4. **Print `18mm`** is a physical unit; the pixel scale does not apply to paper.
5. **`padding-block:2px` on `.term`** (§7.4) — an optical adjustment to a text decoration's hit
   area, not layout spacing. It is deliberately *not* `--space-1`: 4px would begin to affect the
   inline box and disturb `--leading-lesson`, which is the exact failure 03.1 §3 names. Listed here
   so a scale fixture treats it as declared rather than as a stray.

### 3.2 `--panel` → `--chip` — LOCKED (new)

`RUNNABLE_CSS`'s two `var(--panel)` references become `var(--chip)`. No new token.

### 3.3 The semantic tokens the ladder needs — promoted from ASSUMED to **MEASURED**

`.planning/UI-SPEC.md` §7.1 named `--warn-bg`, `--unknown`/`--unknown-bg`, `--pending`/`--pending-bg`
as drafts "gated on a `contrast_ratio` fixture … A failing draft is re-picked, not waived."
**The fixture was run this session. All six pass AA in both modes on all three backgrounds.** They
are therefore adopted as-is. This unblocks `06-UI-SPEC.md` §5.5's unavailable-tier card, which
currently specifies a token that does not exist.

**Read the table exactly as labelled.** Every ratio is a **foreground token measured against three
backgrounds**. The `*-bg` tokens are the paired *backgrounds*, and are never themselves a text
colour — a fixture that measures `--warn-bg` against `--bg` gets 1.03 and is asserting the wrong
thing.

| Foreground token | Light | Dark | Paired background | fg on own-bg / fg on `--bg` / fg on `--card` |
|---|---|---|---|---|
| `--warn` *(already ships)* | `#8a5900` | `#e0a23a` | **`--warn-bg`** `#f8f1e2` / `#2b2312` *(new)* | light 5.32 / 5.46 / 5.98 · dark 6.95 / 8.33 / 7.59 |
| **`--unknown`** *(new)* | `#566067` | `#9aa7ad` | **`--unknown-bg`** `#edf0f2` / `#1b2325` *(new)* | light 5.62 / 5.87 / 6.43 · dark 6.47 / 7.54 / 6.87 |
| **`--pending`** *(new)* | `#5b4a9f` | `#b3a3e6` | **`--pending-bg`** `#efecf7` / `#221c33` *(new)* | light 6.16 / 6.56 / 7.18 · dark 7.25 / 8.24 / 7.51 |

Rules INHERITED unchanged: fixed per mode, **never** derived from the learner accent, **never**
colour alone — each requires an accompanying text label.

### 3.4 `--edge`: a control boundary that meets 3:1 — LOCKED (new)

**MEASURED problem.** `--line` against `--card` is **1.28:1** (light) and **1.26:1** (dark). On the
quiz page the response controls (`.choice`, `.opt`, `.seg button`, `textarea.ans`, `.case`) are
identified by a `1px solid var(--line)` border on a `--card` fill that sits 1.06:1 from the page
`--bg`. A learner therefore identifies the primary response control by a boundary at 1.28:1, which
fails WCAG 1.4.11 (3:1 for non-text content that identifies a UI component). This is not a taste
question and it is not new work invented by this phase — it is gate §8.8 not being met.

| Token | Light | Dark | `--edge` measured **on** `--card` / `--bg` / `--chip` |
|---|---|---|---|
| `--edge` | `#7f8b88` | `#697774` | light **3.53 / 3.22 / 3.13** · dark **3.63 / 3.98 / 3.28** |

**Where `--edge` replaces `--line`, and only here:** the border of any element that is itself an
interactive control or an input surface — `.choice`, `.opt`, `.seg button`, `button.go.ghost`,
`textarea.ans`, `.codewrap`, `.run-source`, `.run-go`, `.gate-opt` controls, `.lesson-table-scroll`
focus boundary, and the `.term` trigger's underline colour.

**Where `--line` stays, unchanged:** every non-interactive rule, card edge, table rule, divider,
`.callout` border, and the **dashed locked-tier border**. A locked tier's identity is carried by its
Ledger header and unlock sentence (`06-UI-SPEC.md` §5.2); the dashed hairline is a secondary
channel, which the never-colour-alone rule already requires.

### 3.5 Ownership

`surfaces/theme.py` remains the **single palette source** and gains only the six §3.3 values plus
`--edge`. `surfaces/presentation.py` SHARED_CSS owns the spacing/radius/voice/measure tokens.
No surface file gains a colour literal. INHERITED, LOCKED.

---

## 4. Type, re-derived against the faces that now actually render

ROADMAP criterion 2. Every judgement below is against the **MEASURED** metrics in §1(b).

### 4.1 The size does not need to change, and here is the number that says so

Source Serif 4's x-height is **0.475 em**. Georgia's — the face every prior spacing decision was
actually judged against — is 0.484 em. At `text-lesson` 18px that is **8.55px vs 8.71px**: a 1.8%
difference, invisible. **The 18px lesson size therefore stands, unchanged, now on evidence rather
than on assumption.** No churn is owed here, and a plan that proposes a sixth type size has
misread this section.

What *did* change under the swap is the **measure** and the **inline voice mix**, because those
depend on advance widths and x-height *ratios*, which differ by 12% and 9% respectively. §4.3
and §4.4.

### 4.2 The five project sizes are the only sizes — LOCKED (new), reconciling a live conflict

Two scales are in the tree and they disagree:

| Source | Scale | Status |
|---|---|---|
| `.planning/UI-SPEC.md` §7 + `03.1-UI-SPEC.md` §4 | **12 / 16 / 18 / 20 / 32** | the project contract |
| `presentation.py` docstring and CSS | 14 / 16 / 20 / 28 | Phase 4 local, stale |
| `quiz_page.py` | 10.5 / 11 / 12.5 / 13 / 13.5 / 14 / 14.5 / 15.5 / 17 / 18 / 20 / 28 / 34 | **twelve sizes, five of them fractional** |

**Ruling: the project scale wins. 12 / 16 / 18 / 20 / 32, at weights 400 / 600 only.** Reason, in
the same shape as the §7 weight ruling: the project contract is stated in two approved specs and
`lesson.py` — the newest surface — already obeys it; `presentation.py`'s docstring predates
`text-lesson` and the display-size row; and `quiz_page.py`'s twelve sizes are not a competing
system but the absence of one. Half-pixel type sizes are the single most legible symptom of
"assembled rather than designed", and they are the reason a learner reads the quiz and the reader
as two products.

**The rule that decides every ambiguous site — LOCKED (new).** `12px` is **not** a general "small
text" size. It is the label size, and it may carry only: non-interactive labels, small-caps Ledger
headers, provenance ids, chips, table column headers, and one-line compact status. **Any string
inside an interactive control, and any string a learner must read in order to recover from a
failure, is `16px` minimum.** A 12px disclosure summary or a 12px recovery sentence is a legibility
regression dressed as token conformance, and this rule exists to forbid it.

**Migration inventory — the whole of the change, by file and line.** In scope: the four files this
phase owns.

`presentation.py` — the shared primitive layer, so each of the eleven `14px` sites is disposed of
individually rather than in bulk:

| Line | Selector | Role | Becomes |
|---:|---|---|---|
| 109 | `.back` | **interactive** — the back link | **16px** |
| 124 | `.step details summary` | **interactive** — disclosure control | **16px** |
| 127 | `details.details-section summary` | **interactive** — disclosure control | **16px** |
| 146 | `.row .links` | **interactive** — link row | **16px** |
| 138 | `.state` | **recovery copy** — `StatusNotice` body a learner acts on | **16px** |
| 155 | `.status` | **recovery copy** — see the note below; this is the *same selector* the reader's degraded/style-warning notice uses | **16px** |
| 112 | `.context-line` | orientation metadata, Ledger | 12px |
| 120 | `.step-status` | one-line compact status | 12px |
| 151 | `.headline-label` | label under a figure | 12px |
| 154 | `.figure-label` | label | 12px |
| 159 | `th` | table column header (a label) | 12px |

**`.status` at 16px, not 12px — resolved rather than left to a reviewer.** The first draft sent
`presentation.py:155` to 12px as "one-line compact status", which contradicted this section's own
rule two rows above it. There is no second selector to scope the 12px to: `LESSON_CSS` defines no
`.status` rule, so the reader's Rule 1 announcing region — emitted at `lesson.py:1641` carrying the
degraded-lesson and style-warning recovery notices — is styled by exactly this declaration. That is
recovery copy, so it takes 16px alongside `.state`. Anything that genuinely is a compact status chip
uses `.step-status` (12px), which already exists for the purpose.
| 99, 150 | `h1`, `.headline` | display | `28px` → **32px** |

`lesson.py` — five `font-size` sites plus **two `font:` shorthand sites the first pass missed**,
both of which also name a family literally and so violate §2's no-literal-family rule:

| Line | Selector | Role | Becomes |
|---:|---|---|---|
| 96 | `.warn` | recovery copy naming a command | **16px** |
| 143 | `pre code` | code block, Ledger voice | **16px** (Quattro x-height 0.516 at 16px = 8.26px, matched to Paper's 8.55px at 18px) |
| 149 | `th,td` | split: `td` is content, `th` is a label | `td` **16px**, `th` **12px** |
| 151 | `.orphan` | muted note | 12px |
| 419 | `.run-source` — `font:14px/1.45 ui-monospace,…` | **editable control**; 16px also prevents focus-zoom on iOS | **16px**, family → `var(--font-code)` |
| 428 | `.run-stdout`, `.run-stderr` — `font:13px/1.45 ui-monospace,…` | dense machine output in a bounded scrollable pane, not prose — a **named exception**, see below | **12px**, family → `var(--font-code)` |
| *(no size today)* | `.run-status` | runtime assertion; declares no size, so it inherits the surrounding 18px Paper prose and puts a runtime string in the author's voice | **16px**, family → `var(--font-ledger)` |

**`.run-stderr` at 12px — the one named exception, and why it does not weaken the rule.** stderr is
text a learner reads after a failure, so the rule's plain reading points at 16px. It stays at 12px
because it is the *machine's* output verbatim — dense, arbitrarily long, in a `max-height` pane that
scrolls — and because the string the learner actually acts on is not in it: the recovery sentence is
`.run-status`, which this same table pins at **16px** in Ledger voice. The rule protects the
sentence a learner must read to recover; it does not oblige us to set a transcript at reading size.
**This is the only exception to the §4.2 rule in this contract**, and any second one is a sign the
rule is wrong rather than the site.

`quiz_page.py`:

| Now | Becomes | Count |
|---|---|---|
| `10.5`, `11` (48, 56, 137, 183, 193, 224, 235, 252) | `12px` | 8 |
| `12.5`, `13`, `13.5`, `14`, `14.5`, `15.5` (24 sites) | `16px` for prose, response text and anything inside a control; `12px` for labels, chips, provenance and one-line status — per the rule above | 24 |
| `17px` (1026, 2920) | `20px` | 2 |
| `34px` (212, `.score`) | `32px` | 1 |
| `.score` weight `700` (155) | `600` | 1 |
| `font:16px/1.55 system-ui,…` (31) | `var(--font-chrome)`, 16/1.5 | 1 |

The per-site split of those 24 is plan-time work against the rule above, not spec work.
`RUNNABLE_CSS`'s relative sizes (`.9em`, `.85em`, `.8em`) are a separate residue: they resolve
off-scale against whichever parent they inherit and are replaced with explicit tokens at plan time.

Out of scope but **owed**, and named so the debt is not lost: `day.py` (536, 564, 569), `study.py`
(99), `theme.py` settings CSS `14px` ×8. These are the Phase 4 cleanup the §7 weight ruling already
recorded; this phase does not widen its diff to reach them.

### 4.3 The measure is 12% wider than its own token name claims — LOCKED (new)

**MEASURED.** `1ch` is the advance of `0`. In Source Serif 4 that is **0.500 em** — but the
frequency-weighted average character in running English prose, spaces included, is **0.447 em**.
The ratio is **1.118**. In iA Writer Quattro the same ratio is **1.119**. The two vendored faces
agree to within 0.1%, so **one correction factor serves both voices**.

Consequences, at `text-lesson` 18px:

- `--measure-prose: 66ch` = 594px = **73.8 real characters per line**, not 66. That is over
  `.planning/UI-SPEC.md` §8's stated 72-character readable ceiling, and well past the 60–70 band
  where a serif at this x-height is comfortable.
- `--measure-wide: 90ch` = 810px ≈ 101 real characters.

**Retune, preserving each token's stated intent rather than its literal number:**

| Token | Was | Becomes | At 18px Paper | Real characters |
|---|---:|---:|---:|---:|
| `--measure-prose` | 66ch | **59ch** | 531px | **66** |
| `--measure-wide` | 90ch | **80ch** | 720px | ~90 (a container cap, not a reading target) |

**And the padding must stop eating the measure — DEFECT-adjacent.** `*{box-sizing:border-box}` is
global, and `.wrap` sets `max-width: var(--measure-prose)` with side padding *inside* it, so the
token has never been the content measure. Fix:

```css
.wrap{max-width:calc(var(--measure-prose) + 2 * var(--space-3));
      padding:var(--space-4) var(--space-3) var(--space-7)}
```

At 18px this is a 563px box holding a 531px / 66-character column. Tables, code, `[!EXAMPLE]`
parallel grids and math displays may still escape to `--measure-wide` (INHERITED, 03.1 §7.1).

### 4.4 Inline Ledger and Code inside Paper prose get x-height matching — LOCKED (new)

**MEASURED.** Quattro's x-height ratio is 0.516 against Source Serif's 0.475. A Ledger or Code span
set at the inherited 18px inside lesson prose therefore renders glyphs **8.6% larger** than the
prose around it — the classic inline-monospace bulge, and one of the loudest "assembled" tells on
a serif page.

```css
.lesson-prose :is(code, .ledger-inline, samp, kbd){ font-size-adjust: 0.475; }
```

`font-size-adjust` normalises the used glyph size to the Paper x-height (18 × 0.475/0.516 =
**16.6px used**) *without* changing the computed `font-size`, so no sixth size is introduced and
the §4.2 scale is untouched. Where unsupported it is ignored and the page renders exactly as it
does today — a free improvement with a zero-cost failure mode.

This rule applies **only** to inline runs inside Paper prose. Block-level Ledger and Code
(`pre code` at 12px, `.gate-note`, tier headers) already carry their own explicit size and must
not receive `font-size-adjust`.

### 4.5 Leading — INHERITED, and the measurement confirms it

`--leading-lesson: 1.65` stays. The justification improves: Source Serif's glyph box is
**1.371 em**, so at 18px the line box is 29.7px over a 24.7px glyph box, leaving **5.0px of visible
leading** — 0.59 × x-height. The same computation on 16px `system-ui` at 1.5 yields 2.7px, or
0.34 × x-height. The reader is already substantially more open than the UI chrome, which is
correct for sustained reading, and 1.65 is not loose. **No change.**

Ledger blocks: Quattro's glyph box is 1.300 em; at `text-xs` 12px with `line-height:1.4` the line
box is 16.8px over 15.6px. Single-line small-caps labels only — acceptable. Multi-line Ledger
bodies (locked-tier unlock sentences, `StatusNotice` copy) use **`line-height:1.5`**, giving 18px
over 15.6px. LOCKED (new).

### 4.6 Narrow viewports: Paper steps down one token — LOCKED (new)

**MEASURED.** At a 375px viewport with `--space-3` gutters the content column is 343px. At
`text-lesson` 18px (0.447 em average char = 8.05px) that is **42.6 characters per line** — below
the 45-character floor for comfortable reading.

```css
@media (max-width:479px){ .lesson-prose{ font-size:16px; } }
```

At 16px the same column carries **47.9 characters**. This uses `text-body`, an existing token; it
adds no size and no exception.

**Stated honestly rather than faked:** at a 320px viewport the column is 288px and yields
**40 characters** at 16px. Dropping below 16px to recover the floor would be a worse trade. The
45-character floor is therefore **not met at 320px and is not claimed to be**; the page remains
fully readable and horizontally scroll-free, which is what gate §8 actually requires.

---

## 5. Spacing and vertical rhythm for the reader

With §3.1 landed, these are the values the reader renders at. Everything not listed keeps its
shipped value.

### 5.1 Paragraph rhythm moves from `space-3` to `space-4` — LOCKED (new)

The one substantive spacing change, derived from §4.5: the lesson line box is **29.7px**. A 16px
paragraph gap is 0.54 of a line — the standard "too tight, reads as one grey slab" figure for
unindented prose. 24px is **0.81 of a line**, which is the conventional 0.75–1.0 band.

| Selector | Now | Becomes | Rationale |
|---|---|---|---|
| `.lesson-prose p` | `0 0 var(--space-3)` | `0 0 var(--space-4)` | 0.81 line |
| `.lesson-prose li` | `0 0 var(--space-3)` | `0 0 var(--space-2)` | items in a list are one unit; 8px separates without breaking it |
| `.lesson-prose :is(ul,ol)` | *(inherits `p`)* | `0 0 var(--space-4)` | the list as a block gets the paragraph gap |

The heading ramp is INHERITED unchanged and is now verified against the real line box: `h2`
`space-6` above / `space-3` below = 1.6 lines / 0.54 lines, a 3:1 asymmetry that binds a heading to
what follows it. `h3` `space-5` / `space-2` = 32/8, same shape. `h1` `0` / `space-3`.

### 5.2 Everything else — INHERITED

Callout inner padding `space-3`, callout block margin `space-4`, glossary entry separation
`space-4`, appendix top rule `space-5`, lesson foot `space-7`, side gutter `space-3`
(`space-2` below 360px). All were already written; §3.1 is what makes them render.

---

## 6. The header and scroll contract — ROADMAP criterion 1

### 6.1 Root cause, stated so the fix is not guessed at

The sticky context line is `position:sticky; top:0` and is 1px-bordered. On first item render the
served client calls `card.scrollIntoView({block:"start"})` (`quiz_page.py:623`, `:1202`). At
`scrollTop: 0` the card is already fully visible, but `block:"start"` scrolls its top edge to
viewport y=0 **anyway**, and the sticky band — which occupies the first ~38px (one row) to ~76px
(two rows) — then covers the first line of the stem. That is the 581×672 screenshot, exactly.

### 6.2 The fix — LOCKED (new)

**The scroll container is the document, and that was verified, not assumed.** `scroll-padding-top`
only works on the element that actually scrolls. On both in-scope surfaces the scrolling element is
the document: `quiz_page.py` sets `body{margin:0}` and `.wrap{max-width:800px;padding:…}` with **no**
`overflow` and no height constraint; `lesson.py`'s `.wrap` likewise. The only `overflow:auto`
regions in either file are `.case pre`, `.table-wrap`, `.scroll`, `.lesson-table-scroll`,
`.lesson-math-display` and the §7.1 gloss panel — all inner content wrappers, none of which contains
a scroll target. **Binding rule:** if a later shell puts the activity canvas inside a nested
overflow container, `scroll-padding-top` moves to that container in the same change; a
`scroll-padding-top` left on `html` while a nested container scrolls is silently inert, which is
this defect again with a new cause.

**Three rules. The first alone is sufficient; the other two are the belt.**

```css
html{ scroll-padding-top: calc(var(--sticky-h, 56px) + var(--space-2)); }
@media (max-width:767px){ html{ scroll-padding-top: calc(var(--sticky-h, 88px) + var(--space-2)); } }

.card, h2[id], h3[id], #glossary dt, [id].term-use, .gate{
  scroll-margin-top: calc(var(--sticky-h, 56px) + var(--space-2));
}
```

1. **`scroll-padding-top` on the scroll container.** `scrollIntoView` honours it, so *every*
   programmatic scroll, every in-page anchor (`Full entry`, `Back to first use`, the section nav)
   and every `:target` jump lands clear of the band with 8px of air. This is the single fix for
   criterion 1 and for the anchor-lands-under-the-header problem in §7 and §8.
2. **`--sticky-h` is measured, with a static fallback that is deliberately generous.** One
   `ResizeObserver` on `[data-surface-context]` writes
   `document.documentElement.style.setProperty("--sticky-h", h + "px")`.
   **The two numbers in this contract are not in conflict and a fixture must not assert either as
   the band height:** the band *measures* ≈38–40px at ≥768px (8px + a 12px/1.55 line + 10px + a 1px
   border) and 1–2 rows below that; the **fallback** is 56px / 88px, chosen above the measurement on
   purpose, because over-scrolling by 16px is invisible and under-scrolling by 1px is the whole
   defect. §10's "≈40px" is the measurement; §6.2's 56px is the no-JS fallback. **The fixture
   asserts clearance (≥8px of the stem visible below the band), never a band height.**
3. **Do not scroll a card that is already fully in view.** Guard the `scrollIntoView` call:
   `const r = card.getBoundingClientRect(); if (r.top < stickyH || r.bottom > innerHeight) card.scrollIntoView(...)`.
   The first item of a sitting then produces **no scroll at all**, which is both correct and
   calmer.

### 6.3 The band may never exceed two rows — LOCKED (new)

A sticky header that grows unbounded is the same defect with a different trigger. At `<768px` the
context line renders exactly **bank context** and **`Item N of M`** inline; **objective**, **mode**
and the **lesson link** move into the existing `Session details` disclosure directly below it. The
band is then one row at 375px and at most two if the bank name wraps.

`keyboard/SR:` the moved items keep their DOM order inside the disclosure; the disclosure summary
already announces its own state. Nothing is removed, only relocated.
`print:` the band prints as static text at the head of the record, mode included.
`degraded:` server-rendered; the band is correct before any script runs, at the fallback height.

### 6.4 Verification, at every supported viewport

Gate: at **1280 / 768 / 375 / 320** px, and at 200% zoom, with scripting **on and off**, the first
line of `h1.stem` is fully visible at first paint with ≥8px clearance below the band, and the same
holds after following each of: `Full entry`, `Back to first use`, a section-nav link, and
`Next item`.

---

## 7. The gloss — ROADMAP criterion 3

The mechanism, the DOM shape, the panel sizing, the `aria-details` association, the no-leak rule
and the "hover may never be the only path" rule are **INHERITED and LOCKED** from
`03.1-UI-SPEC.md` §8.1. This section adds the interaction design that §8.1 explicitly left open
("If hover-to-open is added it is additive over the click/focus path") and fixes D-C.

### 7.1 Placement — LOCKED (new), fixes D-C

```css
.gloss{
  position:absolute;
  position-anchor:var(--gloss-anchor);          /* per-slug, from the existing <style> block */
  position-area:block-end span-inline-end;      /* below the term, starting at its inline start */
  margin-block-start:var(--space-2);            /* 8px — 03.1 §3's "popover offset from its trigger" */
  position-try-fallbacks:flip-block, flip-inline, block-start span-inline-start;
  position-try-order:most-height;
  max-width:min(38ch, calc(100vw - var(--space-4)));
  max-height:min(60vh, 24rem);
  overflow:auto;
  overscroll-behavior:contain;
}
```

- **`position-area` is the missing line.** Without it `position-anchor` is inert and the UA's
  `inset:0; margin:auto` centres the panel. With it the panel sits 8px below the term, inline-start
  aligned.
- **The per-slug block changes shape, and this must not be missed.** `_gloss_anchor_css` currently
  emits `#gloss-<slug>{position:absolute; position-anchor:--anchor-<slug>; position-try-fallbacks:…}`
  — the *property* itself, per slug. The rule above sets `position-anchor:var(--gloss-anchor)` on
  the shared `.gloss` class, so the per-slug block must now emit **only the custom property**:
  `#gloss-<slug>{--gloss-anchor:--anchor-<slug>}`. If it keeps emitting `position-anchor` directly,
  the two rules fight on specificity — the id selector wins, `var(--gloss-anchor)` never applies,
  and the shared block's `position-area` anchors against nothing, which is D-C with an extra step.
  Every other declaration (`position:absolute`, `position-try-fallbacks`, sizing) moves out of the
  per-slug block into `.gloss`; the per-slug block shrinks to two custom-property lines, which is
  also the cheapest thing to emit per term. The `anchor-name` half on `button.term[popovertarget=…]`
  is unchanged.
- **Edges.** `flip-block` lifts the panel above the term near the viewport bottom; `flip-inline`
  pulls it back from the inline end near the right edge; the third fallback covers the corner.
  `position-try-order:most-height` prefers whichever side has room rather than the first that fits.
- **Long definitions** scroll inside the panel (`max-height`, `overscroll-behavior:contain`) and
  never grow past 60vh. There is no truncation and no ellipsis anywhere, per the shipped
  `presentation.py` discipline.
- **No anchor-positioning support:** the panel opens as a centred top-layer card. INHERITED, 03.1
  §8.1 — "a graceful platform fallback, not a defect to script around."

### 7.2 Coarse pointers below 768px get a bottom sheet — LOCKED (new)

```css
@media (max-width:767px) and (pointer:coarse){
  .gloss{ position:fixed; inset:auto 0 0 0; margin:0; max-width:none;
          max-height:60vh; border-radius:var(--r-3) var(--r-3) 0 0;
          border-inline:0; border-block-end:0; padding:var(--space-3) var(--space-3) var(--space-4); }
}
```

A 38ch panel anchored to a word on a 375px screen is a 340px box with nowhere to flip to. A bottom
sheet is the better interaction on touch *and* it makes the edge-flipping question disappear at the
width where it is hardest. Native light-dismiss (tap outside) and Escape still apply; the sheet is
still the same `[popover]` element, so nothing about focus, DOM order or the no-leak rule changes.
No animation — it appears, per §2's motion rule.

### 7.3 Hover intent — LOCKED (new), additive only

Enabled only under `@media (hover:hover) and (pointer:fine)`. **The click/focus path is complete on
its own and is never modified by this.**

| Behaviour | Value | Reason |
|---|---:|---|
| Open delay after `pointerenter` on `.term` | **180 ms** | Long enough that a pointer crossing a sentence never flashes a panel; short enough to feel immediate on intent. |
| Close delay after `pointerleave` of **both** trigger and panel | **260 ms** | The travel budget from the term to the panel 8px below it. Re-entering either during the delay cancels the close. |
| Open transition | **none** | §2 motion rule. It appears. |
| Cancel triggers | `scroll`, `pointerdown` anywhere, `keydown`, `visibilitychange` | A panel must never arrive after the learner has moved on. |

**Three rules that keep it from becoming a flicker war:**

1. A hover-opened panel is marked `data-gloss-open="hover"`. A click-opened panel is
   `data-gloss-open="click"` and is **pinned**: hovering a *different* term while a pinned panel is
   open opens nothing. The learner must click. This is the fix for two terms adjacent in one
   sentence — the second term cannot steal a panel the learner deliberately opened.
2. **Hover never moves focus.** Only click/Enter/Space does (native `popovertarget` behaviour,
   INHERITED).
3. Terms are `popover` (= `popover="auto"`), so opening one **natively closes any other**. Exactly
   one gloss panel can be open at any time, by platform guarantee rather than by our bookkeeping.
   State this in the plan so nobody writes the bookkeeping.

`keyboard/SR:` unchanged from 03.1 §8.1 — a real `<button>` in reading order, Enter/Space toggles,
Escape dismisses, focus returns to the trigger, `aria-details` associates the panel, and the
trigger carries **no** `title` and **no** `aria-label` (both a verbosity failure and a leak
channel). Hover intent is invisible to AT by construction.
`print:` INHERITED, `print_gloss: appendix | inline`.
`degraded:` the reader ships every definition inline, so the whole gloss — including the bottom
sheet — works with the network unplugged and before any script loads. Hover intent is the only part
that needs script, and its absence leaves a complete surface.

### 7.4 The trigger's own treatment — LOCKED (new)

```css
.term{ text-decoration:underline dotted var(--edge); text-underline-offset:.15em;
       text-decoration-thickness:from-font; padding-block:2px; }
```

Dotted underline in `--edge` (3:1, §3.4) rather than `currentColor`, so the affordance is legible
without shouting and without a second accent use. `padding-block:2px` enlarges the pointer target
without touching `--leading-lesson` — the failure 03.1 §3 names by name. It is declared as
**§3.1 exception 5**, not a stray. The WCAG 2.2 §2.5.8 inline exception continues to apply,
compensated by the ≥44px glossary-appendix entry.

### 7.5 Relationship to `[!KEY]` and to the appendix — LOCKED (new)

The question criterion 3 asks. The answer is a division of labour, and it is a rule, not a
preference:

| Surface | What it is | What it may contain |
|---|---|---|
| **Gloss panel** | a **lookup**. Transient, costs nothing, commits to nothing. | term, definition, `Full entry` link, and — when applicable — one `Also a key point` link. |
| **`[!KEY]` card** | a **commitment**. "This is on the exam"; it exports to Anki. | the authored body, the Ledger export footer, and the `Add to review` form. |
| **Glossary appendix** | the **record**. The print surface, the `Full entry` target, and the ≥44px target path the inline exception owes. | every term in authored order, each with `Back to first use`. |

**The gloss panel never carries an `Add to review` control.** A transient hover panel is the wrong
place for a decision that writes to a scheduler; putting it there would also make an accidental
hover one click from a commitment. The path is: gloss → `Also a key point` → the `[!KEY]` card,
which owns the control it always owned.

**`Also a key point` — DEFAULT.** When a `[!KEY]` block in the same lesson carries the same term
slug (a render-time lookup against the already-parsed `parse_key_blocks` output — no format change,
no new parse), the panel renders a second Ledger line linking to that card's anchor. When no such
block exists the line is absent. Copy: `Also a key point`.

### 7.6 `Full entry`, and getting back — LOCKED (new)

Three fixes to a link that currently jumps into the void:

1. **It lands clear of the sticky band** — §6.2's `scroll-margin-top` on `#glossary dt`.
2. **It closes the panel it was clicked from.** Without this the popover stays in the top layer,
   floating over the appendix. Four lines of script: on click inside `.gloss-more a`, call
   `panel.hidePopover()` before the fragment navigation. With scripting off the panel is dismissed
   by the next Escape or outside click — degraded but not broken.
3. **The arrival is visible.** `#glossary dt:target, #glossary dt:target + dd{ background:var(--chip); }`
   with `border-inline-start:2px solid var(--accent)` on the `dt`. Colour is not the only channel —
   the `:target` entry is also the scroll destination, which is the primary cue.

**And the way back — the "back to text" link, criterion 4's second half.** Each `.term` trigger
gains a stable `id="use-<slug>"` on its **first** marked occurrence (the first-use machinery
already exists for `gloss_marks: first-use` and for print). The appendix's existing `Back to first
use` anchor targets it. Enhancement, when script is present: if the appendix was reached from a
specific trigger, that entry's back link swaps `href` to the originating occurrence and its label
to **`Back to the text`** (DEFAULT). Baseline without script: `Back to first use`, INHERITED and
unchanged.

**There is no "back to the section nav" link.** The browser's back button covers it, and a second
back-affordance on a reading page is clutter. Recorded so it is not invented.

---

## 8. The reader section nav — ROADMAP criterion 4

`reader_nav: none | column` with DEFAULT `none` is INHERITED from `03.1-UI-SPEC.md` §7.1. It was
chosen when "there is no real bank yet … the length at which orientation starts paying is
unmeasured", and 03.1 explicitly says "Revisit against the Phase 3.2 corpus." Phase 3.2 has landed.
This is the revisit.

### 8.1 `reader_nav: none | column | rail | auto`, DEFAULT **`auto`** — BOTH (Directive §3)

| Value | Renders | Available at |
|---|---|---|
| `none` | no nav | forced override |
| `column` | the shipped `<details class="reader-nav">`, always | forced override |
| `rail` | a sticky nav in the left margin outside the reading column | ≥1280px only; below that it renders `column` |
| **`auto`** | `column` when the lesson has **≥4 `###` sections**, otherwise `none`; `rail` instead of `column` at ≥1280px | **DEFAULT** |

**Why `auto` is the default.** The 03.1 rationale for `none` was an unmeasured-length argument, not
a design objection — a two-section lesson does not need a table of contents and a nine-section one
does. "≥4 sections" is a rule an executor implements in one line and a fixture asserts exactly;
a word count is not.

**Why `rail` is now allowed.** 03.1 rejected the margin rail (R3) for Phase 3.1 on two grounds:
"the support column already owns that third", and "a third responsive behaviour to test at three
widths". It recorded the rejection as "the reason a **later shell revision** might revisit
UI-SPEC §3, not as a 3.1 option", and called it "the most distinctive of the three". Both grounds
are answered here: **the standalone reader has no support column** (the lesson *is* the activity,
03.1 §7.3), and the rail is gated to a single breakpoint at which it is the only variant, so it adds
one responsive case rather than three. It is not the default; per Directive §3 it is registered, not
arbitrated.

### 8.2 What it looks like — LOCKED (new)

**`column` (768–1279px, and ≥1280px when `rail` is off).** Placed after `<h1>`/`.sub` and before the
first section — permitted by 03.1 §7.3's reasoned reading of C16 ("a table of contents is
*navigation to* the activity, not support *about* it"). Native `<details>`, **open by default at
≥1024px, closed below**.

```
SECTIONS IN THIS LESSON                        ← Ledger, text-xs, .08em, uppercase, --mut
  01  Airway anatomy                           ← number Ledger text-xs; title Chrome text-body
  02  Indications for an OPA
  03  Sizing and insertion
```

Summary in Ledger; list items in **Chrome** voice (the nav is the tool, not the author);
`list-style:none`; item rhythm `--space-2`; each anchor a real `<a href="#slug">` with a **44px**
minimum row height (this is a navigation control, so the inline exception does not apply).

**`rail` (≥1280px).** The same markup, `<details open>` with the disclosure triangle suppressed,
placed in a `grid-template-columns: minmax(0,1fr) auto` shell so the reading column stays exactly
where `column` puts it and the rail occupies otherwise-empty margin. `position:sticky;
top:calc(var(--sticky-h,56px) + var(--space-4)); max-height:calc(100vh - var(--sticky-h,56px) - var(--space-6)); overflow:auto`.
Width `18ch`, titles wrap, no ellipsis. The reading measure **does not change** between `rail` and
`column` — that is what makes the rail free rather than a second layout.

**Current-section highlighting is optional and, if present, must be announced not merely painted**
(INHERITED, 03.1 §7.1): `aria-current="true"` on the anchor, plus a 2px `--accent`
`border-inline-start`. No scroll-spy is required; a `:target`-driven highlight is sufficient and
needs no script.

### 8.3 Long, multi-section lessons

- The nav scrolls inside itself (`rail`) or inside the open `<details>` (`column`,
  `max-height:40vh; overflow:auto`) rather than pushing the lesson off the first screen.
- Section titles wrap to as many lines as they need. No `nowrap`, no ellipsis.
- Under Phase 6.2 gated reading the filtered nav copy is INHERITED and unchanged:
  `More sections appear as you clear each check.`

`keyboard/SR:` a labelled `<nav>` of real anchors in reading order; headings remain real headings;
nothing is pointer-only; `<details>` announces its own state.
`print:` `display:none`, INHERITED — "a printed page does not need a TOC of itself".
**Note the DEFECT this replaces:** until 2026-08-12 that print rule leaked to screen. The fix is to
scope it inside `@media print`, not to delete it.
`degraded:` server-rendered static anchors. Nothing here needs script.

### 8.4 In a sitting, the ladder wins — INHERITED, restated

`03.1-UI-SPEC.md` §7.3, LOCKED: when an item is active the lesson is *support*, so the nav goes
**below the hint ladder**, collapsed, inside the in-flow support region. The support region's order
is **hints → document navigation → evidence**. §9 builds on this and does not modify it.

---

## 9. The wrong-answer surface — ROADMAP criterion 5

> This is the moment the whole product exists for, and today it is one red sentence and a collapsed
> `<details>`. The reason is D-D: **the ladder that `06-UI-SPEC.md` fully specifies has no route to
> the browser.** This section is therefore mostly an act of connection, plus four genuinely new
> calls (§9.2, §9.4, §9.5, §9.6). Every card design, every locked-tier string and every mode rule
> below is INHERITED verbatim from `06-UI-SPEC.md` §5–§7 and is not re-litigated.

### 9.1 What must exist before any of this renders — the payload contract

The browser must never derive entitlement, never count attempts, and never decide what a tier
contains. The runtime already owns all three. Phase 14 requires one route that exposes what the
runtime already computes:

```
POST /api/teach   { session_id, action: { kind: "hint" | "stumped" } }
→ { shown: [ { index, name, label, header, display } … ],
    next_locked: { index, name, header, unlock_copy } | null,
    entitled: bool,          /* a tier is unlocked and not yet shown */
    exhausted: bool,
    unlock_path: "attempt" | "stumped" }
```

**LOCKED (new), and this is the D-09 boundary in one sentence: the browser renders `shown` and
`next_locked` and nothing else.** It does not receive unshown tier bodies, does not receive
`highest_tier_unlocked` as a number it could reason about, and cannot construct a request for a
specific tier. `display` is text the runtime already resolved (`runtime.authored_hint` returns it
today); the client never re-derives display text from an id.

Whether this is a new route, a widened `/api/submit` action envelope, or `/api/hint` gaining a
`kind`, is the **plan's** call — it is plumbing, not design. The daemon's existing
`API_ACTION_FORBIDDEN_FIELDS` gate (which refuses `tier`, `reveal`, `advance`, `correct` by name)
applies unchanged.

### 9.2 The shell: the sat quiz is the tablet shell at every width — LOCKED (new)

`06-UI-SPEC.md` §6.1 places the ladder in the *support column* and rejected option H3
(inline-under-the-item) because `.planning/UI-SPEC.md` §3 reserves the activity canvas. The sat
quiz has **no support column** — it is one 800px column. Rather than invent a third answer, apply
§3's own tablet rule, which already covers exactly this shape:

> *"Tablet (768–1023px): activity is full width; support opens as an in-flow 'Help and evidence'
> disclosure after the active response controls."*

**Ruling: the sat quiz is the tablet shell at every viewport width, and `hint_display` resolves to
`slot` there.** The support region is in-flow, immediately after the response controls and the
reserved feedback slot, before the next action. This is not H3 — H3 put hint content *inside* the
activity canvas; this puts it in the support region that §3 defines for a single-column shell. When
the two-column workspace exists (a later shell revision), `hint_display: rail` becomes available at
≥1024px with no change to any of this.

### 9.3 The state machine

Names are binding; a plan and a fixture use these strings.

```
PRE_ANSWER ──submit──▶ SUBMITTING
SUBMITTING ──empty──────────────▶ PRE_ANSWER + EMPTY_NOTICE       (no attempt recorded)
SUBMITTING ──same canonical─────▶ HELD      + DUPLICATE_NOTICE    (no tier movement)
SUBMITTING ──correct────────────▶ CORRECT ──▶ next activity
SUBMITTING ──wrong, drill───────▶ REVEAL_AND_ADVANCE
SUBMITTING ──wrong, diag/exam───▶ DEFERRED
SUBMITTING ──wrong, practice────▶ HELD_FIRST     (one tier unlocks, none shown)
HELD_FIRST ──open next hint─────▶ HELD_TIER_SHOWN
HELD_TIER_SHOWN ──changed retry, wrong──▶ HELD_REPEAT   (one more tier unlocks)
HELD_* ──I'm stumped────────────▶ HELD_TIER_SHOWN       (unlocks and shows exactly one)
HELD_* ──tier 5 shown───────────▶ REVEALED
REVEALED ──any submit───────────▶ advance
```

Rendering per state — the `role=status` copy column below is announced through the single Rule 1
region defined in §13.1; the support region holds the ladder and announces nothing:

| State | `role=status` copy (Ledger) | Support region | Controls |
|---|---|---|---|
| `HELD_FIRST` | `Not correct. Try a different answer, or open the next hint.` | `Hints` heading; **no shown cards**; the next locked card | `Check answer` (re-enabled), `Open the next hint` |
| `HELD_TIER_SHOWN` | unchanged from `HELD_FIRST` | shown tier cards in index order, then the next locked card | `Check answer`, `Open the next hint` *(if entitled)* **or** `I'm stumped — show the next hint` *(if not)* |
| `HELD_REPEAT` | unchanged | one more shown card is now available; the rail grows, nothing is replaced | as above |
| `DUPLICATE_NOTICE` | `That is the same answer as before. Change it, or use "I'm stumped" to open the next hint.` | unchanged — **no tier movement** | `Check answer`, `I'm stumped — show the next hint` |
| `EMPTY_NOTICE` | `Enter an answer before checking. An empty answer does not open a hint.` | unchanged | `Check answer` |
| `REVEALED` | `The answer is shown above. Move on when you're ready.` | full ladder, tier 5 shown; no locked cards remain | `Next item` |
| `DEFERRED` (diagnostic) | `Diagnostic mode records your answers and shows nothing until the sitting ends.` | ladder block **absent with that stated reason** | `Next item` |
| `DEFERRED` (exam) | `Exam mode holds all feedback until this attempt has been marked.` | ladder block **absent with that stated reason** | `Next item` |
| drill | verdict + explanation immediately | `Drill mode shows the answer straight away. The hint ladder does not run here.` | `Next item` |

Every string in that column is **INHERITED verbatim** from `06-UI-SPEC.md` §7. The only new string
is `Open the next hint` (§14). The **currently shipped** sentence — `Not correct yet — the card
stays open. Optional guidance is available under Help and evidence below.` — is **retired**: it
describes a mechanism instead of an action, and it points at the model panel as if that were the
help, which is precisely the inversion §9.5 fixes.

`06-UI-SPEC.md` §6.4 binds: **a new tier card arrives with no entrance animation, no highlight
pulse, and no scroll-into-view.** One `role=status` update, no focus jump. Focus stays on the
control the learner pressed (gate §8.3).

### 9.4 Layout of the held card — LOCKED (new)

```
┌ card ─────────────────────────────────────────────────────────┐
│  h1.stem                          — Paper, 32/1.2, 600        │
│  the learner's answer, still visible and still selected       │
│  [Check answer]                                               │
│  ┌ feedback (reserved, min-height) ──────────────────────┐    │
│  │ Not correct. Try a different answer, or open the      │    │  Ledger 16/1.5, --bad
│  │ next hint.                                            │    │
│  └───────────────────────────────────────────────────────┘    │
├───────────────────────────────────────────────────────────────┤
│  HINTS                            — Ledger, 12px, .08em, --mut│
│  ┌ TIER 0 · LESSON ────────────────────────────────────┐      │  --card, 1px --line, --r-2
│  │ Read: Airway adjuncts                               │      │  Chrome link; slug in Code voice
│  └─────────────────────────────────────────────────────┘      │
│  ┌╌ TIER 1 · OBJECTIVE ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┐      │  --chip, 1px dashed --line
│  ╎ Tier 1 unlocks after another attempt.               ╎      │  Ledger 12/1.5
│  ╎ Or unlock it now with "I'm stumped".                 ╎      │
│  └╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┘      │
│  … remaining locked tiers (hint_locked_preview: full) …       │
│  [ I'm stumped — show the next hint ]                         │
│  ▸ Sections in this lesson                                    │  document nav, second
│  ▸ Help and evidence                                          │  generated help, third, collapsed
└───────────────────────────────────────────────────────────────┘
```

Concrete values, all from the existing scale: ladder is an `<ol>`, `list-style:none`, card padding
`--space-3`, gap between cards `--space-2`, `Hints` heading margin `--space-4` above /
`--space-2` below, region separated from the activity by a full-measure 1px `--line` rule. Shown
card bodies are **Paper 16/1.5**; headers and locked bodies are **Ledger 12/1.5**. Locked and shown
cards have **identical padding** so the rail does not jitter as tiers arrive (`06-UI-SPEC.md` §2
exception 2, INHERITED).

`hint_display: slot` (§9.2) means: the most recent shown tier renders as one card, earlier shown
tiers collapse behind `<details>` labelled `Hints shown (2)`, and the next locked card and the next
legal action follow. INHERITED, `06-UI-SPEC.md` §6.1.

The three ordering rules are INHERITED and testable: **hints → document navigation → evidence**
(03.1 §7.3); support follows the activity in DOM order (UI-SPEC §3); and one announcing region,
in the activity canvas — **per §13.1 rules 1–4, which is the single authority on live regions in
this document. Neither this section nor §9.5 restates it.**

### 9.5 The offline path is not a degraded path — LOCKED (new)

Criterion 5's hardest requirement: *"The offline path must not read as a degraded version of a
better online product."* Four rules make that true structurally rather than by reassurance.

1. **The authored ladder is the product; generated help is an accessory.** The ladder is
   unconditionally visible, full measure, above. Generated help lives inside a collapsed
   `<details>` labelled `Help and evidence`, **below** the ladder and below the section nav. With
   the model unreachable the page loses a collapsed disclosure's contents. The teaching surface is
   untouched.
2. **Absence is communicated by the absence of an offer, and by nothing else.** No banner, no
   status chip, no colour, no "offline mode" badge. The LOCKED string
   `Generated help is unavailable. You can keep learning with the lesson and authored hints.`
   renders as **static text inside the `Help and evidence` disclosure — with no live region of any
   kind in its steady state** (§13.1 rules 3 and 5 — the region is live only for the seconds between
   the learner's press and their answer arriving, then reverts to static text). It is seen only by a
   learner who opened the disclosure and pressed `Get optional guidance`, and it is spoken only to a
   learner who did exactly that.
   Routing it through the shared canvas region instead would announce the model's absence to every
   learner on every wrong answer, which is precisely the "page that announces what it does not
   have" this section exists to prevent. **This is why the single-region rule and this rule do not
   conflict: the sentence is not an announcement, it is the result the learner asked for.**
3. **Retire the padlock.** The `&#128274;` glyph and the `assist-lock` card are removed. Neither is
   a LOCKED row of any copy or component table (verified: `"Optional guidance is locked"` appears
   nowhere in `.planning/`), and a padlock connotes a paywall while colliding with the *legitimate*
   lock language — the dashed tier card, which is the one place in this product where "locked" means
   something. **Dashed border = a runtime tier gate. Nothing else in the UI may use lock imagery.**
   The `lock_label` string is retired with it; the unavailable sentence stands alone and says more.
4. **The authored hint the panel currently shows is not a hint ladder.** Today the model panel's
   fallback renders a single `Authored hint` block that shows only the lesson section title — which
   is tier 0 with no ladder around it, mistaken for the whole of the authored path. Once §9.1 lands,
   that block is **removed** and the disclosure carries generated content and provenance only. The
   authored path is the ladder, in one place.

`degraded:` shown tiers are server-rendered and the stumped control is a form POST, so the whole
ladder is operable before any script loads and over a flaky link (INHERITED, `06-UI-SPEC.md` §6.1).
Sitting, scoring, the ladder, the reader, the gloss, evidence and the report all work with the
network unplugged — `CLAUDE.md:57`'s "degrade, never block", which is Phase 14's §15 gate 5.

### 9.6 Nothing may pre-announce a reveal — LOCKED (new), ROADMAP criterion 6

Bright-line rules a fixture can assert:

- **No progress indicator over the ladder.** No "3 of 6", no bar, no dots. A count of *shown* tiers
  is permitted only where 06 already permits it (`hint_locked_preview: next`'s
  `{k} more tiers after this one.`). Six locked cards showing their own unlock conditions is the
  honest depiction; a progress bar to the answer converts teaching into a countdown.
- **No "Show answer" control, ever.** Tier 5 is reached by the same two paths as every other tier.
- **No dimmed, greyed, or `aria-disabled` reveal affordance.** A tier the runtime would refuse is
  not drawn at all — 06 §6.5's "absent with a stated reason, never a rail of greyed cards".
- **A locked card contains its header and its unlock sentence and nothing else** — no body, no
  availability flag, no `title`, no `aria-label`, no CSS-off text, no `data-*` carrying content.
  Availability is disclosed at the moment a tier is shown, never before (06 §5.2, LOCKED).
- **No first person and no encouragement anywhere in the ladder.** No "I", no "let's", no "you're
  close". A rule chose; a personality did not (06 §5.1, LOCKED).

---

## 10. Responsive matrix

| | 1280px | 768px | 375px | 320px / 200% zoom |
|---|---|---|---|---|
| Reader column | 59ch = 531px content, centred | same, viewport-capped | viewport − 32px; Paper steps to 16px (§4.6) | viewport − 16px; 40 chars, stated not faked |
| Section nav | `rail` (sticky, 18ch) | `column`, `<details>` closed | `column`, `<details>` closed | same |
| Gloss | anchored panel, 38ch | anchored panel | **bottom sheet** (coarse pointer) | bottom sheet |
| Sticky band | 1 row, measured ≈38–40px (fallback 56px, §6.2) | 1–2 rows (fallback 88px) | 1 row; objective/mode/lesson move into `Session details` (§6.3) | same |
| Quiz shell | one 800px column, `hint_display: slot` | same | same | same |
| Ladder | full `hint_locked_preview` | full | `slot` collapses earlier tiers behind `Hints shown (n)` | same |
| Tables / code / math | escape to `--measure-wide` 80ch | labelled scroll wrapper | labelled scroll wrapper | labelled scroll wrapper; page never widens |

Long content, INHERITED: prose wraps; ids and code scroll horizontally inside their labelled
wrapper; citations wrap without ellipsis; every chip and meta string may wrap to a second line.
There is no `nowrap` and no `text-overflow` anywhere in this project (`presentation.py` discipline).

---

## 11. Voice repair on the quiz page — the largest single "feels designed" lever

Fixing D-B is what makes the sat quiz look like the same product as the reader.

| Element | Now | Becomes | Authority |
|---|---|---|---|
| Document body font | literal `system-ui,…` | `var(--font-chrome)` | UI-SPEC §7 — no literal family |
| `h1.stem` | body sans, 28px | **`var(--font-paper)`, 32/1.2, 600** | §7.1 — "item stems" are Paper voice |
| `.choice .ot`, `.opt .ot`, `.rowtext` (option text) | body sans, 12.5–14.5px | **`var(--font-paper)`, 16/1.5** | §7.1 — "options" are Paper voice |
| `.rat`, `.exp .blk div` (rationales) | body sans | **`var(--font-paper)`, 16/1.5** | §7.1 — "rationales" are Paper voice |
| `.verdict`, `.pend`, `.refused`, `.assist-status`, tier headers | body sans / literal mono | **`var(--font-ledger)`** | §7.1 — runtime assertions |
| `.chip`, `.case-n`, `.cf h5`, `.exp h4`, `.session-details summary`, `.assist summary`, `.provenance` | literal `ui-monospace` | **`var(--font-ledger)`, 12px** | §7.1 |
| `.codewrap`, `.case pre`, `.run-source` | literal `ui-monospace` | **`var(--font-code)`** | §7.1 — the machine under study |
| Buttons, legends, labels, `Next item` | body sans | **`var(--font-chrome)`** | §7.1 |
| Generated support text | body sans | **`var(--font-chrome)` inside its labelled container** | §7.2.3 — a model gets no voice |

**And the mechanical precondition:** `quiz_page.TEMPLATE` must include `presentation.SHARED_CSS`
(which carries the four `@font-face` rules and the token `:root`) between `__THEME__` and its own
layer. Without that substitution every row above resolves to the fallback stack and the whole
repair is invisible — which is exactly how D-B happened.

Duplicate declarations that `SHARED_CSS` already provides (`*{box-sizing}`, the reduced-motion
block, `.mono`, focus-ring rules) are removed from the quiz layer rather than left to shadow it.

---

## 12. What must not change

- The item payload contract, the canonical response shapes, the scorer, the parser, the evidence
  schema. Phase 14 touches presentation only.
- Any copy string in `.planning/UI-SPEC.md` §7, `03.1-UI-SPEC.md` §15, `06-UI-SPEC.md` §7, or
  `06.2-UI-SPEC.md` §15, except the two retirements named explicitly (§9.3's shipped held sentence,
  §9.5's invented lock label) — both verified as *not* belonging to any locked table.
- `--leading-lesson`, the weight pair 400/600, `theme.py` as the single palette source, the
  `[!KEY]` card design, the callout kinds, the print contract, the `glossable()` silence rule.
- A bank with no `## TERMS` and no `## LESSON` renders **byte-identically** to today (§15 gate 7).

---

## 13. Accessibility gates that bind here — INHERITED, restated by number

All nine of `.planning/UI-SPEC.md` §8.1–8.9 bind unchanged. This phase does not invent a competing
set. The six that bite hardest, and where:

| Gate | Bites at |
|---|---|
| **§8.2** keyboard path, no trap | the gloss trigger → panel → `Full entry` → appendix → `Back to the text` round trip; the ladder's stumped control; the section nav; the `Session details` relocation in §6.3 |
| **§8.3** focus: 2px accent ring with offset, never removed; after submit focus stays on the submitted control; status announced without a focus jump | §9.3's every transition; §7.3's hover intent, which never moves focus |
| **§8.4** SRs never receive key, unshown tier text, or delayed verdicts via hidden labels, `alt`, CSS-off text, `title`, or live regions | §9.6's locked-card DOM rule; the `.term` trigger's forbidden `title`/`aria-label`; the `Help and evidence` summary previewing nothing |
| **§8.7** exactly one `role=status`; `role=alert` only for blocking errors; announce once | §13.1 — the numbered rule, plus the inventory of every shipped live region in the two in-scope files |
| **§8.8** WCAG AA contrast; semantic status carries text and structure | §3.3's measured tokens; §3.4's `--edge` at 3:1, which is the gate currently failing |
| **§8.9** degraded state keeps the authored loop usable and names what is unavailable; no disabled button without a reason | §9.5 in full |

Plus WCAG 2.2 §2.5.8: 44px minimum targets, with the documented inline exception for `[[term]]`
only, compensated by the appendix entry (INHERITED, 03.1 §3).

### 13.1 The one-live-region rule, stated numerically — LOCKED (new)

Gate §8.7 was being restated as a slogan ("exactly one `role=status`") in two places while §9.5
required a second polite region, and neither statement was checked against the code. Both are
resolved here, and the code is inventoried.

**Rule 1 — one *announcing* region per activity canvas.** Exactly one element carries
`role="status"` + `aria-live="polite"` on a rendered page: the reserved `.feedback` region inside
the active card. It announces verdicts, held state, duplicate/empty notices, and tier arrival. It
is the only element on the page whose content changes are spoken without the learner asking.

**Rule 2 — `role="alert"` is reserved for a change that blocks the learner's next action**, and is
used nowhere in this phase. Nothing in §9's state machine blocks; a held card is still operable.

**Rule 3 — a result the learner explicitly requested is not an announcement.** Text that appears
only as the direct outcome of a control the learner just pressed, inside the container they just
opened, is **static text with no live region**. The press is the event; announcing it again is a
double utterance. This is what makes §9.5 rule 2 and Rule 1 compatible rather than contradictory,
and it is the resolution of the blocking contradiction in the first draft of this document.

**Rule 4 — a persistent state *readout* is not a live region.** An element that displays current
state for reference (a manipulation's current value, a run's last output) is a visible readout
associated with its control by `aria-describedby`, at `aria-live="off"`. It is read on demand, not
pushed.

**Rule 5 — Rule 3 covers *synchronous* results only, and a deferred result announces.** Rule 3's
justification is that the learner's press is the event. That holds when the result is there on the
next frame; it does not hold when the result arrives seconds later while focus is still on the
button. A screen-reader learner who pressed `Get optional guidance` and was told nothing would never
learn the result landed. So: **a result that arrives asynchronously gets a live region that exists
only for the duration of the request the learner initiated.**

Sequence on `#assist-status`, and this is the whole of the exception:

1. On press: set `aria-live="polite"`, then write `Preparing optional guidance…`.
2. On arrival: write the result text (generated support, `unavailable`, `policy_drop`, `cancelled`)
   into the same region — one announcement, no focus movement.
3. After it has rendered: **remove `aria-live`.** The element reverts to static text, so re-opening
   the disclosure later re-announces nothing and §9.5 rule 2's "static text" framing stays true for
   every state except the few seconds the learner is waiting on their own request.

**Why not the alternative.** Moving focus to the result container on arrival was the other candidate
and is rejected: gate §8.3 is INHERITED and LOCKED — *"After submit, keep focus on submitted control
unless an error needs focus; status is announced without a focus jump."* An arriving hint is not an
error, so focusing it is a focus jump this contract may not authorise. A time-boxed live region
announces without moving anything.

**And §9.5's argument survives intact,** which is the test any exception here has to pass. The region
exists only inside a disclosure the learner opened, only after they pressed a button in it, and only
until their answer arrives. It never announces the model's absence to a learner who did not ask —
which was the whole objection. A learner who *did* ask is entitled to the answer to their own
question, including when the answer is that nothing is available.

**Inventory of every live region shipped in the two in-scope files, with its disposition.**
The spec previously audited none of these.

| File:line | Element | Today | Disposition |
|---|---|---|---|
| `quiz_page.py:2962` | `.feedback` boot placeholder (`Loading…`) | `role=status` + polite, static markup | **Survives** — it *is* the Rule 1 region, present before the first card renders. |
| `quiz_page.py:1136` / `:1187` (SERVED_JS) | `.feedback` per card | `role=status` + polite, created per card | **Survives, as exactly one at a time.** Only the active card exists in `#host`; the plan asserts that a page never holds two. This is the Rule 1 region. |
| `quiz_page.py:574` / `:614` (OFFLINE_JS) | `.feedback` per card | same | **Survives**, same rule. Only one client script runs per page, so 574/614 and 1136/1187 are never both live. |
| `quiz_page.py:338` | `#assist-status` inside the `Help and evidence` disclosure | `role=status` + polite, permanently | **Static text by default, live only while a request is in flight** — Rule 3 for the steady state, **Rule 5** for the deferred result. This is the site the blocking contradiction was about. Drop the permanent `role="status"`; add and remove `aria-live="polite"` around the request per Rule 5's three-step sequence. Every LOCKED string is unchanged. |
| `quiz_page.py:1597, 1798, 2006, 2238, 2453` | `.visual-status` in the five visual-item renderers | `role=status` + polite | **De-lived → `aria-live="off"` readout**, Rule 4, wired by `aria-describedby` from the manipulation control. **Cross-check owed at plan time:** `06.1-UI-SPEC.md` owns the visual-interaction contract; if it requires an announcing region there, 06.1 wins and this row becomes a recorded exception rather than a silent divergence. Default if 06.1 is silent: de-live. Note that a visual item today yields **three** concurrent polite regions (`.feedback` + `.visual-status` + `#assist-status`), which is the §8.7 failure in its clearest form. |
| `lesson.py:1641` | `.status` — the reader's degraded/style-warning notice | `role=status` (no `aria-live`) | **Survives** — the reader has no activity canvas of its own, so this is *its* Rule 1 region. Add `aria-live="polite"` for parity. Exactly one per reader page. |
| `lesson.py:1110` | `.run-status` per runnable code block | `role=status` + polite | **De-lived → `aria-live="off"` readout**, Rule 4. A lesson with four runnable blocks ships four polite regions today. **But it may not simply be de-lived — see the correction below**, or run failures become silent. |
| `lesson.py:1085`, `:1628` | *(docstrings only)* | — | Prose references, not emitted markup. Counted by a naive grep; listed so the count reconciles. |

**Correction found while writing this inventory, and it changes the `.run-status` disposition.**
`lesson.py:411` documents that *"Request errors are announced once with `role="alert"`"*. **The code
does not do this.** `RUNNABLE_JS`'s `setStatus(block, text, isError)` sets `textContent` and a
`run-error` class and nothing else; the string `alert` appears in that module only inside the
comment. So today a failed run is announced only because `.run-status` happens to be polite, and
de-living it under Rule 4 would make **every run failure silent** — a real regression hiding behind
a token cleanup.

**Binding disposition, therefore — and the sequence is the specification, not an implementation
detail.** A naive "set `aria-live="off"` idle, add `role="alert"` on error" is **self-silencing**:
an explicit `aria-live="off"` *overrides* the implicit live value that `role="alert"` would
otherwise carry, so an element left at `off` while the role is added announces nothing. It is the
live attribute that produces the announcement in practice; several screen readers do not react to a
role change alone. `setStatus(block, text, isError)` therefore performs, in this order:

```js
if (isError) {
  el.setAttribute("role", "alert");
  el.setAttribute("aria-live", "assertive");   // never "off"; removing the attribute is equivalent
} else {
  el.removeAttribute("role");
  el.setAttribute("aria-live", "off");
}
el.textContent = text;                          // written LAST, after the region is live
```

Three rules that make it portable: the live attributes are set **before** the text is written, never
after; `aria-live` is never left at `off` while `role="alert"` is present; and the success path
restores both, so a subsequent idle update does not re-announce. A failed run blocks the learner's
next action, which is exactly Rule 2's condition, so this is the role the comment always claimed and
the code never had. The docstring at `lesson.py:411` becomes true rather than aspirational.

`.run-status` also gains `var(--font-ledger)` at **16px** — it is a runtime assertion, and without an
explicit size it currently inherits the surrounding 18px Paper prose, which puts a runtime string in
the author's voice.

**Net:** one *polite* announcing region per rendered page in the steady state — `.feedback` on the
quiz, `.status` on the reader — down from up to three concurrent on a visual item and up to five on
a runnable lesson. Two are permitted transiently: `#assist-status` while a request the learner
initiated is in flight (Rule 5), and `role="alert"` on the two blocking-failure paths. Gate §15.3
asserts the steady-state count directly and asserts that both transient regions announce.

---

## 14. Copywriting contract

Rows marked INHERITED are reproduced verbatim and were neither edited nor re-voiced.

| Element | Copy | Voice | Status |
|---|---|---|---|
| Submit | `Check answer` (type-specific: `Run code`, `Check response`) | Chrome | INHERITED |
| Hint, unlocked | **`Open the next hint`** | Chrome | **DEFAULT (new)** — the only new string in this phase. Needed because 06's held sentence says "or open the next hint" and no control said that. |
| Hint, not unlocked | `I'm stumped — show the next hint` | Chrome | INHERITED (LOCKED) |
| Practice wrong | `Not correct. Try a different answer, or open the next hint.` | Ledger | INHERITED |
| Duplicate resubmission | `That is the same answer as before. Change it, or use "I'm stumped" to open the next hint.` | Ledger | INHERITED (LOCKED) |
| Empty submission | `Enter an answer before checking. An empty answer does not open a hint.` | Ledger | INHERITED (LOCKED) |
| Reveal shown | `The answer is shown above. Move on when you're ready.` | Ledger | INHERITED |
| Next locked tier | `Tier {n} unlocks after another attempt.` / `Or unlock it now with "I'm stumped".` | Ledger | INHERITED (LOCKED) |
| Further locked tier | `Tier {n} unlocks after tier {n-1}.` | Ledger | INHERITED (LOCKED) |
| Shown tier header | `TIER {n} · {LESSON\|OBJECTIVE\|TRAP\|RATIONALE FOR {letter}\|DISCRIMINATOR\|REVEAL}` | Ledger | INHERITED (LOCKED) |
| Unavailable tier | `This item has no authored {trap\|discriminator\|…}.` | Ledger + `--unknown` + label | INHERITED (LOCKED) |
| Ladder region label | `Hints` | Ledger | INHERITED (06 §6.3 wireframe) |
| Drill / diagnostic / exam ladder absence | the three sentences in §9.3 | Ledger | INHERITED (LOCKED) |
| Model unavailable | `Generated help is unavailable. You can keep learning with the lesson and authored hints.` | Ledger | INHERITED (LOCKED) |
| Policy-blocked | `Generated help is unavailable for this step. Continue with the available hint or try another attempt.` | Ledger | INHERITED (LOCKED) |
| Generated-help disclosure | `Help and evidence` / `Get optional guidance` | Chrome | INHERITED |
| Gloss full entry | `Full entry` | Chrome | INHERITED (LOCKED) |
| Gloss → key point | **`Also a key point`** | Ledger | **DEFAULT (new)** |
| Appendix back link | `Back to first use` | Chrome | INHERITED (LOCKED) |
| Appendix back link, arrived from a use | **`Back to the text`** | Chrome | **DEFAULT (new)** — script-only enhancement; the baseline string is unchanged |
| Section nav | `Sections in this lesson` | Ledger (summary) | INHERITED (LOCKED) |
| Gated reading, filtered nav | `More sections appear as you clear each check.` | Ledger | INHERITED |
| Key card, no runtime | `Review scheduling is unavailable without the runtime. Run itembank export anki to take this key to Anki.` | Ledger | INHERITED |
| **RETIRED** | `Not correct yet — the card stays open. Optional guidance is available under Help and evidence below.` | — | replaced by the INHERITED held sentence (§9.3) |
| **RETIRED** | `Optional guidance is locked` + the padlock glyph | — | never in any locked table; §9.5 rule 3 |
| Destructive action | *(none)* | — | Phase 14 introduces no destructive or irreversible learner action. Inventing a confirmation would make a hint request feel like a transgression. |

---

## 15. Required verification gates

Every one is a fixture, not a checklist item. Gates 1–6 are `.planning/UI-SPEC.md` §11's six,
applied; gates 7–12 are this phase's.

1. **Public-payload inspection.** No key, no unshown tier text, no expected output, no diagnostic or
   exam verdict in HTML, JSON, ARIA, CSS-off text, `title`, or accessible names before legal
   disclosure. Assert on a `HELD_FIRST` page that the strings for tiers 1–5 are absent from the
   served bytes.
2. **State fixtures.** Each named state in §9.3, plus reader empty / no-lesson / degraded-style /
   long-heading / long-table.
3. **Keyboard, SR, and the live-region count.** The §13 round trips, tested directly: focus order,
   labels, focus never jumping on submit or on tier arrival, and **one announcement per
   transition**. Assert the count structurally against §13.1's inventory: a rendered quiz page —
   including a visual item with the `Help and evidence` disclosure open and no request in flight —
   contains exactly **one** element matching `[role=status], [aria-live=polite]`, and a rendered
   lesson page with four runnable blocks contains exactly **one**. Two are permitted only while an
   optional-guidance request is in flight (§13.1 Rule 5), and the fixture asserts the second one is
   gone once the result has rendered.
   **The failure paths must be asserted to *announce*, not merely to be permitted.** For
   `.run-status` and `#assist-status`: at the moment of failure the element carries `role="alert"`
   **and** an `aria-live` that is absent or `assertive` — never `off` — and a source-order assertion
   on `setStatus` confirms the live attributes are written **before** `textContent`. An element left
   at `aria-live="off"` with `role="alert"` added is silent, so a fixture that checks only for the
   presence of the role passes while the learner hears nothing. This is the fixture that would have
   caught both the contradiction and the self-silencing sequence that the first two drafts of this
   document shipped.
4. **Responsive snapshots.** 1280 / 768 / 375 / 320 px for the reader and the quiz.
5. **Offline / degraded.** Network disabled: sit an item, get it wrong, open two tiers, reach the
   reveal, open a gloss, follow `Full entry` and come back. All must succeed. The word "offline"
   must not appear on screen.
6. **Evidence trace.** A shown tier writes exactly one hint event carrying its unlock path; a
   duplicate submission writes none; a gloss open writes at most the `term_lookup` 03.1 §8.5
   already defines.
7. **Byte-identity.** A bank with no `## TERMS` and no `## LESSON`, rendered before and after,
   differs only in the ways this contract names. Assert byte-identity of the *item* rendering path.
8. **Token completeness (D-A).** A fixture greps the fully rendered page for `var(--…)` references
   and asserts every referenced custom property is defined in the same document. This is the test
   that would have caught D-A, D-B and the `--panel` stray, and it must exist before any of them is
   fixed. Extend `tests/stylesheet_roundtrip.py`.
9. **Font reachability (D-B).** Every daemon-served page — reader **and quiz** — declares all four
   `@font-face` rules with root-absolute urls, and each url returns 200.
10. **Header clearance (criterion 1).** §6.4's assertion, at four widths, scripting on and off.
11. **Popover placement (D-C).** In a headless browser at 1280 and 375, the open panel's bounding
    box is within 24px of its trigger (or is the bottom sheet at coarse/narrow), and near the right
    edge and the bottom edge it stays fully inside the viewport.
12. **Type-scale conformance.** A fixture asserts that the rendered CSS of the four in-scope files
    contains no `font-size` outside {12, 16, 18, 20, 32}px, no `font-weight` outside {400, 600},
    and no literal font-family name.

---

## 16. Settings this phase registers — Directive §3

| Setting | Values | Default | Note |
|---|---|---|---|
| `reader_nav` | `none \| column \| rail \| auto` | **`auto`** | `rail` and `auto` are new (§8.1); `none`/`column` INHERITED |
| `gloss_hover` | `on \| off` | **`on`** | Under `(hover:hover) and (pointer:fine)` only. Off restores the pure click/focus path, which is complete on its own. |
| `hint_display` | `rail \| slot` | **`slot`** on the sat quiz at every width (§9.2) | INHERITED interface; this phase fixes its resolution for the single-column shell |
| `hint_locked_preview` | `full \| next` | **`full`** | INHERITED |
| `gloss_marks` | `all \| first-use \| none` | `all` | INHERITED |
| `print_gloss` | `appendix \| inline` | `appendix` | INHERITED |
| `example_layout` | `stacked \| parallel` | `stacked` | INHERITED |

---

## 17. OPEN — deliberately not settled here, each with a default so nothing blocks

1. **The two-column learning workspace.** `.planning/UI-SPEC.md` §3's desktop 2/3 + 1/3 shell does
   not exist; the quiz is one column. §9.2 rules for the shell that exists and names the
   forward path (`hint_display: rail` at ≥1024px once it does). **Default: do not build the second
   column in Phase 14.** Building it would put the ladder, the reader nav and the evidence drawer
   into one layout change and swamp a quality pass.
2. **`--measure-prose` for the non-vendored fallback.** 59ch is tuned to Source Serif's 1.118
   zero-to-average ratio. Georgia's ratio differs slightly, so a fallback render is a percent or two
   off. **Default: accept.** Correcting it needs a second measure token; the error is smaller than
   the rounding.
3. **Whether the `term_lookup` evidence field records hover-opens.** 03.1 §8.5 left the field OPEN.
   A hover-open is weaker intent than a click. **Default: record click-opens only**, and record
   nothing for hover, until there is a reason to distinguish them. Under-recording is reversible;
   a polluted append-only field is not.
4. **`aria-current` scroll-spy in `reader_nav: rail`.** **Default: `:target`-driven only, no
   scroll-spy.** Announced-not-merely-painted is INHERITED and holds either way.
5. **The 320px reading measure.** §4.6 records that the 45-character floor is not met and is not
   claimed. **Default: accept and state.** Revisit only with evidence that a 320px sitting happens.
6. **The rest of the type-scale migration** (`day.py`, `study.py`, `theme.py` settings CSS).
   **Default: out of scope here, owed as the Phase 4 cleanup the §7 weight ruling already
   recorded.** Named in §4.2 so the debt survives this phase.
7. **Whether `.visual-status` may keep an announcing region.** §13.1 de-lives the five visual-item
   readouts under Rule 4, but `06.1-UI-SPEC.md` owns the visual-interaction contract and this
   document may not overrule it. **Default: de-live to an `aria-describedby` readout.** If 06.1
   requires an announcing region, 06.1 wins, the row becomes a recorded exception, and the §15.3
   count fixture is written against two regions on visual items only — never against "some number".
   Resolve by reading 06.1 at plan time; do not resolve by guessing.

---

## Registry Safety

| Registry | Blocks used | Safety gate |
|---|---|---|
| None | None | Not applicable. No component registry, no npm, no CDN, no third-party UI blocks. |

The only third-party artifacts on these surfaces are the four OFL 1.1 font files and the vendored
KaTeX and CodeMirror 6 distributions, all already fetched, pinned, checksummed and licence-reviewed
under the KaTeX precedent (`fonts/MANIFEST.json`, `fonts/REGISTRY-SAFETY.md`, `09-03-PLAN.md`).
**This phase fetches no new byte.**

## Checker Sign-Off

- [ ] Copywriting contract checked
- [ ] Visual hierarchy and responsive behavior checked
- [ ] Color/semantic-token usage checked
- [ ] Typography and spacing token usage checked
- [ ] Accessibility/assessment-integrity gates checked
- [ ] Registry safety checked

**Approval:** pending Phase 14 UI verification
