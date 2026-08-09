---
date: 2026-08-09
topic: Visual design of learning / reading / docs products; one coherent visual direction for itembank
researched_by: Claude (gsd-phase-researcher, standalone pass per RESEARCH-BRIEF §4)
binding_inputs:
  - .planning/RESEARCH-BRIEF-learning-platform-2026-08-09.md §1-3
  - .planning/UI-SPEC.md §7 (Phase 4 token system — extend, never replace)
  - surfaces/theme.py (shipped token source)
confidence:
  product_findings: MEDIUM-HIGH (mix of CITED primary sources and ASSUMED training knowledge, tagged per claim)
  typography_numbers: HIGH where CITED (Butterick, Tufte, gwern, Linear, Stripe), MEDIUM elsewhere
  proposed_direction: HIGH (internally consistent with locked Phase 4 tokens and UI-SPEC gates)
  font_licensing: HIGH (OFL confirmed for all recommended vendored faces)
  cost_estimates: MEDIUM (based on current presentation.py/theme.py architecture)
provenance_legend: >
  [CITED: url] = read from that source this session. [VERIFIED: path:lines] = read
  in this repo this session. [ASSUMED] = training knowledge, not verified this
  session; planner must confirm before it becomes a locked decision.
---

# Visual Design Research — Learning, Reading, and Docs Products (2026-08-09)

## 0. Summary and Primary Recommendation

Every product studied splits into two camps. **Reading-first products** (Tufte CSS, gwern.net,
LessWrong/GreaterWrong, Quanta, iA Writer, Readwise Reader) put a serif or near-serif on a
paper-tinted field, cap the measure at 55–75ch, and let typography do nearly all the work —
they are instantly recognizable and age well. **Dense-UI products** (Linear, Stripe, Notion,
Anki, most edtech) run one sans at many sizes on a neutral field; the good ones (Linear, Stripe)
are recognizable only because of one extreme, disciplined choice (Linear: near-black canvas +
weight 510; Stripe: one variable font + tightening letterspacing). The templated-looking ones
(Docusaurus defaults, most 2025 edtech) share: system-or-Inter sans everywhere, one brand hue
used for both navigation and success, 5px-left-border callouts, and card grids — exactly the
"default admin template" failure the brief names.

**Primary recommendation:** adopt the direction **"Paper & Ledger"** (§8): authored content
(lesson prose, item stems, rationales) moves to a vendored serif on the existing paper-tinted
field; everything the **runtime asserts** — verdicts, evidence counts, hint-tier state,
provenance, gate status — renders in a vendored duospace "ledger" voice; UI chrome stays on the
current system-ui stack unchanged. The distinctive move: **typography encodes authority**. One
glance tells you who is speaking — the author, the runtime, or a model — which makes the
product's core guarantee (the runtime, not the model, decides what reaches the learner) visible
on every screen. No competitor does this; it costs two OFL font files and CSS.

---

## 1. Long-Form Reading Exemplars

### Tufte CSS
- **Type:** ET Book (open-source Bembo relative), fallback Palatino/Georgia [CITED: edwardtufte.github.io/tufte-css]. Training-data specifics: `html{font-size:15px}`, body copy `1.4rem/2rem`, body `width:87.5%`, paragraphs constrained to `~55%` width (≈ 50–60ch), sidenotes `1.1rem` at `width:20%` floated into the right margin [ASSUMED — numbers from tufte.css source in training data; the fetched page confirms fonts/colors but not numbers].
- **Color:** off-white `#fffff8` on off-black `#111` — deliberately not pure white/black [CITED: edwardtufte.github.io/tufte-css]. Zero semantic colors; links are underlined body-color text. Meaning is carried entirely by position (margin) and style (italic epigraphs).
- **Layout:** single column at ~60% width with a ~36% sidenote margin [CITED: css4.pub/2023/tufte]. No nav, no TOC — documents are meant to be read top to bottom.
- **Blocks:** epigraph = italic blockquote + footer attribution; figures default to main-column width with a `fullwidth` escape hatch; code = Consolas-first mono stack [CITED: edwardtufte.github.io/tufte-css].
- **Motion:** none. CSS-only by policy; JS is declared out of scope [CITED: edwardtufte.github.io/tufte-css].
- **Identity in one screenshot:** the cream field + serif + populated right margin. Nothing else looks like it.
- **Take for itembank:** the *margin as a place where secondary voices live* (provenance, source citations) and the off-white/off-black restraint Phase 4 already ships (`#f3f5f4`/`#171d1c` is the same instinct) [VERIFIED: surfaces/theme.py:36-39, values quoted: light `{"bg": "#f3f5f4", "ink": "#171d1c", ...}`].

