---
date: 2026-08-10
topic: "Cross-phase UI inspiration and pattern research for the five surfaces with no per-phase UI-SPEC (3.1, 6, 6.2, 7, 13) plus the cross-cutting `## SCENARIO` staged reveal"
status: INPUT ARTIFACT — not a spec
binding_inputs:
  - .planning/PLANNING-DIRECTIVES.md (all six sections)
  - .planning/UI-SPEC.md (accessibility gates §8 and copywriting contract §7 are LOCKED and bind everything here)
  - .planning/RESEARCH-BRIEF-2-lesson-styles-2026-08-10.md §4 (round-two verdicts)
  - .planning/research/2026-08-09-lesson-display-editor.md, -visual-design.md, -differentiators-d1-d2-d3.md, -landscape-widening.md (round one — extended, not repeated)
  - .planning/ROADMAP.md Phases 3.1, 6, 6.2, 7, 13
provenance_legend: >
  [CITED: url] = read or search-verified this session (2026-08-10).
  [VERIFIED: path] = read in this repo this session.
  [ASSUMED] = training knowledge, not verified this session.
  [UNVERIFIED] = attempted and could not confirm; named in §8.
---

# UI Inspiration and Patterns — the Five Surfaces with No UI-SPEC

## 0. What this document is, and is not

**This is INPUT to five future per-phase UI-SPECs. It is not itself a spec.**

Five phases have a learner-facing surface, no per-phase UI-SPEC, and a `/gsd-discuss-phase`
step still ahead of them: **3.1** (reading surface), **6** (hint ladder and feedback modes),
**6.2** (executable textbook loop), **7** (selection engine), **13** (desktop packaging).
Per `PLANNING-DIRECTIVES.md` §6 each gets `/gsd-ui-phase <n>` after its discuss step. This
artifact exists so those five runs are **fast and evidenced rather than invented**: it surveys
how real products solve each surface, states take-this/fix-that per source in the discipline
round one used, and proposes **2-3 costed layout options per surface with the tradeoff named**
— never a single option presented as inevitable.

Nothing here is LOCKED. Nothing here overrides `.planning/UI-SPEC.md`, whose accessibility
gates (§8) and copywriting contract (§7) are LOCKED and bind every proposal below; a proposal
violating one is rejected on that basis alone and is marked **REJECTED (gate)** where it came
up. Where two options are both good, the recommendation is **ship both behind one named
interface** per Directive §3, and the interface is named.

## 0.1 Constraint basis (corrected 2026-08-10)

An earlier framing of this research brief asserted a blanket **"every proposal must survive
no-JS"** rule and attributed a per-lesson-JavaScript ban to `PLANNING-DIRECTIVES.md` §4.5. That
framing was overstated and has been corrected. **The five future per-phase UI-SPECs must inherit
the accurate list below, not the overstated one.** Recorded here because an invented constraint
propagates further than a real one.

**What was wrong:**

1. **There is no no-JS constraint in this project.** `.claude/CLAUDE.md:57` requires the core loop
   to "degrade, never block" when the **network** is unplugged — sitting, scoring, lessons, hints,
   evidence, reports. That is network resilience, not a JavaScript prohibition.
2. The "No Node.js, JavaScript" line at `.claude/CLAUDE.md:83` is explicitly marked **HISTORICAL**
   at lines 74-78 ("not forward constraints"). The 2026-08-09 amendment relaxed Python-only,
   no-build-step and offline-first to **preferences**.
3. **Directive §4.5 reads "the accessibility gates in `.planning/UI-SPEC.md`."** Those gates are
   activity-first, evidence-before-inference, progressive disclosure, calm progress, degrade
   honestly, same-loop-varied-media. **None of them forbids JavaScript.**
4. The product **already ships JavaScript**: CodeMirror 6 (MIT, ~300KB) is adopted in Phase 5 with
   a vendoring pipeline (ROADMAP Phase 5, absorbed research 2026-08-10).

**What actually binds, and what every proposal below is judged against:**

| # | Constraint | Status |
|---|---|---|
| B1 | **Accessibility gates in `UI-SPEC.md` §8.** Keyboard operability, focus order, DOM/reading order, screen-reader equivalents, reduced motion, and an accessible equivalent for any pointer interaction. | **LOCKED** |
| B2 | **Degrade honestly** (UI-SPEC §2.7). A surface says exactly what is unavailable and never fakes an answer, confidence, score or model result. Applies to network, model and capability loss. | **LOCKED** |
| B3 | **The copywriting contract** (UI-SPEC §7) and calm progress (§2.5). | **LOCKED** |
| B4 | **No answer leakage** — no key, unshown tier, or undisclosed content in HTML, JSON, ARIA, CSS-off text or accessible names before legal disclosure (UI-SPEC §11.1). | **LOCKED** |
| B5 | **Print is a first-class output, not a veto.** A lesson is a markdown file the learner owns and paper is a legitimate output, especially for EMT. Interactive affordances **may** collapse to a static equivalent in print — a gloss becomes a glossary appendix (ROADMAP:309). Every proposal must **name** its print form. A proposal is never rejected merely for being interactive. | Requirement |
| B6 | **No unbounded per-lesson arbitrary JavaScript.** This survives, but on its own reasoning and **not** on §4.5: author-supplied executable content in a lesson file is an unbounded review and security surface, and it stops the content being a plain file the learner owns. **Vendored, shared, reviewed components are fine** — CM6 is the precedent. | Requirement |
| B7 | **A model gets no typographic voice of its own.** Round-one ruling (`2026-08-09-visual-design.md` F15). Binds surfaces 2 and 4 hard: a generated hint and a model-suggested mark render in **Chrome voice inside a labelled container**, never in the Ledger voice reserved for things the runtime guarantees, and never in a voice invented for them. A model that gets its own face is a model that looks like an authority. | **LOCKED** |

**How to read the per-proposal lines below.** Each proposal names three things:

- `keyboard/SR:` its keyboard path and screen-reader equivalent (B1).
- `print:` its print form (B5).
- `degraded:` its behaviour when the network, the daemon, or the model is unavailable (B2).

Where a proposal additionally notes that it needs **no** JavaScript, that is recorded as a **cost
and robustness fact worth having** — a surface that works before its script loads is cheaper to
test and cheaper to keep accessible — and **never** as the reason another option was rejected.

**Reconsidered under the correction.** Three items were downgraded or rejected in the first draft
on no-JS grounds alone and have been revisited: the in-sitting gloss fetch (§1.2b), interactive
lesson figures (§1.5), and the first-launch guided tour (§5.3). Each now carries its verdict on
product merit and real cost. Rejections that rest on **B4 answer leakage** (§3.4 G3, §6.3 C2) or
on a **shell change** (§1.3 R3, §2.3 H3, §4.4 S3) are unaffected and stand.

### The single most important correction to round one

Round one (`2026-08-09-differentiators-d1-d2-d3.md` §D1.2) frames the gloss popover as a
**JS enhancement** over a no-JS link fallback. That framing is now wrong and it matters,
because it is the load-bearing assumption under Phase 3.1's biggest UI risk.

**The Popover API is fully declarative.** `<button popovertarget="gloss-x">` paired with
`<div id="gloss-x" popover>` gives show/hide toggling, Escape dismissal, light-dismiss,
focus return, and top-layer stacking **with zero JavaScript**, and it is supported across
Chrome, Edge, Firefox and Safari [CITED: developer.mozilla.org Popover_API; web.dev/blog/popover-api;
dfm2html.com/tutorials/accessible-drop-down-menus-in-2026-without-a-framework]. **CSS Anchor
Positioning is Baseline 2026**, so tethering the panel to its trigger is also zero-JS
[CITED: nexgismo.com/blog/css-anchor-positioning-replace-javascript-tooltip-library-2026;
lucioduran.com/blog/css-anchor-positioning-popover-api-2026].

So the gloss popover is **not** an enhancement over a link fallback — the popover *is* the
baseline, and it arrives with Escape, focus return and top-layer stacking already correct, which
is most of B1 satisfied by the platform rather than by us. JavaScript is still available and still
useful here (hover-to-open, and fetch-on-open for the gated in-sitting case, §1.2b), and neither
is forbidden. The finding is a **cost and correctness** finding, not a purity one: the cheapest
and most accessible version of this component is the declarative one, and Phase 3.1's UI-SPEC
should be written from that footing rather than from round one's "JS enhancer" framing.

---

## 1. Surface 1 — the reading surface (Phase 3.1)

The biggest gap, and the one **Phase 6.2 must reuse rather than re-invent**. If 6.2 ships a
second reading layout the project has two readers, which is the same class of error as two
parsers. Everything in §1 is written so §3 can say "reuse, plus three additions."

### 1.0 What the surface must show

From Brief 2 §4.3 and ROADMAP 3.1 criteria: gloss popovers for `[[term]]`, `[!KEY]` blocks,
`[!EXAMPLE]` annotated steps, `[!CHECK: <id>]` inline placement anchors, the reading column at
`--measure-prose` 66ch, and print CSS. Plus, inherited from round one and not restated here:
three heading levels, spacing-asymmetric headings, spaced paragraphs, wide-escape tables and
figures, focusable `<pre>`, inline `<details>` notes instead of margin sidenotes.

### 1.1 Prior art — take this, fix that

| Source | Take | Fix / reject |
|---|---|---|
| **Kindle Word Wise** [CITED r1: amazon.com nodeId=201645250] | The **density control** as a concept: a learner setting for how many terms are marked. | Reject the above-the-line inline render — it seizes line-height control and fights the 66ch/1.65 contract. Round-one ruling, restated because it will be re-proposed. |
| **LingQ** [ASSUMED r1] | State lives **on the word**, in the reading flow, not in a sidebar. | Reject background-colour-as-state: colour alone is a UI-SPEC §7 violation. Our channel is **underline style**, colour secondary. |
| **gwern.net** [CITED r1: gwern.net/design] | Semantic zoom — title, abstract, headers, body, collapsed sections, link previews — as the way to navigate a long document instead of paginating. Core pages work with JS off. | Reject margin sidenotes (no free margin; the support column is spoken for) and section auto-numbering (apparatus without a reader). |
| **Tufte CSS** [CITED r1: edwardtufte.github.io/tufte-css] | The `fullwidth` escape hatch as an explicit authored affordance, and CSS-only-by-policy as a *stated* constraint rather than an accident. | Its measure (~55%) is narrower than our 66ch and it has no assessment surface competing for space. Take the policy, not the numbers. |
| **Stripe docs** [CITED r1: designmd.cc/benchmarks/stripe] | Tight display tracking against generous body leading; heading sizes drop one step on mobile. | **Reject the scroll-synced code rail.** It is JS, it earns its keep on marketing pages, and our right column is the support column. |
| **MDN** [ASSUMED r1] | The right-hand "In this article" TOC as the standard long-document orientation answer. | Reject the scroll-spy JS for the baseline; a static heading `<nav>` gets ~90% of the value at zero JS. `aria-current` highlighting is a legitimate enhancement, never a requirement. |
| **Execute Program / Brilliant** [CITED r1: mike.place/2020/executeprogram] | Interleave short prose with a check instead of paginating. | That is Phase 6.2's loop, **not** a 3.1 scroll affordance. 3.1 must not paginate lessons. Reject Brilliant's celebration motion outright — UI-SPEC §2.5 LOCKED. |
| **Popover API + CSS Anchor Positioning** [CITED: MDN; modern-css.com/articles/build-a-tooltip-system] | The whole mechanism, declaratively. This is the finding of §0. | `interestfor` (hover-to-open) is **not Baseline** — Chromium-only with recorded WebKit objections [CITED: open-ui.org interest-invokers explainer; MDN Using_interest_invokers]. So hover is decoration; it may never be the only path. |

### 1.2 The hard part: a gloss that satisfies the accessibility gate, print, *and* the answer-leak gate

Three requirements collide. Taking them one at a time.

**(a) The reading-surface gloss.** Solved, and more cheaply than round one thought. In the
**lesson reader**, each
`[[term]]` renders as `<button popovertarget="gloss-<slug>" popover-ish>` with a sibling
`<div id="gloss-<slug>" popover>` holding the DEF and a "Full entry" link to the appendix
anchor. Zero JS. Keyboard, tap, Escape, focus return, and light-dismiss are browser behaviour.
Anchor positioning places it; a `position-try` fallback keeps it on screen at 320px. The
glossary `<dl>` appendix is still always rendered, because it is the print surface and the
"Full entry" target.

**(b) Inside a live sitting, where `glossable()` may be false. [RECONSIDERED]** Round one's answer
was `GET /gloss?item=&term=` fetched on first open. The first draft of this artifact treated that
as a defect because it needs JavaScript. **That was wrong, and the fetch is in fact the right
primary design**, because it is the mechanism that keeps the gloss body out of the sitting's HTML
entirely — which is a B4 answer-leak property, not a JS property. Round one had this right.

What is still worth adding is a **degraded path**, on B2 rather than on a JS taboo: if the script
has not loaded or the daemon is unreachable, a permitted term renders as a real
`<a href="/gloss?item=&term=&return=">` and following it is an ordinary navigation — the runtime
records the `term_lookup` server-side *because it served the page*, and a "Back to the question"
link returns. Same server contract, same event, one extra template. A non-permitted term renders
as plain text with no affordance and no DOM trace under either path, exactly as round one requires.

`keyboard/SR:` a real `<button>` or `<a>` in reading order; `aria-details` associates the gloss;
AT receives the DEF text and never more. `print:` §1.4 Proposal C. `degraded:` navigation
fallback above; with no daemon at all, plain text plus the appendix, and the surface says the
gloss is unavailable rather than silently dropping the affordance.

**(c) Print.** `[popover]` is `display:none` until shown, so a naive print sheet prints the
trigger and silently drops every gloss. Three ways out, costed in §1.4 Proposal C.

### 1.3 Layout options for the reading column

Three options. All three are static server-rendered HTML and therefore satisfy B1 and B5 by
construction; they differ in what they do with horizontal space, and the tradeoff is stated.

**Option R1 — Single column, wide-escape (recommended default).**
One 66ch (`--measure-prose`) column, centred in the activity canvas; tables, figures, code
results and `[!EXAMPLE]` step grids may escape to `--measure-wide` 90ch. Headings, `[!KEY]`,
`[!CHECK:]` anchors all sit in the reading column at full measure.
*Tradeoff:* nothing competes with the prose, and the layout is identical in the reader, in
6.2's gated mode, and in print — one layout, three uses, which is the whole point. Cost: **S**.
*Against:* leaves horizontal space unused on a 1280px desktop, and a long lesson has no
persistent orientation cue beyond the top-of-lesson `<nav>`.
`keyboard/SR:` headings are real headings in reading order; nothing is pointer-only.
`print:` the measure becomes the page measure. `degraded:` unaffected — static HTML.

**Option R2 — Reading column plus a sticky heading `<nav>` in the support column.**
R1, plus the static TOC lives in the existing UI-SPEC §3 support column on desktop and inside
the "Help and evidence" disclosure on tablet/narrow. This is the MDN answer with the JS removed.
*Tradeoff:* real orientation value on a 3000-word lesson, at the cost of putting the TOC in the
same column the hint ladder occupies during a sitting — so in a **sitting** the TOC must yield,
and 6.2 has to specify which. That "which wins" question is exactly the kind of thing that
should be settled in 3.1's UI-SPEC and not discovered in 6.2.
Cost: **S** on top of R1.
`keyboard/SR:` a labelled `<nav>` of real anchors, after the activity in DOM order per UI-SPEC §3;
scroll-spy `aria-current` is an enhancement and is announced, not merely painted.
`print:` the `<nav>` is `display:none` — a printed page does not need a TOC of itself, and if it
does, that is Proposal C's page-reference machinery, not a nav.
`degraded:` the anchor list is server-rendered; only the current-section highlight is lost.

**Option R3 — Two-track: prose column plus a persistent narrow "margin rail" for provenance.**
The Tufte move, adapted: a ~20ch rail carrying only `[SRC:]` locators and `[!KEY]` export
identities in Ledger voice, collapsing under the paragraph on tablet/narrow.
*Tradeoff:* it is the most distinctive of the three and it is the only one that makes the
Paper/Ledger authority split visible **in the layout** rather than only in the type. But it
directly contradicts round one's structural rejection of margin notes — the support column
already owns that third — and it introduces a third responsive behaviour to test at three
widths. **Do not ship R3 in 3.1.** Record it as the reason a later phase might revisit the
shell, not as a 3.1 option.

**Recommendation: ship R1 and R2 behind one setting, `reader_nav: none | column`.** They are
the same DOM with one optional `<nav>`; per Directive §3 this is a registration, not a fork,
and R2 degrades to R1 by omitting one element. R3 is recorded and rejected for this phase.