### gwern.net
- **Type:** body Adobe Source Serif Pro, headers Source Sans Pro, code IBM Plex Mono (picked after comparing ~20 code faces); fonts subset per-site [CITED: gwern.net/design].
- **Color:** deliberately **grayscale-only** "as an experiment in consistency"; the discipline itself is the identity [CITED: gwern.net/design]. Dark mode is a 3-state switch (dark/light/auto) with per-image inversion decisions [CITED: gwern.net/design].
- **Layout/nav:** "semantic zoom" — title → abstract → section headers → margin notes → body → collapsed sections → link-preview popups. Long documents are navigated by progressive disclosure, not pagination [CITED: gwern.net/design].
- **Blocks:** sidenotes via `sidenotes.js` degrade to footnotes on narrow screens; hundreds of link icons classify destination by type; collapsible sections; core pages work without JS [CITED: gwern.net/design].
- **Motion:** essentially none; budget goes to popups and transclusion, not animation.
- **Take:** progressive disclosure is exactly our `<details>` evidence-drawer pattern (UI-SPEC §4 EvidenceDrawer); grayscale-plus-nothing proves a near-monochrome learning surface can carry identity. Also the strongest precedent for **vendoring subset fonts as a deliberate act**.

### LessWrong / GreaterWrong
- GreaterWrong's "Less" theme (modeled on LessWrong) sets body text in **Source Serif Pro** [CITED: lesswrong.com/posts/xjgdtswhcxJTqu95Q]. LessWrong itself: serif post bodies on a warm neutral field, sans UI chrome, green accent used sparingly for links/karma [ASSUMED]. Long posts navigated by a floating TOC with scroll-spy [ASSUMED].
- **Take:** serif-for-content / sans-for-chrome split within one page is proven at scale for demanding readers. This is the same split "Paper & Ledger" proposes.

### Quanta Magazine
- **Type:** Noe Display for headlines, Merriweather for body/bylines/subheads, Pangram Sans for nav [CITED: fontsinuse.com/uses/36718]. A three-voice system: display serif (drama), text serif (reading), sans (chrome) — the same "voice per role" pattern, used editorially.
- **Take:** confirms voice-per-role is a recognized, learnable convention, not a novelty risk.

### Practical Typography (Butterick) — the numbers the direction must satisfy
- Body on screen **15–25px**; line spacing **120–145%** of point size; line length **45–90 characters**; bold/italic as little as possible and never together; all-caps only under one line and letterspaced +5–12% [CITED: practicaltypography.com/summary-of-key-rules.html].
- Phase 4's `text-body 16px/1.5` sits inside every one of these ranges [VERIFIED: .planning/UI-SPEC.md §7 table, quoted: "`text-body` | 16px / 1.5 | prose, response, explanatory copy"]. The proposed `text-lesson 18px/1.65` (§9) also does.

---

## 2. Docs Platforms (Stripe, MDN, Docusaurus, VitePress)

### Stripe docs
- **Type:** one variable font, `sohne-var`, across the whole interface; effectively two weights (300 body/headings, 400 UI); letterspacing tightens with size: −1.4px @56, −0.96 @48, −0.64 @32, −0.26 @26, normal ≤16px; heading sizes drop one step on mobile [CITED: designmd.cc/benchmarks/stripe via search digest].
- **Layout:** strict 4/8pt grid; generous body line-height against tight display tracking [CITED: designmd.run/blog/stripe-design-system-breakdown via search digest]. Three-pane docs: left nav tree, center prose ~70ch, right code column that scroll-syncs to the prose [ASSUMED].
- **Identity:** the synced code rail + the single-font discipline. Recognizable because the code column is a *layout organ*, not a block.
- **Take:** "one variable font, two weights" validates Phase 4's two-weight rule; the scroll-synced secondary column is the expensive version of what our contextual-support column already is (UI-SPEC §3) — do not add scroll-sync, it costs JS and helps marketing pages more than lessons.