### 1.4 Block-level proposals

**Proposal A — `[!KEY]` as an index card.**
Round one's design (`2026-08-09-visual-design.md` §10) stands: `<section>`, visible text label
"Key point", 1px `--line` border, `--card` background, a single non-blurred `box-shadow` hint of
physicality, and a Ledger-voice footer showing its export identity. The thing to add here is the
**footer's honesty**: `key: airway-opa-01 · exports to Anki` is a claim about a file the learner
can inspect, so it renders in Ledger voice; the "Add to review" affordance is a `<form method="post">`.
`keyboard/SR:` a `<section>` with a visible text label carrying the semantics, icon `aria-hidden`;
the review control is a real button. `print:` a bordered box with its label; the `?print=drill`
variant that blanks clozes and prints an answer list at the end is a **second stylesheet, not a
second renderer** — cost S, and it is the cheapest thing in this entire document that a learner
will actually notice. `degraded:` with no daemon the block is fully readable and the "Add to
review" control is **absent with a stated reason**, never a dead disabled button (UI-SPEC §8.9).

**Proposal B — `[!EXAMPLE]` as annotated steps.**
Brief 2 §4.3 rules `[!EXAMPLE]` a callout *kind*, not a new block, and `math-worked` makes it
the annotated worked example that carries the whole `math-worked` style. Two renderings, and
this is a genuine fork worth shipping both of:
- **B1 — stacked annotation.** Each step is a `<li>`; the annotation is a second line under the
  step in `text-xs` Chrome voice. Reads top-to-bottom, wraps at any width, prints as-is.
- **B2 — two-column annotation.** `<ol>` of steps at `--measure-prose`, annotations in a
  parallel column, joined by a shared row. Reads like a worked example in a textbook — which is
  the entire point of `math-worked` — but needs a stacked fallback under 768px and a decision
  about whether print uses the two-column or the stacked form.
*Tradeoff:* B1 is free and never breaks; B2 is materially better for math and materially more
responsive-test surface. **Ship both behind `example_layout: stacked | parallel`**, default
`stacked`, with `math-worked` declaring `parallel`. This is a CSS-grid class swap on one
container, so it is one interface. Cost: **S** for B1, **S-M** for B2.
`keyboard/SR:` both are an `<ol>`; in B2 the annotation must be in the same list item as its step
so reading order pairs them, not in a parallel list. `print:` both; B2 must declare its print form
explicitly rather than inheriting the screen breakpoint. `degraded:` unaffected, it is CSS.

**Proposal C — print CSS for glosses.** The unsolved part of §1.2(c). Three mechanisms:
- **C1 — appendix only (floor).** `[popover] { display: none }` in print; the term keeps its
  dotted underline; the full glossary `<dl>` prints at the end. Zero risk, works today, and it
  is what round one already assumed. *Weakness:* on paper the reader has no idea which page the
  entry is on.
- **C2 — appendix plus page references.** C1 plus `a.term::after { content: " (p. " target-counter(attr(href), page) ")" }`.
  This is the CSS Generated Content for Paged Media cross-reference mechanism and it is the
  correct one [CITED: w3.org/TR/css-gcpm-3; print-css.rocks]. **But browser support for
  `target-counter` is a print-engine feature, not a browser one** — it is standard in Prince and
  Paged.js, and I could not confirm it in Chrome or Firefox print output this session
  [UNVERIFIED, §8]. Treat C2 as *conditional*: ship it only behind a fixture that actually prints
  a page number, and degrade to C1's plain text when the engine ignores it, which is the natural
  failure mode of an unsupported `content` function.
- **C3 — inline print footnotes.** `@media print` un-hides each `[popover]` and reflows it as a
  small bordered note after the paragraph that used it. Every gloss is on the page where it is
  needed, no page references required, no unsupported CSS.
  *Weakness:* a term used four times prints four glosses, which on an EMT chapter is noise;
  needs a `:first-of-type`-ish authoring or renderer rule to print only the first use.
*Tradeoff:* C1 is safe and slightly worse to read; C3 is better to read and more machinery;
C2 is the elegant answer standing on an unverified capability.
**Recommendation: ship C1 and C3 behind `print_gloss: appendix | inline`, default `appendix`,
and treat C2 as a progressive enhancement layered on C1** — it either prints a page number or it
does not, and nothing breaks either way. Cost: **S** (C1), **S-M** (C3), **S** (C2 as enhancement).

**Proposal D — `[!CHECK: <id>]` as a placement anchor in 3.1.**
In 3.1 the anchor carries no key and no scoring path (Brief 2 §4.3). It must therefore render as
something honest and inert. Two candidates:
- **D1 — a labelled rule.** A horizontal `--line` rule with a Ledger-voice label
  `Check · <objective>` and, where a runtime is present, a link to the item. Reads as "the lesson
  pauses here."
- **D2 — an empty slot.** A bordered region the same width as the eventual check, holding the
  Ledger-voice line `This check is available when you are reading with a session.`
*Tradeoff:* D1 is quieter and prints well; D2 pre-reserves the vertical space so that turning on
6.2's gate does not reflow the page, which matters because reflow-on-state-change is exactly the
kind of thing that makes a gate feel like a trick. **Recommend D2 for the reader and D1 for
print** — they are the same element with a print rule, not two designs.
`keyboard/SR:` an inert region needs no control; when 6.2 activates it, it becomes a real form.
`print:` D1; a printed lesson has no session, so an empty slot on paper is a lie.
`degraded:` D2's copy already states the condition, which is B2 satisfied by construction.

### 1.5 Interactive lesson figures — the rejection, reconsidered and narrowed

**[RECONSIDERED.]** The first draft rejected "any gloss, example, or check that needs per-lesson
JavaScript" and cited Directive §4.5. **That citation was wrong** (§0.1) and the blanket form of
the rejection does not survive. The narrower rejection does, on its own reasoning:

- **Still rejected — author-supplied executable content in a lesson file** (a `<script>` block, an
  inline expression evaluator, arbitrary JS in a fenced block that the renderer runs). Reason
  **B6**: it is an unbounded review and security surface, and it stops the lesson being a plain
  file the learner owns and can hand to someone else. This is also independently consistent with
  Brief 2 §4.3's rejection of explorable explanations as a *style*, and with 06.1's existing rule
  that bank-authored JavaScript is refused (ROADMAP 06.1 criterion 1). Nothing here reopens that.
- **No longer rejected — a vendored, shared, reviewed interactive component that a lesson
  *declares*.** This is exactly the CM6 precedent and exactly 06.1's declarative SVG protocol: the
  lesson names a scene and its parameters, the renderer owns the code, one implementation is
  reviewed once. A manipulable figure inside a lesson section is therefore **legal and should be
  planned as such** — via 06.1's protocol, as a figure inside a section, and it must carry the
  three lines every proposal here carries (equivalent semantic controls per UI-SPEC §8.5, a static
  print form, and a stated behaviour when the daemon is gone).

The practical consequence for Phase 3.1: the phase does not need to build this, but its UI-SPEC
should **not** write a prohibition it would then have to unwind in Phase 9. Say "declarative and
vendored, never author-supplied code," which is a rule that will still be true in three phases.

---

## 2. Surface 2 — the hint ladder and feedback modes (Phase 6)

**The visible-lock card is the differentiator's entire UI surface.** Everything the project
claims — the runtime and not a model decides what reaches the learner — is either legible in
this card or it is a sentence in a README. Round one already found the reason
(`2026-08-09-landscape-widening.md` §5): Socratic tutoring is commoditised at the prompt layer
in every competitor, so **the structural lock differentiates only if the learner can see that it
is structural**.

### 2.1 Prior art — take this, fix that