### MDN
- 2022+ design: Inter-ish sans body ~16px, left sidebar tree + right "In this article" scroll-spy TOC, note/warning "notecards" with a 4px left border and tinted background [ASSUMED — search returned no primary source this session].
- **Take:** the right-hand scroll-spy TOC is the standard long-lesson navigation answer in docs land. For itembank lessons, a static `<nav>` TOC from headings (no scroll-spy JS) gets 90% of the value at ~0 cost and works with JS off.

### Docusaurus (Infima) and VitePress — what "templated" looks like
- Docusaurus: system font stack, 16px body, primary green `#2e8555`, admonitions = **5px left border + same-hue tinted background + icon + bold uppercase title** [ASSUMED]. VitePress: Inter, indigo brand, "custom containers" = tinted rounded boxes, code always on a dark block in both modes [ASSUMED].
- **Shared templated tells:** (a) brand hue does triple duty (nav, links, success), (b) every callout is the same box with a different hue, (c) Inter/system + card grid + left-border callout. Avoiding exactly these three is the cheapest possible distinctiveness.
- **Take:** our callout grammar (§10) deliberately breaks (b): callout *types* are distinguished by icon + label + structure, with color as a secondary channel only — which UI-SPEC's "never color alone" rule already forces [VERIFIED: .planning/UI-SPEC.md §7, quoted: "semantic … paired with text/icon/structure; never color alone"].

---

## 3. Dense-UI Product Exemplars (Linear, Notion, Obsidian, Bear, Typora, iA Writer)

### Linear
- **Type:** Inter Variable with `cv01`/`ss03` enabled; weights 300→510→590, where **510** (only reachable on the variable axis) is the signature UI weight [CITED: designmd.cc/benchmarks/linear via search digest].
- **Color:** dark-first: canvas `#08090a`, text `#f7f8f8`, borders `rgba(255,255,255,0.05)` — hierarchy built almost entirely from luminance steps [CITED: same].
- **Motion:** micro-transitions ~100–150ms, opacity/transform only [ASSUMED].
- **Identity:** the near-black canvas + one custom weight. One decision, executed everywhere.
- **Take:** identity comes from a *single extreme discipline*, not from more colors or more components. Also a warning: Linear's look is now the most-copied template in dev tools; copying it is the new default-admin-template.

### Notion / Obsidian / Bear / Typora / iA Writer
- Notion: system sans, gray-on-white chrome, callout = light gray bg + emoji icon + small radius; offers exactly three content voices (Default sans / Serif / Mono) the user can switch per page [ASSUMED].
- Obsidian: Inter-ish UI, purple accent, dark default, everything themeable — identity outsourced to the community [ASSUMED].
- Bear: Avenir-style humanist sans + one red accent `#dd4c4f`-ish; recognizable from the accent alone [ASSUMED].
- iA Writer: one mono/duospace face, ~18px, generous measure, almost no chrome; the *font is the brand*. Quattro gives every character one of four widths — proportional comfort with typewriter honesty [CITED: ia.net/topics/in-search-of-the-perfect-writing-font; fontsinuse.com/typefaces/118331]. Fonts are **SIL OFL 1.1**, free to vendor [CITED: github.com/iaolo/iA-Fonts LICENSE.md].
- **Take:** Notion's per-page three-voice switch proves users understand "serif = reading, mono = literal record" without training. iA proves a duospace face can carry an entire product's identity and remain readable at body sizes — the strongest evidence for the "ledger voice" half of our direction.

---

## 4. Learning Platforms (Execute Program, Brilliant, Boot.dev, Runestone, Khanmigo)

### Execute Program
- Structure: short prose → inline runnable code check → SRS resurfaces the same concept on a schedule; reviews are all auto-checkable code; common mistakes (syntax errors) are detected and not penalized [CITED: mike.place/2020/executeprogram]. Visuals: minimal white page, sans UI, mono code boxes inline in prose, per-course progress counts; the *code box in the prose stream* is the identity [ASSUMED].
- SRS UX lesson: users missed easy/hard grading and disliked the hard "day 64, never again" cutoff [CITED: mike.place/2020/executeprogram] — pace honestly, expose the schedule (Phase 10).