| Source | Take | Fix / reject |
|---|---|---|
| **Khanmigo** [CITED r1: agentconn.com; neuralclass.uk] | The three-part redirect copy formula. | **Reject naked Socratic dialogue as the refusal surface.** Its top documented complaint is that a learner who wants help gets a question. The refusal must be **structural and visible**, not conversational — a card that says a tier is locked, not a tutor that declines. This is the single strongest anti-pattern in the whole landscape. |
| **Duolingo "Explain My Answer"** (free to all users 2026-01-01) [CITED r1: blog.duolingo.com/explain-my-answer-now-free] | The inverse lesson: explanation is **learner-pulled and post-verdict**. A hint the learner asked for after a verdict is not the same object as a hint pushed before one. | Do not let it become a general chat affordance; it is one control, tied to one attempt, with a parent link. |
| **Anki's four grade buttons** [ASSUMED r1] | Self-rating is legitimate and cheap where nothing is scored. | Reject the visual grammar wholesale — four coloured buttons is meaning-by-colour and a UI-SPEC §7 violation, and it trains the learner to read colour as verdict, which is precisely what the `--pending` surface must not do. |
| **Brilliant** [CITED r1: screensdesign.com] | Per-distractor feedback; we already author `DA:` per option. | **Reject celebration motion and the branching progress map.** LOCKED §2.5. Brilliant spends its motion budget on exactly what our contract bans. |
| **Execute Program's SRS UX** [CITED r1: mike.place/2020/executeprogram] | Users disliked the opaque "day 64, never again" cutoff. Pace honestly; expose the schedule. | This is Phase 10's problem, but it lands here as a copy rule: never state a hint or interval outcome the learner cannot inspect. |

### 2.2 The non-deferrable field problem: B15 latency and duration across every client

ROADMAP 6 criterion 7 makes latency and duration **non-deferrable** — the evidence log is
append-only, so a field not written now can never be backfilled. Timing is usually a client-side
measurement, and this project has **three** first-class clients: the browser, the CLI, and the
static offline build submitted later. A plan that assumes `performance.now()` produces a log whose
series is comparable only within one of the three. This is a real conflict independent of any
JavaScript question, and the UI-SPEC needs the answer written down.

**The answer is two fields with different provenance, and only one of them is the record.**

- `served_at` / `received_at` — **server-side timestamps**, taken when the runtime renders the
  item and when the response POST arrives. Duration is the difference. Available in **every**
  client — browser, CLI, and static-build-then-submit. This is the record. It measures wall-clock
  from serve to submit and it honestly includes the learner making tea.
- `first_input_ms` — **optional, client-measured, explicitly nullable**, present only where a
  client measured it. Genuinely useful for latency-to-first-keystroke, and useless as a comparable
  series because whole classes of session will lack it.

The UI consequence, and it binds the copywriting contract: **any surface displaying a duration
must say which of the two it is showing, and must never present a nullable client field as the
record.** A report that quietly falls back from one to the other has invented a number. The
Ledger voice exists for exactly this — a duration in Ledger voice is a claim the runtime makes;
there is no voice available for a claim the browser makes, and that is the correct outcome.

### 2.3 Layout options for the hint ladder