### Brilliant
- One concept per lesson, mix of direct instruction and blocked problem solving; wrong answers open *interactive* explanations; instant custom feedback per distractor [CITED: screensdesign.com/showcase/brilliant-learn-by-doing]. Motion via Rive: tangram-styled loading, branching-path progress maps, in-lesson celebration + encouragement moments [CITED: rive.app/blog/how-brilliant-org-motivates-learners-with-rive-animations; ustwo.com/work/brilliant].
- **Take:** one-idea-per-screen sequencing (Phase 7) and per-distractor feedback (we already author `DA:` per option). **Reject** celebration motion — UI-SPEC LOCKED forbids celebratory motion and engagement pressure. Brilliant spends its motion budget on exactly what our contract bans.

### Boot.dev
- Identity: dark-fantasy RPG framing, pixel-art characters, XP/levels/gems; gamification as the core retention mechanic against boredom [CITED: alternativeto.net/software/boot-dev + ASSUMED detail].
- **Take:** proof that a *strong theme* differentiates — and a list of exactly the mechanics our spec forbids. The lesson is the strength of commitment, not the content of it.

### Runestone Academy
- Open-source executable textbooks; default Bootstrap-era look; identity ~zero; value is all in the runnable/graded blocks [ASSUMED].
- **Take:** what itembank looks like if we ship function without a visual direction — the counterexample.

### Khanmigo / Synthesis
- Khanmigo's refusal UX is "naked Socratic dialogue" in a chat panel; the top complaint is that kids who want help get questions; Synthesis succeeds by wrapping the same structure in an activity loop [CITED: agentconn.com/blog + neuralclass.uk via search digest].
- **Take:** validates our architecture — the refusal should be *structural and visible*, not conversational. The HintLadder with visible locked tiers (UI-SPEC §4) is the anti-Khanmigo: the learner sees there IS a ladder, sees which rung they are on, and the copy ("I'm stumped — show the next hint") makes the next step legal and shame-free. Render the *gate itself* (see §10, "tier rail") instead of a chat window apologizing.

---

## 5. SR-Native and Reader Apps (Anki, Mochi, RemNote, Readwise Reader, LingQ)

- **Anki:** dense Qt UI, no design language; meaning carried by four colored grade buttons; identity = hostility [ASSUMED]. Take FSRS, not the face.
- **Mochi:** "Anki redesigned in 2020" — markdown cards, LaTeX, no gamification, no visual noise; SM-2 default with optional FSRS since June 2025 [CITED: study-genius-ai.hatolabs.com + skilllearningcompass.com via search digest]. Closest existing product to our aesthetic register: quiet, markdown-native, one accent.
- **RemNote:** notes and cards are one object; visually a dense outliner — powerful, cluttered [ASSUMED].
- **Readwise Reader:** every format (article/PDF/email/video transcript) normalizes into ONE reading view with one typography; user controls font/size/spacing/theme; dark mode genuinely dark; highlights use warm "physical highlighter" colors (soft yellow/coral/blue) [CITED: blakecrosley.com/guides/design/readwise-reader + docs.readwise.io].
- **LingQ:** word-knowledge state encoded as background highlight on the word itself (blue = new, yellow fading through 4 learning levels, none = known) — the canonical "reading surface carries learner state" pattern [ASSUMED].
- **Take:** Reader's "one reading view for every format" is our subject-invariant rule (LOOP: same loop, varied media) expressed visually. LingQ's per-word state is the model for D1 `[[term]]` glosses: a `<dfn>` with a dotted underline (state channel = underline style + hover card, never color alone).

---

## 6. 2025–2026 Trend Check (what to ignore)

Current edtech trend lists push: dopamine color, neon gradients, gamification (72% motivation claims), AI-personalization everywhere, oversized display type [CITED: lollypop.design 2025; zeenesia.com 2026; figma.com/resource-library/web-design-trends]. Two durable signals inside the noise: **dark mode is now expected by default** (>68% preference claimed) and **WCAG-compliant palettes correlate with completion** [CITED: litslink.com via search digest — treat the percentages as marketing-grade, LOW confidence].
**Verdict:** itembank should be deliberately counter-trend (calm, paper, evidence) — the trend material describes exactly the punitive/gamified framing our spec forbids. The two durable signals are already shipped (dark derivation, WCAG gate in theme.py).

---

## 7. Empty States, First-Run, Loading, Error — cross-product patterns

- **Linear:** keyboard-first onboarding; empty views teach one shortcut [ASSUMED]. **Notion:** templates as empty state [ASSUMED]. **Brilliant:** diagnostic quiz as first-run [CITED: screensdesign.com]. **Readwise:** import-first onboarding — the product is empty until your stuff arrives, so import IS onboarding [CITED: docs.readwise.io].
- **Pattern worth stealing (addresses brief B5):** the empty state names the *one command that fills it*. For itembank: an empty Day page shows the exact CLI line (`itembank start banks/... --mode practice`) and a "serve a sample bank" action against a synthetic fixture bank shipped in-repo. Every surface already has a CLI twin (CLAUDE.md), so empty states can be *literal, copyable commands* rendered in the ledger voice — an empty state no web-only competitor can imitate. CONVENTION, cost S per surface, Phase 4-follow-on/each phase's surface work.
- **Loading:** reading-first products avoid skeletons (content arrives fast or the page is static); Brilliant themes its loaders as brand moments [CITED: rive.app blog]. Ours: text status lines in the ledger voice ("deriving… n items"), no skeleton screens, no spinners longer than 150ms without words — matches UI-SPEC StatusNotice.
- **Error:** best-in-class (Stripe) errors state cause + next action in one sentence. Our copywriting contract already does this; keep errors in the ledger voice so a runtime refusal *looks like* a runtime statement, not a decorated apology.

---

## 8. THE PROPOSED DIRECTION — "Paper & Ledger"

One direction unifying quiz, study, lesson, day, report, settings, **built strictly on Phase 4 tokens** (60/30/10 split, derived accent, fixed semantic tokens, space-1..7, two weights, 150ms motion — all unchanged).

### The distinctive move
**Typography encodes authority.** Every string on screen renders in the voice of its source:

| Voice | Who is speaking | Face | Where |
|---|---|---|---|
| **Paper** | The author (human or approved AI) | vendored serif (Source Serif 4) | lesson prose, item stems, options, rationales, epigraphs, `[!KEY]` blocks |
| **Ledger** | The runtime — things the system *guarantees* | vendored duospace (iA Writer Quattro) | verdicts, scores, hint-tier state, evidence counts, provenance/`[SRC:]` lines, session IDs, empty-state commands, StatusNotice copy |
| **Chrome** | The tool | existing system-ui stack, unchanged | nav, buttons, labels, settings forms |
| **Code** | The machine being studied | existing ui-monospace stack | code blocks, learner code, canonical responses |

A model's generated text renders in Chrome voice inside the already-specified "Generated synthesis" labeled surface — deliberately given **no voice of its own**: it is a guest, and the label + container say so. This makes D4 ("the runtime gates the tutor") *visible on every screen*, which the brief explicitly says the UX must do. No product in the study set distinguishes system-guaranteed text from generated text typographically. That is the move that keeps six surfaces from reading as an admin template: a report page where the numbers are in the ledger voice reads as *sworn record*; a lesson in serif on the paper field reads as *authored teaching*; the seam between them is the product's thesis.

### Why these two faces
- **Source Serif 4** (SIL OFL 1.1): proven for exactly this job by gwern.net and GreaterWrong [CITED: gwern.net/design; lesswrong.com GreaterWrong post]; variable weight+optical-size axes; excellent at 16–19px; pairs naturally with system sans chrome. [ASSUMED: latin-subset variable woff2 ≈ 100–160KB + italic ≈ same.]
- **iA Writer Quattro** (SIL OFL 1.1, confirmed) [CITED: github.com/iaolo/iA-Fonts/blob/master/iA Writer Quattro/LICENSE.md]: duospace — reads as "typewritten record" without code-editor connotation, distinct at a glance from both the serif and true code mono; carries an entire product's identity at iA. [ASSUMED: variable woff2 ≈ 60–90KB.]
- **Accessibility option (B13):** vendor **Atkinson Hyperlegible Next** (SIL OFL, released 2025, variable + mono companion) [CITED: en.wikipedia.org/wiki/Atkinson_Hyperlegible] as an opt-in "high-legibility reading" setting that swaps the Paper voice only. Settings toggle, same pattern as the accent picker.