**Option H1 — vertical tier rail (round one's F8, recommended).**
A vertical stack of tier cards in the support column. Shown tiers are `--card` with a Ledger-voice
header `TIER 2 · authored`. Locked tiers are `--chip` with a **dashed** `--line` border and the
literal visible text `Tier 3 unlocks after another attempt`. The dashed border plus the Ledger
label is the visual signature of "the runtime holds the key" and no competitor has it.
*Tradeoff:* the learner sees the whole shape of the ladder at once, which is the differentiator
made visible — and also sees how far they have to go, which on tier 1 of 6 can read as a long
road. Cost: **S-M**.
`keyboard/SR:` each shown tier is a landmarked card in reading order; the stumped control is a
normal button; **locked tiers contain no hidden text and no ARIA label carrying it**, so there is
nothing in the DOM or the accessibility tree to leak (B4, UI-SPEC §8.4, §11.1). Tier arrival is
announced once through the single `role=status` region without a focus jump.
`print:` shown tiers print; locked tiers print as their visible locked text. A printed page is a
record of a sitting, and "tier 3 was never unlocked" is part of that record.
`degraded:` shown tiers are server-rendered and the stumped control is a form POST, so the ladder
is fully operable before any script loads. With the **model** unavailable, the authored ladder is
untouched and the generated-support slot states `Generated help is unavailable. You can keep
learning with the lesson and authored hints.` verbatim (UI-SPEC §7).

**Option H2 — single slot plus a shown-history disclosure.**
One card showing the most recent tier, with earlier tiers behind a `<details>` labelled
`Hints shown (2)`, and a single line naming the next legal action.
*Tradeoff:* far calmer, much less vertical space, works better at 375px — but it **hides the
ladder**, which means it hides the differentiator. It is the right answer if the ladder ever
grows past six tiers, and the wrong answer today. Cost: **S**.
`keyboard/SR:` `<details>`/`<summary>` is natively operable and announced with its state.
`print:` force the `<details>` open. `degraded:` identical to H1.

**Option H3 — inline-under-the-item stack.**
Tiers accumulate directly under the response controls in the activity canvas rather than in the
support column.
*Tradeoff:* keeps the learner's eye in one place and is the best narrow-viewport behaviour by
construction — but it puts hint content inside the activity canvas, which UI-SPEC §3 reserves for
the active task and §6 requires the support column to follow in DOM order. It is a shell change,
not a component choice. **Do not ship H3 without changing UI-SPEC §3**, which is out of scope for
a Phase 6 UI-SPEC.

**Recommendation: ship H1 and H2 behind one setting, `hint_display: rail | slot`,** default
`rail` on desktop and `slot` under 768px. They render the same server-side data with different
CSS and one `<details>` wrapper, so this is one component with a variant, not two. H3 is
recorded as blocked on a shell decision.

### 2.4 The `--pending` model suggestion, so it never reads as a grade

Brief 2 §4.5 is precise and this is the surface that has to keep the promise: **self-mark first**;
the model suggestion sits behind a disclosure control `suggestion_reveal` with values
`after-self-mark` (default), `on-request`, `never`, all three shipped per Directive §3; **never a
number, never a fraction, never a check or cross glyph** — a `--pending` token only; accept is the
existing `mark_event`; a suggestion never accepted stays pending forever; a pending mark
influences nothing but counts as an attempt.

Three presentation options, and the differences are real.

**Option P1 — sequenced disclosure (recommended).**
Learner writes the response. The revealed model answer appears. The learner self-marks against it
(this is the highest-evidence approach in Brief 2 §4.4: g=0.55/0.664, and a learner self-mark
*is* a human accept, which dissolves the pending state rather than managing it). Only then does a
`<details>` appear: `A suggested review is available`. Opening it shows the per-criterion claims
as a plain list, each in Chrome voice inside a container labelled `Suggested review — not a mark`,
with a `--pending` chip on the container and no glyph on any row.
*Tradeoff:* the strongest possible guarantee that the suggestion never front-runs the learner's
own judgement, at the cost of three steps before a learner ever sees it. Cost: **M**.
`keyboard/SR:` `<details>` is native; the `--pending` state must be **text in the container label**,
not only a token colour, so AT receives it (B1 + UI-SPEC §7 never-colour-alone).
`print:` prints as an open list under a `Suggested review — not a mark` heading. **Print must never
elide the label**, because a printed page with an unlabelled per-criterion list is indistinguishable
from a marked paper. Name this as an explicit print fixture.
`degraded:` self-mark is a form POST and accept is a second POST, so the learner's own path never
depends on the model. With the model unavailable there is simply **no suggestion and no
disclosure control** — not an empty one — and the surface says so if it says anything.

**Option P2 — always-visible, always-labelled.**
The suggestion renders inline with the response, permanently labelled, permanently `--pending`,
with `Accept this review` beside it.
*Tradeoff:* honest and one step shorter, but it makes the suggestion the first thing the learner
reads, which destroys the self-assessment effect that is the entire reason to prefer self-marking.
**Reject for tier-3 open text.** It is defensible only for `suggestion_reveal: on-request`, which
is what that value is for.

**Option P3 — per-criterion checklist the learner fills, with the suggestion as a second column.**
The rubric criteria render as a list the learner marks themselves; the model's view appears as a
parallel column after the learner commits.
*Tradeoff:* the best ergonomics for accepting a decomposed rubric (Brief 2 §4.4 justifies rubric
decomposition on accept ergonomics, explicitly **not** on accuracy), and the most honest — the
learner's column and the model's column are visibly different columns. But a two-column
compare at 375px is a stacked list again, and a side-by-side invites reading the model's column
as the answer key. **Ship P3 only if the discuss step wants it, and only behind P1's ordering.**

**Recommendation: P1 is the default and the shape of the interface. `suggestion_reveal` already
names the interface;** P2 is what `on-request` renders, and P3 is a later variant of P1's third
step. And restating the binding rule: **the suggestion has no typographic voice.** Not Ledger —
the runtime does not guarantee it. Not Paper — no author wrote it. Chrome voice, inside a labelled
container, exactly as `2026-08-09-visual-design.md` F15 rules.

### 2.5 The hint-ladder depth distribution readout

ROADMAP 6 criterion 11: a ratio with a stated denominator, a property of the system rather than the
person, **never shown to the learner with a target**.

**Option D1 — a plain table in Ledger voice (recommended).** Rows are tiers, columns are count and
share, with the denominator stated in words above the table: `Of 84 correct responses in modes
where the ladder runs`. That is it. Cost: **S**.
*Tradeoff:* boring and unimpeachable. Nothing about it can be read as a score about the learner.
`keyboard/SR:` a real `<table>` with headers; narrow viewport uses the labelled scroll wrapper
UI-SPEC §8 already requires. `print:` natively. `degraded:` server-computed.

**Option D2 — a horizontal stacked bar above the table.** Same data, one CSS-only bar built from a
flex row of `<div>`s with inline widths, each segment labelled in text.
*Tradeoff:* genuinely easier to read the shape at a glance, and it is the shape that reveals the
design failure this measure exists to catch — a ladder nobody climbs past tier 0. But a bar is
one CSS change away from looking like progress, and UI-SPEC §2.5 forbids progress framing. **Ship
D2 only with the table beneath it and no percentage above 100 rendered as a fill.** Cost: **S**.
`keyboard/SR:` the bar is decorative over the table and must be `aria-hidden`, with the table as
the accessible representation. `print:` the bar needs text labels because print may drop
backgrounds. `degraded:` inline widths are server-computed.

**Recommendation: ship both behind `depth_readout: table | table+bar`, default `table`.**
And bind one copy rule into the phase spec: this readout lives on the **report** surface and never
in the learning workspace. A distribution shown next to an active item is a target no matter how
it is worded.

---

## 3. Surface 3 — the executable textbook loop (Phase 6.2)

**6.2 reuses §1's reading layout. It adds exactly three things and redesigns nothing.**
That sentence should appear at the top of 6.2's UI-SPEC. This section exists to say precisely
what the three are.

### 3.1 What it adds

1. **A gate band at each `[!CHECK: <id>]` anchor.** The 3.1 anchor (Proposal D2, the reserved
   empty slot) becomes a rendered item with its response controls, under a Ledger-voice header
   naming the gate mode. Nothing above it changes.
2. **The recorded-skip control**, with copy that has to be exactly right (§3.3).
3. **A truncation boundary** below the gate, when `[GATE: required]`, plus the honest statement
   of what is below it.

Everything else — measure, heading ramp, `[!KEY]`, `[!EXAMPLE]`, glosses, print — is 3.1's,
unchanged. If 6.2's plan touches the reading CSS beyond adding the gate band, it has failed.

### 3.2 Prior art — take this, fix that

| Source | Take | Fix / reject |
|---|---|---|
| **Execute Program** [CITED r1: mike.place/2020/executeprogram; mechanics secondhand — site is JS-rendered, §8] | Forced gating as a *pacing* device: prose is short, the check is immediate, and the next idea does not arrive until the check clears. | Reject the language lock-in and the closed content. Our version's content is a markdown file the learner owns — which is also why our gate can only ever be a default (§3.3). |
| **Runestone** [ASSUMED r1; runestone.academy returned 403, §8] | Executable/graded blocks inline in the textbook flow — the structural proof the pattern works. | Its visual identity is ~zero. Take the block placement, not the Bootstrap-era look. |
| **Brilliant** [CITED r1] | One idea, then an interaction, then the next idea. | It paginates because every screen *is* an interaction. Ours is prose with checks in it, so it scrolls. Do not import pagination. |
| **Progressive-disclosure cases in therapeutics/nursing education** [CITED: pubmed.ncbi.nlm.nih.gov/30025772; PMC12858445] | The same mechanic exists and is studied under "unfolding case" and "progressive disclosure"; documented gains in confidence at information-collection and plan-design steps. | The literature is about *cases*, which is §6, not about gating a textbook. Do not overclaim it as evidence for the gate. |

### 3.3 The gate is a default, not a lock — and the copy carries that

Brief 2 §4.3 (R3.3) gives the reason, and it is better than the mastery-learning argument:
**a hard gate is theater on a plaintext file the learner owns.** The claim cannot be kept, and an
unkeepable claim is worse than an absent feature. The loop's value is the return, not the wall.

That ruling has a direct UI consequence that the phase spec must not soften: **the skip control is
never styled as a transgression.** No warning colour, no confirm-you-really-want-this dialog, no
`--bad` token. It is a normal button, in the same visual register as `I'm stumped — show the next
hint` — which UI-SPEC §7 already LOCKS as "a normal button, not a warning" for exactly this reason.
Suggested copy for the discuss step to ratify (not locked here):
`Read ahead without answering` for `[GATE: required]`, and for `recommended` the check simply sits
in the flow with the rest of the lesson already visible beneath it.

The `gate_skip` event is a distinct event type, explicitly **not** a `response` with a null score
(ROADMAP 6.2 criterion 8), and Phase 6 criterion 10 already rules that a skip advances the reading
position and never the hint tier. The UI must therefore never render a skip in the hint ladder.

### 3.4 Layout options for the gate band

**Option G1 — truncate-and-reveal (recommended for `required`).**
Under `[GATE: required]`, the server renders the lesson **up to** the anchor, then the gate band,
then a Ledger-voice line stating what remains: `3 more sections below this check.` Clearing the
check (or skipping) re-renders the page with the next segment appended, and focus lands on the
new heading.
*Tradeoff:* the strongest version of the loop, and the reason it is defensible is that the
truncation is honest — the remaining content is **not in the DOM**, so the claim "the next idea
has not arrived yet" is true rather than a CSS trick. That also means the printed page of a gated
lesson is incomplete, which §3.5 has to handle. Cost: **M**.
`keyboard/SR:` focus moves to the newly revealed heading after the POST, which is the one place a
focus jump is correct because the page content changed; the status region announces the reveal
once. `print:` §3.5. `degraded:` server-rendered progressive disclosure — form POST, page
re-render, more content — so the loop works before any script loads and over a flaky link. A
client-side variant that swaps the section without a reload is a legitimate later enhancement,
but the truncation must stay **server-side** or B4 is lost.

**Option G2 — inline-and-continue (recommended for `recommended`).**
The whole lesson renders; the gate band sits in the flow with the check; the sections below it are
present and readable. Clearing the check marks the band as cleared.
*Tradeoff:* zero friction and zero theater, and it is the honest rendering of a soft gate. It
gives up the pacing effect entirely, which is why it is the wrong rendering for `required`.
Cost: **S**. `keyboard/SR:` the check is an ordinary item in reading order. `print:` trivially,
the whole lesson is there. `degraded:` static.

**Option G3 — collapse-and-expand.** The below-gate content ships in a `<details>` that opens on
clear. **REJECTED (B4 answer leakage — not a JavaScript objection):** the content is in the DOM.
For a lesson that is merely untidy; for a gated check whose *own* later sections may contain the
discriminating fact, it is a leak, and UI-SPEC §11.1 requires a fixture proving no undisclosed
content is in the HTML, ARIA, or CSS-off text. Recorded so it is not re-proposed, because it is
the cheapest-looking option and it is wrong. Note that this rejection is **unchanged by the §0.1
correction** — it never rested on a JS taboo.

**Recommendation: G1 and G2 are not alternatives — they are the renderings of `required` and
`recommended`, and `off` is 3.1's reader unchanged.** `[GATE: required|recommended|off]` is
already the named interface (Brief 2 §4.3) and it already selects between them. That is Directive
§3 landing for free.

### 3.5 Print, and the one thing 6.2 must decide

A printed lesson has no runtime, no session, and no way to clear a check. So:
**print always renders the complete lesson, ungated, with each gate band printed as a labelled
check.** A truncated printout is a defect, not a feature — the gate is a pacing device for a
reading session, and paper is not a reading session the runtime can observe.

The decision 6.2 owes: whether printing a `required` lesson records anything. **Recommend no.**
A print is not a skip; inventing a `gate_skip` on print would corrupt the gate-outcome-split
measure (ROADMAP 6.2 criterion 9) with events no learner generated. Record the reasoning so the
absence is a decision rather than an oversight.

---

## 4. Surface 4 — the selection engine (Phase 7)

Mostly headless. The whole surface is `select --explain` and the "why this item" trace, and
UI-SPEC §1 already classifies 07-06 as UI-DEPENDENT with a full workspace panel deferred to Phase
10. So this section is small on purpose, and its job is to stop the trace being invented twice.

### 4.1 The failure modes to design against

A selection rationale fails in exactly two ways, and they pull in opposite directions:

- **Black box.** "Recommended for you." No evidence, no runner-up, nothing inspectable. Every
  consumer recommender does this and it is why nobody trusts one.
- **Score theater.** "Priority 0.87." A number that looks like measurement, is actually the
  output of weights someone chose, and cannot be argued with. This is worse than the black box
  because it is a black box wearing a lab coat. UI-SPEC §4 `RecommendationCard` already bans its
  nearest relative: unknown is an explicit state, **not `0%`**.

The design target is the narrow path between them: **enough structure to be argued with, no number
that implies measurement.**

### 4.2 Prior art — take this, fix that

| Source | Take | Fix / reject |
|---|---|---|
| **Anki's Card Info** [ASSUMED] | The genre-defining move: a per-card panel showing the full review history, current interval, ease/difficulty, and due date, so any scheduling decision is inspectable after the fact. Nobody has to trust it. | It is a **state dump**, not a rationale — it shows what the scheduler knows, never why this card and not another. Take the inspectability; add the runner-up. |
| **FSRS** [CITED: deepwiki.com/ankitects/anki 4.1; open-spaced-repetition docs] | Difficulty, Stability, Retrievability are three named, separately-inspectable quantities rather than one opaque priority. Decomposition is what makes a schedule arguable. | Reject surfacing R as a percentage to a learner. A recall probability shown next to an item is a prediction about the person, and UI-SPEC §2.5 and §13 (no predictive learning analytics, no false precision) forbid it. |
| **ALEKS knowledge-space "fringe"** [CITED r1: aleks.com/about_aleks/knowledge_space_theory; Matayoshi et al. JMP 2021] | The rationale is **structural, not numeric**: this topic is ready because its prerequisites are known. That is a sentence a learner can disagree with by pointing at a prerequisite. Already adopted as ROADMAP 7 criterion 7. | Reject the pie chart as the primary surface. It is a mastery display, and mastery percentage is on UI-SPEC §13's do-not-build list. |
| **jpdb.io** [CITED r1: jpdb.io/faq] | Utility weighting — an item is worth serving because of what it unlocks, and that is stateable in words. | Its weighting is opaque in the UI; we owe the named strategy. |
| **Brilliant** [CITED r1] | One-idea-per-screen sequencing wording, already absorbed into ROADMAP 7. | — |

### 4.3 The shape: an ordered trace, not a score

ROADMAP 7 criterion 9 already gives the mechanism — every rule is a **named, registrable strategy**
with one interface (candidates in, ranked candidates plus a reason string out), and
`select --explain` names the strategy that ranked the winner. The UI contribution is to say what
the reason string has to contain, so five strategies do not each invent a different sentence.

**Proposal — the four-line trace.** In order, and in Ledger voice, because every line is a claim
the runtime guarantees:

1. **The filter and the pool.** `objective=airway-adjuncts · type=any · 14 candidates`
2. **The strategy that ranked the winner, by name.** `ranked by: prerequisite-fringe`
3. **The one field that separated winner from runner-up.** `chosen over Q31 — Q31 was served 2 days ago (cooldown), this was last served 19 days ago`
4. **What was *not* used.** `no pending marks were read` — because ROADMAP 7 criterion 11 makes
   that a selection-side invariant, and an invariant nobody can see is an invariant nobody
   maintains.

The rule that makes this hold together: **the trace names a field and a comparison, never a
weight and never a total.** "Q31 was served 2 days ago" is arguable. "Q31 scored 0.62" is not.
Where a strategy genuinely is numeric, it states the input, not the output.

### 4.4 Layout options

**Option S1 — CLI-first, `<details>` on the web (recommended).**
`itembank select --explain` prints the four lines. The web surface renders the identical four
lines inside a `<details>` labelled `Why this item?` in the support column, collapsed by default.
*Tradeoff:* one text artifact, two renderings, no divergence possible — the CLI twin is a
UI-SPEC-wide rule and this is the cheapest place to honour it. Collapsed-by-default keeps the
activity primary (UI-SPEC §2.1). Cost: **S**.
`keyboard/SR:` `<details>` is native and follows the activity in DOM order; it never takes focus
after an ordinary submit. `print:` force open — a printed sitting record should carry why each
item was served. `degraded:` the trace is server-rendered from a deterministic decision, so it is
present whenever the item is; it never depends on a model (§4.5).

**Option S2 — a candidate table.** Winner and runner-up as two rows with the comparison fields as
columns, so the comparison is spatial rather than sentential.
*Tradeoff:* materially clearer for a discrimination pair or a blueprint-weighted exam sim, where
"why this over that" is the actual question — and materially more surface: a table needs the
narrow-viewport treatment UI-SPEC §8 requires, and it invites a third column and then a fourth,
which is how a table becomes a dashboard. **Ship S2 only for the pair/blueprint cases**, not as
the general trace.

**Option S3 — a persistent "why" panel in the workspace.** **Do not build.** UI-SPEC §1 defers
the full panel to Phase 10 and §13 forbids a metric dashboard above the next instructional
action. Recorded so Phase 7's discuss step does not re-open it.

**Recommendation: S1 is the trace. S2 is a variant of S1's step 3 that renders two candidates as
rows instead of one sentence** — same data, same strategy interface, one extra template. Name the
interface `explain_render: lines | table`.

### 4.5 The binding constraint, restated

**A model gets no typographic voice of its own,** and Phase 7 is where it will be tempting to
forget, because a rationale sentence *feels* like generated prose. It is not. The trace is
runtime output about a deterministic decision, so it renders in **Ledger voice**. If a model ever
paraphrases a trace for readability, that paraphrase is a separate, labelled, Chrome-voice object
sitting next to the trace, and the trace does not move. A rationale a model rewrote is a rationale
the runtime no longer guarantees.

---

## 5. Surface 5 — desktop packaging (Phase 13)

**Window chrome, the installer, and first launch only. This is not a redesign**, and the strongest
thing a Phase 13 UI-SPEC can do is say so in its first line. Every surface inside the window is
already specified by the phase that owns it.

### 5.1 Window chrome

Tauri 2.x over the existing localhost HTTP surface (ROADMAP 13 criterion 1); the WebView is the
OS's own (WebView2 on Windows), which is why the shell is ~3MB rather than Electron's ~150MB
[CITED: v2.tauri.app/blog/tauri-20; dev.to/ottoaria Tauri in 2026].

**Recommendation: native window decorations. Do not build a custom titlebar.** A custom titlebar
is the default aesthetic move in every Tauri tutorial and it costs three things this project
cannot pay: Windows Snap and Aero-shake behaviour must be reimplemented, the drag region is a
known accessibility and keyboard-focus hazard, and it is a second place where theme tokens have to
be kept in sync with `theme.py` — which is LOCKED as the single palette source (UI-SPEC §7). The
gain is a slightly more branded screenshot.
*If the discuss step wants it anyway,* the tradeoff to state is exactly that trade, and the
mitigation is that the titlebar carries no controls other than the OS ones.

Two things the chrome **should** carry, because they are honesty affordances rather than decoration:
- The sidecar's state in the window, not only in a log: a single Ledger-voice line
  (`runtime: listening on 127.0.0.1:PORT`) reachable from a menu. ROADMAP 13 criterion 3 makes
  orphaned-sidecar and held-port behaviour a success criterion; if the learner cannot see the
  state, they cannot report the failure.
- The CLI twin, discoverable. ROADMAP 13 criterion 5 says every capability stays reachable from
  the CLI without the shell. A menu item that shows the equivalent command for the current view
  makes that claim visible instead of documented — and it is the same "empty state names the one
  command that fills it" pattern round one already recommends
  (`2026-08-09-visual-design.md` F10).

### 5.2 The installer

NSIS, per ROADMAP 13 criterion 2. Two UI-relevant notes:

- **Default to a per-user install.** It avoids the UAC prompt on first run, and a
  learning tool that asks for administrator rights before showing anything is a tool a cautious
  user cancels.
- **The antivirus warning is a first-class screen, not a footnote.** ROADMAP 13 criterion 4 names
  AV false positives on frozen Python as *the* top risk and requires an executed checklist. The
  installer should state plainly, before install, that the app bundles a Python runtime and that
  some AV products flag frozen Python, with the signing fingerprint shown. This is the "degrade
  honestly" principle (UI-SPEC §2.7) applied to the one moment the product is most likely to look
  like malware.

### 5.3 First launch

**Option F1 — one screen, two doors (recommended).**
A single view: `Open a bank folder` and `Open the sample bank`. Nothing else. The sample bank
already has to exist as a fixture, and round one's F10 empty-state pattern already argues for it.
Cost: **S**.
*Tradeoff:* the fastest path to the actual product, and it leaves the learner in a real lesson
within one click. It teaches nothing about the app, which is correct — there is nothing to teach
until there is a bank.
`keyboard/SR:` two real buttons, focus lands on the first. `print:` n/a.
`degraded:` the view is served by the same daemon as every other surface; if the sidecar has not
come up, this is the screen that must say so plainly with the port and a retry (B2), because it
is the first and most likely place a packaging failure shows.

**Option F2 — F1 plus a three-step checklist that stays until complete.**
`Open a bank` / `Run your first sitting` / `See your evidence`, persisted and dismissible.
*Tradeoff:* genuinely useful for a tool whose loop is not obvious from one screen, and it is the
one onboarding pattern that does not become engagement pressure **provided it has no streak, no
completion celebration, and a permanent dismiss**. UI-SPEC §2.5 is LOCKED and a checklist that
nags violates it. Cost: **S-M**.

**Option F3 — a guided tour with highlighted regions. [RECONSIDERED — still rejected, better
reason.]** The first draft rejected this partly because it "needs JS overlays," which is not a
valid objection (§0.1). It is still the wrong build, on three grounds that survive: it is
**per-surface coupling** that rots the moment any of the eleven phases changes a layout, so its
maintenance cost is paid by every future phase rather than by Phase 13; an overlay that traps
focus over the real UI is a B1 hazard that has to be got exactly right for no product gain; and
it is the most-skipped pattern in desktop software [ASSUMED]. Rejected on cost and value, not on
technology.

**Recommendation: ship F1, and F2 only if the discuss step decides the loop is not
self-evident** — behind `first_run: minimal | checklist`, defaulting to `minimal`. F1 is a
subset of F2's DOM, so this is one view with an optional block.

---

## 6. Cross-cutting — the `## SCENARIO` staged reveal

Owed by Phase 9 (Brief 2 §4.3, R3.2) but consumed by 3.1's `case-narrative` style and by 6.2's
loop, so it is specified here as cross-cutting rather than inside one surface.

### 6.1 The ruling this must render

Already fixed by Brief 2 §4.3 and not re-opened: ordered `[STAGE:]` blocks with a **closed
two-value advance vocabulary**, `on-ack` and `on-item`. `on-elapsed` rejected against
UI-SPEC:105 (calm progress, no countdown pressure); `on-correct` rejected because it gates on a
verdict. The reveal position is a **derived integer replayed from existing evidence**, so a model
authors the file but never moves the pointer. **No un-reveal. No answer locking.** Five lint
codes, zero new item types, zero scorer change.

### 6.2 How medical education actually phases a case

The mechanic is well-established and has three interchangeable names in the literature —
**unfolding case**, **serial case**, and **progressive disclosure** — used across nursing and
medical education [CITED: PMC12858445, scoping review of unfolding case-study learning;
pubmed.ncbi.nlm.nih.gov/30025772, progressive-disclosure cases across multiple therapeutics
courses]. The documented gains are in confidence at information collection, assessment, plan
design, and monitoring — that is, at the *steps of reasoning*, which is exactly what a staged
reveal is for and exactly what a single-shot vignette cannot exercise. Clinical vignettes
themselves are near-universal in clinical teaching and underpin morning report and case-based
learning [CITED: link.springer.com/article/10.1007/s11606-025-09531-5].

**What I could not verify** [see §8]: the specific claim that NBME-style sequential items forbid
returning to earlier answers. It is a widely-repeated description of sequential testlets, but I
found no primary source this session. **This matters, and the way it matters is convenient:** our
ruling already forbids answer locking on independent grounds, so the unverified claim would only
have been evidence *for* something we have already rejected. Do not cite it in the phase spec.

**Take this, fix that:**

| Take | Fix / reject |
|---|---|
| The stage is a **unit of information**, not a unit of time — new findings, a change in the patient's condition, a lab result. That is what makes `on-ack` and `on-item` the right advance vocabulary and `on-elapsed` the wrong one. | Reject the timed reveal in every form. It is countdown pressure and UI-SPEC §2.5 is LOCKED. |
| Earlier stages stay readable. The reasoning being exercised is *revision in light of new information*, which requires seeing what you knew before. | Reject any pattern that collapses or hides a prior stage. Answer locking is the classroom-exam version of the same instinct and is separately rejected. |
| The disclosure is authored, ordered, and fixed. A human wrote the sequence. | Reject any dynamic or model-chosen pacing. This is the whole point of the derived-pointer rule: a model authors stages, the runtime replays the position from evidence. |

### 6.3 Layout options

**Option C1 — linear append (recommended).**
Stages render top-to-bottom in the reading column, in order, up to the current reveal position.
Each stage carries a Ledger-voice header (`Stage 2 · 20 minutes later`) and the advance control
sits below the last revealed stage: for `on-ack`, a form button; for `on-item`, the item itself.
Advancing re-renders the page with one more stage appended and moves focus to the new stage
heading.
*Tradeoff:* it is the same mechanism as 6.2's G1 truncate-and-reveal, which means one
implementation serves both — the strongest argument available. Prior stages stay visible, which
the pedagogy requires. Long cases get long, which is what scrolling is for. Cost: **S-M** given
G1 exists.
`keyboard/SR:` each stage is a heading-led region in reading order; focus moves to the new stage
heading on advance and the status region announces the position once.
`print:` prints revealed stages in order with their headers, plus a Ledger-voice line stating the
position (`3 of 5 stages revealed`). A printed case that silently looks complete is dishonest.
`degraded:` server-rendered progressive disclosure — form POST, re-render. Unrevealed stages are
**not in the DOM**, which is what makes "not yet revealed" true rather than a CSS claim; a
client-side smoothing of the transition is a legal enhancement, the truncation is not.

**Option C2 — accordion of all stages, revealed ones open.**
All stages present, unrevealed ones collapsed. **REJECTED (B4 answer leakage — not a JavaScript
objection):** the unrevealed content is in the DOM, and for a case whose later stages contain the
finding that discriminates the answer, that is a leak under UI-SPEC §8.4 and §11.1. Same rejection
as 6.2's G3, same reasoning, recorded twice because it is the obvious-looking option in both
places. **Unchanged by the §0.1 correction.**

**Option C3 — one stage per page, with a stage rail.**
Only the current stage in the canvas; a rail of prior stages in the support column, each opening
its own view.
*Tradeoff:* the best behaviour for a very long case and the cleanest focus, but it breaks the
"earlier stages stay readable" requirement in the exact place it matters — while answering, the
learner should be able to see stage 1 and stage 3 together. **Reject for the default.** It is
defensible only as a narrow-viewport variant, and even there C1 with sticky stage headers is
probably better.

**Recommendation: C1, and say explicitly in the phase spec that it is the same renderer as 6.2's
gated reading.** Directive §3 does not apply here — this is not two good options, it is one that
survives the B4 answer-leak gate and two that do not.

### 6.4 The print form is a real deliverable

A staged case printed at position 3 of 5 is a **paper study artifact**: the case so far, the
question, and nothing that gives it away. That is a thing EMT learners actually want and it costs
one `@media print` rule on top of C1. It is worth naming as a success criterion rather than
leaving it to fall out, because "print what has been revealed, and say how much that is" is a
decision, and the alternative (print everything) is a leak.

---

## 7. Cost roll-up

Costs are S/M/L in the repo's existing sense, and are **incremental to what the phase already
owes**, not totals.

| # | Proposal | Interface name (Directive §3) | Kind | Cost | Phase |
|---|---|---|---|---|---|
| 1 | Declarative popover glosses (corrects round one's "JS enhancer" framing) | — | RENDERER | S (down from M) | 3.1 |
| 2 | In-sitting gloss: fetch-on-open primary, navigation as the degraded path | — | RUNTIME | S | 3.1 |
| 3 | Reading column R1 + optional TOC R2 | `reader_nav: none \| column` | RENDERER | S | 3.1 |
| 4 | `[!KEY]` index card + `?print=drill` sheet | — | RENDERER | S | 3.1 |
| 5 | `[!EXAMPLE]` stacked / parallel annotation | `example_layout: stacked \| parallel` | RENDERER | S-M | 3.1 |
| 6 | Print gloss appendix / inline; page refs as enhancement | `print_gloss: appendix \| inline` | RENDERER | S-M | 3.1 |
| 7 | `[!CHECK:]` reserved slot on screen, labelled rule in print | — | RENDERER | S | 3.1 |
| 8 | Server-side `served_at`/`received_at`; nullable `first_input_ms` | — | RUNTIME (one-way) | S | 6 |
| 9 | Hint tier rail / single slot | `hint_display: rail \| slot` | RENDERER | S-M | 6 |
| 10 | `--pending` sequenced disclosure, self-mark first | `suggestion_reveal` (exists) | RENDERER | M | 6 / 8 |
| 11 | Depth-distribution table (+ optional bar), report only | `depth_readout: table \| table+bar` | RENDERER | S | 6 |
| 12 | Gate band; truncate-and-reveal vs inline-and-continue | `[GATE:]` (exists) | RENDERER | M | 6.2 |
| 13 | Gated lesson prints complete and ungated; print records nothing | — | RENDERER | S | 6.2 |
| 14 | Four-line trace, CLI-first, `<details>` on web | `explain_render: lines \| table` | RENDERER | S | 7 |
| 15 | Native window chrome; runtime-state and CLI-twin menu items | — | PACKAGING | S | 13 |
| 16 | Per-user install; AV/signing statement as an install screen | — | PACKAGING | S | 13 |
| 17 | First launch: two doors, optional checklist | `first_run: minimal \| checklist` | RENDERER | S | 13 |
| 18 | `## SCENARIO` linear append, sharing 6.2's renderer | — | RENDERER | S-M | 9 |
| 19 | Staged-case print at the revealed position, position stated | — | RENDERER | S | 9 |

**Rejections recorded, each with the ground it actually stands on** (so they are not re-proposed,
and so none of them is re-derived from the withdrawn no-JS rule):

| Rejected | Ground | Affected by the §0.1 correction? |
|---|---|---|
| Author-supplied executable content in a lesson file (§1.5) | **B6** — unbounded review/security surface; the lesson stops being a plain file the learner owns. Consistent with ROADMAP 06.1 criterion 1. | **Narrowed.** A vendored, declarative interactive figure is now explicitly legal. |
| `<details>`-hidden below-gate content, G3 (§3.4) | **B4** answer leakage | No |
| Accordion of unrevealed stages, C2 (§6.3) | **B4** answer leakage | No |
| Margin sidenote rail, R3 (§1.3) | Structural — the support column already owns that third | No |
| Inline hint stack, H3 (§2.3) | Requires a UI-SPEC §3 shell change, out of scope for a Phase 6 spec | No |
| Persistent "why this item" panel, S3 (§4.4) | UI-SPEC §1 defers to Phase 10; §13 forbids a metric dashboard above the next action | No |
| Always-visible model suggestion for tier-3 open text, P2 (§2.4) | Destroys the self-assessment effect that is the reason to self-mark first | No |
| Guided tour, F3 (§5.3) | Per-surface coupling cost + focus-trap hazard, **not** technology | **Reconsidered, verdict unchanged, reason replaced** |
| Custom titlebar as default (§5.1) | Snap/Aero reimplementation, drag-region a11y hazard, second palette sync point | No |
| Timed stage advance `on-elapsed` (§6.1) | UI-SPEC §2.5 calm progress, LOCKED | No |
| Celebration motion, gamified progress, mastery percentage (§2.1, §4.2) | UI-SPEC §2.5 and §13, LOCKED | No |

---

## 8. What I could not verify

Recorded so no phase inherits a confident wrong answer, per Brief 2 §3.6.

- **`target-counter` in browser print output.** The CSS GCPM cross-reference mechanism is
  specified [CITED: w3.org/TR/css-gcpm-3] and standard in dedicated print engines, and Chrome has
  supported generated content in page-margin boxes since 131 [CITED: developer.chrome.com/blog/print-margins].
  I could **not** confirm `target-counter(attr(href), page)` resolves in Chrome or Firefox
  print-to-PDF. Proposal C2 is therefore an enhancement over C1, never a dependency.
- **`interestfor` / interest invokers are not Baseline.** Shipped in Chromium with recorded WebKit
  objections [CITED: open-ui.org interest-invokers explainer; MDN Using_interest_invokers]. Hover
  is decoration in every proposal here for the B1 reason — UI-SPEC §8 forbids hover-only controls
  at narrow widths regardless — so a polyfill is permitted but buys nothing that the declarative
  click/focus path does not already have.
- **The NBME "cannot change earlier answers" constraint on sequential items.** Widely repeated,
  no primary source found this session (§6.2). Not cited in any proposal.
- **Anki Card Info's exact field set** is training knowledge, not re-read this session. The
  pattern claim (state dump, not rationale) is robust; the field list is not.
- **Execute Program's mechanics remain secondhand** — the site is JS-rendered and could not be
  read directly, as Brief 2 §4.5 already records. **Runestone returned 403** in round one. Both
  carry into §3.2 and neither is load-bearing for a layout decision here.
- **No usability evidence exists for a "visible lock" hint UI specifically.** §2's H1 rail rests
  on the structural argument (Khanmigo's documented complaint is that its refusal is invisible and
  conversational), not on a measured comparison. Falsify at plan time with a UAT, not after
  building.
- **First-launch and installer numbers.** Tauri bundle-size figures are cited from 2026 secondary
  sources [CITED: v2.tauri.app/blog/tauri-20; dev.to/ottoaria], not measured against a
  PyInstaller-onedir sidecar. ROADMAP 13's 25-45MB target is the phase's own and is not confirmed
  here.

---

## Sources

**Verified this session (2026-08-10):**
[MDN Popover API](https://developer.mozilla.org/en-US/docs/Web/API/Popover_API) ·
[MDN Using interest invokers](https://developer.mozilla.org/en-US/docs/Web/API/Popover_API/Using_interest_invokers) ·
[MDN :interest-source](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Selectors/:interest-source) ·
[Open UI interest invokers explainer](https://open-ui.org/components/interest-invokers.explainer/) ·
[Accessible drop-down menus in 2026 without a framework](https://www.dfm2html.com/tutorials/accessible-drop-down-menus-in-2026-without-a-framework/) ·
[CSS anchor positioning replaces JS tooltip libraries](https://www.nexgismo.com/blog/css-anchor-positioning-replace-javascript-tooltip-library-2026) ·
[CSS anchor positioning + Popover API 2026](https://lucioduran.com/blog/css-anchor-positioning-popover-api-2026) ·
[modern.css tooltip system](https://modern-css.com/articles/build-a-tooltip-system/) ·
[CSS GCPM Level 3](https://www.w3.org/TR/css-gcpm-3/) ·
[print-css.rocks footnotes lesson](https://print-css.rocks/lesson/lesson-footnotes) ·
[Chrome print margin boxes](https://developer.chrome.com/blog/print-margins) ·
[Unfolding case-study learning scoping review (PMC12858445)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12858445/) ·
[Progressive disclosure cases in therapeutics courses](https://pubmed.ncbi.nlm.nih.gov/30025772/) ·
[Case to Vignette framework, JGIM 2025](https://link.springer.com/article/10.1007/s11606-025-09531-5) ·
[FSRS scheduler implementation (DeepWiki/Anki)](https://deepwiki.com/ankitects/anki/4.1-fsrs-scheduler-implementation) ·
[fsrs4anki tutorial](https://github.com/open-spaced-repetition/fsrs4anki/blob/main/docs/tutorial.md) ·
[Tauri 2.0 stable release](https://v2.tauri.app/blog/tauri-20/) ·
[Tauri in 2026](https://dev.to/ottoaria/tauri-in-2026-build-cross-platform-desktop-apps-with-web-technologies-better-than-electron-11mo)

**Carried from round one** (not re-fetched; see those artifacts for their own provenance):
gwern.net/design · edwardtufte.github.io/tufte-css · practicaltypography.com ·
mike.place/2020/executeprogram · blog.duolingo.com/explain-my-answer-now-free ·
aleks.com/about_aleks/knowledge_space_theory · jpdb.io/faq · docs.ankiweb.net/importing/text-files.html ·
screensdesign.com (Brilliant) · agentconn.com + neuralclass.uk (Khanmigo) ·
designmd.cc/benchmarks/stripe + /linear