### What does NOT change
Palette, accent derivation, semantic tokens, spacing scale, weights (two, per face), motion budget, 44px targets, breakpoints, WCAG gates, the `theme.py` single-source rule. Dark mode needs no second palette: both faces render on the existing dark tokens; fonts are palette-independent.

---

## 9. Concrete Token Additions (extends Phase 4; nothing removed or renamed)

Add to the generated style block (owner: `surfaces/presentation.py` SHARED_CSS + `theme.py` remains color-only):

```css
/* Voice tokens — RENDERER, Phase 03.1 */
--font-paper:  "Source Serif 4", Georgia, "Times New Roman", serif;
--font-ledger: "iA Writer Quattro", ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
--font-chrome: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;   /* names the existing stack */
--font-code:   ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace; /* names the existing stack */

/* Reading scale extension — one new size with recorded reason:
   16px system-ui is right for UI copy; sustained serif prose reads best 17–19px
   (Butterick 15–25px window [CITED]); lesson bodies get one dedicated size. */
--text-lesson: 18px;  --leading-lesson: 1.65;

/* Measure tokens (UI-SPEC already caps prose at 72ch) */
--measure-prose: 66ch;   /* default lesson column; ≤ the locked 72ch max */
--measure-wide: 90ch;    /* tables, code results */

/* Radius tokens — tokenize the literals already shipped in theme.py SETTINGS_CSS (6/8/12) */
--r-1: 6px;  --r-2: 8px;  --r-3: 12px;
```

**Semantic token completion — RENDERER + theme.py, Phase 03.1 (S):** UI-SPEC §7 names
`--ok/--bad/--warn/--unknown/--pending`; `theme.py` ships `ok, ok_bg, bad, bad_bg, warn`
[VERIFIED: surfaces/theme.py:42-47, quoted: `{"ok": "#1b7a3d", "ok_bg": "#e8f4ec", "bad": "#b4272b", "bad_bg": "#fbebeb", "warn": "#8a5900"}` /
dark `{"ok": "#4fbf74", "ok_bg": "#11291b", "bad": "#f0666a", "bad_bg": "#2b1416", "warn": "#e0a23a"}`].
Missing: `unknown`, `pending`, `warn_bg`. Proposed values (must pass the same fixed-per-mode,
never-derived-from-accent rule and a contrast check before landing — treat hexes as drafts):

| token | light | dark | note |
|---|---|---|---|
| `warn_bg` | `#f8f1e2` | `#2b2312` | completes the ok/bad pattern |
| `unknown` / `unknown_bg` | `#566067` / `#edf0f2` | `#9aa7ad` / `#1b2325` | deliberately close to `mut` but distinct: unknown is a *stated* state, "not enough evidence," never rendered as decoration |
| `pending` / `pending_bg` | `#5b4a9f` / `#efecf7` | `#b3a3e6` / `#221c33` | "a review is pending — work, not mastery yet" |

## 10. Block Styling Specs (03.1 grammar; all values from existing tokens)

- **Lesson prose container:** `font:var(--text-lesson)/var(--leading-lesson) var(--font-paper); max-width:var(--measure-prose); color:var(--ink)`. Headings stay `text-heading 20px` but in `--font-paper` 700 inside lessons. Long-lesson nav: a static `<nav>` TOC built from headings at the top (details-collapsed on narrow), no scroll-spy JS. One idea per `##` section; the lesson scrolls — pagination is rejected (evidence: docs products all scroll; Brilliant paginates only because each screen is an interaction).
- **Callout grammar** (`[!NOTE]`, `[!KEY]`, `[!WARNING]`, `[!EXAMPLE]`, `[!SRC]`): NOT the Docusaurus tinted-box-per-hue. Structure: `border:1px solid var(--line); border-radius:var(--r-3); background:var(--card); padding:var(--space-3) var(--space-4)`; header row = inline SVG icon (16px, `stroke:currentColor`) + small-caps label in `--font-ledger` `text-xs` letterspaced +6% (Butterick range) + type name as text. Color appears only as the label's foreground for WARNING (`--warn`) — type is always readable from icon + label alone.
- **`[!KEY]` memorizable (D2):** the one callout allowed extra weight — an "index card": same structure plus `border-width:1px; box-shadow:0 1px 0 var(--line)` (a physical-card hint, no drop-shadow blur), label `REMEMBER`, and a footer line in ledger voice showing its export identity (`key: airway-opa-01 · exports to Anki`). One authoring act, three surfaces, and the card *looks like* the flashcard it becomes.
- **Definitions (D1):** `dfn[data-term]{ text-decoration: underline dotted 1px; text-decoration-color: var(--mut); text-underline-offset: 3px; cursor: help }` — LingQ's state-on-the-word pattern, but underline-style not background-color. Hover/focus opens a 320px card (`--r-2`, `--card`, `1px var(--line)`) with the gloss in Paper voice and "tested by: Q12, Q31" in Ledger voice. No JS = plain visible `<dfn>` + the gloss available in the TERMS section; degrades exactly as the brief requires.
- **Hint-tier rail (D4 made visible):** replace nothing; style the HintLadder as a vertical rail of tier cards. Shown tiers: `--card` + ledger-voice header `TIER 2 · authored`. Locked tiers: `background:var(--chip); border:1px dashed var(--line)` with the literal text `Locked by session mode` in ledger voice — no hidden DOM text for locked content (already LOCKED in UI-SPEC). The dashed border + ledger label is the visual signature of "the runtime holds the key," unique to us.
- **Verdicts:** existing `state-ok/state-bad` chips [VERIFIED: surfaces/theme.py:338-343 — quoted: `.sample.state-ok{color:var(--ok);background:var(--ok-bg);border-color:var(--ok)}`] but the verdict word (`Correct`, `Incorrect — held`, `Correct after tier 2`) renders in `--font-ledger`. "Correct after tier N" in ledger voice IS the report's honesty made typographic.
- **Code blocks:** unchanged stack, `background:var(--chip); border:1px solid var(--line); border-radius:var(--r-2); padding:var(--space-3)`; same in both modes (no VitePress dark-block-in-light-mode — it fights the paper field).
- **Math (Phase 9 KaTeX):** rendered math inherits Paper voice context; the raw-LaTeX fallback disclosure renders in Code voice.
- **Figures:** main-column width, caption `text-xs` in Chrome voice `color:var(--mut)`, Tufte-style `fullwidth` escape only in reports.
- **Motion:** unchanged budget. The only earned animation: feedback-panel entry, 120ms opacity + 4px translateY, once. Tier reveal is instant (a gate opening should feel mechanical, not theatrical). `prefers-reduced-motion` strips both — already shipped.

## 11. Migration Note (from the current system-ui stack)

1. **Additive, degrade-to-today:** `@font-face` for the three vendored families (Source Serif 4 roman+italic, Quattro variable, Atkinson opt-in) served by the daemon at `/assets/fonts/*.woff2` with `font-display: swap`. Fallback chains are the *current* stacks, so no-asset/offline/static contexts render exactly today's look. Precedent: the vendored-KaTeX exception (goal forbids services/network, not files) and Phase 9's 09-03 provenance/license/checksum review pattern — run the same review for fonts (OFL texts vendored beside the files).
2. **Static offline quiz build:** do NOT embed fonts (base64 would triple the HTML). `build` copies woff2 beside the output HTML when present; otherwise the fallback stack applies. Offline sitting never blocks on a font.
3. **Ownership stays split:** `theme.py` = color only (unchanged single palette owner); `presentation.py` SHARED_CSS = voice/measure/radius tokens + `@font-face`. No surface names a font family directly — only `var(--font-*)`.
4. **Order of adoption:** lesson surface first (03.1), then verdict/report strings (ledger voice is a per-selector CSS change), then day/settings inherit via SHARED_CSS. Quiz/study item stems move to Paper voice last, behind a fixture check that measure/leading changes don't break the 375px snapshot gate.
5. **Packaging (Phase 12):** fonts ship inside the app bundle; the updater treats them as static assets with checksums.

## 12. Consolidated Finding Table

| # | Finding → action | Tag | Cost | Phase |
|---|---|---|---|---|
| F1 | Two-voice typography (Paper/Ledger) as the distinctive move | RENDERER | M (CSS + @font-face + selector audit) | **03.1** |
| F2 | Vendor Source Serif 4 + iA Writer Quattro (OFL, license review + checksum) | PACKAGING/RENDERER | S–M | **03.1** (review), 12 (bundle) |
| F3 | `text-lesson 18/1.65`, `measure-prose 66ch`, radius tokens | RENDERER | S | **03.1** |
| F4 | Complete semantic tokens: `unknown/pending/warn_bg` in theme.py | RENDERER | S | **03.1** (needed by 7/10 surfaces) |
| F5 | Callout grammar incl. `[!KEY]` index-card + ledger export footer | FORMAT + RENDERER | M (parser additive + lint + CSS) | **03.1** |
| F6 | `<dfn>` dotted-underline gloss, hover card, no-JS fallback (LingQ pattern) | FORMAT + RENDERER | M | **03.1** |
| F7 | Static heading TOC for long lessons (no scroll-spy) | RENDERER | S | **03.1** |
| F8 | Hint-tier rail with visible dashed "locked" tiers (anti-Khanmigo) | RENDERER | S–M | 6 |
| F9 | Verdict strings in ledger voice; "correct after tier N" styling | RENDERER | S | 6 / 10 |
| F10 | Empty states = copyable CLI command in ledger voice + sample-bank action | CONVENTION | S per surface | each surface's phase; spec in **03.1** |
| F11 | Atkinson Hyperlegible Next opt-in reading face (B13) | RENDERER | S (settings toggle, picker pattern exists) | 03.1 or 10 |
| F12 | Reject: celebration motion, gamified progress, dopamine palettes, scroll-synced code rail, skeleton loaders | CONVENTION | 0 (a decision) | all |
| F13 | Pace honestly: expose schedule; no "never again" cliff (Execute Program lesson) | RUNTIME/CONVENTION | copy + scheduler param | 10 |
| F14 | One reading view across media (Readwise pattern = LOOP rule, visually) | CONVENTION | 0 (already implied) | 9 |
| F15 | Generated model text has no voice of its own — Chrome face inside labeled container | RENDERER | S | 8 |

## 13. Assumptions Log (confirm before locking)

| # | Claim | Risk if wrong |
|---|---|---|
| A1 | Tufte CSS numeric values (15px root, 55% para width, sidenote 20%) from training data | Low — used as reference, not adopted |
| A2 | Docusaurus/VitePress/MDN/Notion/Obsidian/Bear/LingQ/Execute Program visual specifics | Low — pattern-level only |
| A3 | Font file sizes (SS4 ~100–160KB/wt subset; Quattro ~60–90KB) | Medium — check before Phase 12 budget; measure actual woff2 at vendoring time |
| A4 | Draft hex values for `unknown/pending/warn_bg` pass WCAG on all Phase 4 surfaces | Medium — run theme.py's own `contrast_ratio` in the fixture before landing |
| A5 | Trend statistics (68% dark-mode preference, completion-rate claims) are marketing-grade | None — direction doesn't depend on them |
| A6 | Source Serif 4 renders well at 18px on Windows ClearType (gwern uses Source Serif Pro, its predecessor) | Low–Medium — verify in the 375px/1280px snapshot fixtures |

## Sources (primary, read this session)
edwardtufte.github.io/tufte-css · gwern.net/design · practicaltypography.com/summary-of-key-rules.html · github.com/iaolo/iA-Fonts (LICENSE.md) · en.wikipedia.org/wiki/Atkinson_Hyperlegible · fontsinuse.com/uses/36718 (Quanta) · designmd.cc/benchmarks/linear + /stripe (via search digests) · rive.app/blog (Brilliant) · ustwo.com/work/brilliant · screensdesign.com/showcase/brilliant-learn-by-doing · mike.place/2020/executeprogram · docs.readwise.io + blakecrosley.com (Reader) · lesswrong.com GreaterWrong theme post · agentconn.com + neuralclass.uk (Khanmigo) · lollypop.design / zeenesia.com / figma.com resource library (trends).
