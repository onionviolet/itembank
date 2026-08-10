---
phase: "06"
slug: hint-ladder-cursor-hold-feedback-modes
status: approved
shadcn_initialized: false
preset: none
created: 2026-08-10
reviewed_at: 2026-08-10
primary_input: .planning/research/2026-08-10-ui-inspiration-missing-surfaces.md §0, §0.1, §2
constraint_basis: .planning/PLANNING-DIRECTIVES.md §4a
---

# Phase 6 — UI Design Contract: Hint Ladder, Cursor-Hold & Feedback Modes

> **This is the differentiator surface.** Everything the project claims — *the runtime,
> not a model, decides what reaches the learner* — is either legible in the visible-lock
> hint card or it is a sentence in a README. Research §2 opens with exactly that framing:
> "The visible-lock card is the differentiator's entire UI surface." This document's job
> is to make the lock **structural and visible** rather than conversational.

## 0. Authority, legend, and what this document may not do

| Label | Meaning |
|---|---|
| **LOCKED** | Binding. Other phases build against it; a plan may not weaken it. Source is quoted at the point of use. |
| **DEFAULT** | This contract's decision, revisitable by a later phase with a recorded reason and equal-or-better accessibility/safety. |
| **BOTH** | Two defensible options, shipped behind one named setting per Directive §3. Not arbitrated. |
| **OPEN** | A real choice this phase may not settle. Implement a seam, never a learner-visible behaviour. |
| **REJECTED** | Recorded with the ground it actually stands on, so it is not re-proposed. |

**Authority order.** `REQUIREMENTS.md` / `ROADMAP.md` Phase 6 criteria → `06-CONTEXT.md` D-01…D-17
→ `.planning/UI-SPEC.md` (§7 copywriting and §8.1–8.9 accessibility gates are LOCKED)
→ this document → `.planning/research/2026-08-10-ui-inspiration-missing-surfaces.md` §2 recommendations.

**Citation discipline (Directive §4a):** *"Any rejection that names a Directive section quotes the
sentence it relies on. A citation that cannot be quoted is not a citation, and the finding it
supports is void."* Every "must" below quotes its source. Three constraints are explicitly **not**
invoked anywhere in this document because Directive §4a records that they do not exist: a no-JS
rule, a print veto, and a vendored-asset budget. Where the real reason is cost, taste, or churn,
this document says cost, taste, or churn.

**What this document may not do.** It may not change `.planning/UI-SPEC.md` §3's shell (activity
canvas + support column). It may not introduce a second scorer, parser, or evidence store
(Directive §4.2). It does not design the generated-hint panel — that is Phase 8 — but it **does**
lock the slot's shape and its absence rule, because a slot invented twice is a slot that disagrees
with itself.

---

## 1. Design System

| Property | Value |
|----------|-------|
| Tool | **None.** Python stdlib with embedded semantic HTML/CSS/vanilla JS. No shadcn, npm, CDN, registry, or third-party UI block. |
| Component approach | Reuse the shipped `surfaces/presentation.py` primitives: `surface_shell`, `context_line`, `teaching_step`, `details_section`, `state_panel`. Phase 6 adds exactly **one** new primitive, `hint_ladder`, and no second status region. |
| Palette source | `surfaces/theme.py` — **LOCKED** as the single palette source by `.planning/UI-SPEC.md` §7. Phase 6 introduces no hex value. |
| Voice/measure tokens | `surfaces/presentation.py` SHARED_CSS, per `.planning/UI-SPEC.md` §7.1. No surface names a font family literally. |
| Icon library | None. Callout kinds are distinguished by **structure + Ledger-voice label**, with any glyph `aria-hidden` and never the sole channel. |
| Font | Voice tokens only: `--font-paper`, `--font-ledger`, `--font-chrome`, `--font-code`. With no vendored face present these resolve to the shipped stacks and render byte-for-byte today's look. |
| Motion | 150ms maximum functional transition. `prefers-reduced-motion: reduce` removes it. **No motion on tier arrival** (see §6.4). |

### 1.1 shadcn gate — resolved, not asked

`components.json` is absent and the stack is Python + `http.server`, not React/Next/Vite, so the
shadcn initialization gate does not apply. Recorded rather than asked, per Directive §2: *"Do not
stop a planning session to ask a question you can answer from the codebase, the research
artifacts, or a defensible default. Record the assumption and continue."*

---

## 2. Spacing Scale

**LOCKED** — inherited unchanged from `.planning/UI-SPEC.md` §7. Phase 6 adds no value.

| Token | Value | Usage in this phase |
|-------|-------|---------------------|
| `space-1` | 4px | Tier-header label to rule gap; chip inline padding |
| `space-2` | 8px | Tier card internal line spacing; ladder rail item gap on narrow |
| `space-3` | 16px | Tier card padding (shown **and** locked — see below); status region padding |
| `space-4` | 24px | Gap between the ladder and the stumped control |
| `space-5` | 32px | Gap between the ladder block and the agent-support block |
| `space-6` | 48px | Support-column top offset on desktop |
| `space-7` | 64px | Report-section separation on the depth-readout surface |

**Exceptions:**

1. **44px minimum interactive target** for `I'm stumped — show the next hint`, `Check answer`,
   and every disclosure summary in this phase. This is a target-size floor, not a spacing token.
2. **A locked tier card uses the identical `space-3` padding and the identical box metrics as a
   shown tier card. — LOCKED.** The lock is expressed by border style and copy, never by making
   the card smaller, denser, or dimmer. A visually shrunken lock reads as *less important*; the
   whole point is that it is the most important object on the screen. It also means unlocking a
   tier causes **no reflow of the rail**, which matters because reflow-on-state-change is exactly
   what makes a gate feel like a trick.

---

## 3. Typography

**LOCKED** — the four-size / two-weight system from `.planning/UI-SPEC.md` §7. `text-lesson`
(18/1.65) is scoped to sustained authored lesson prose and is **not** used by any Phase 6 surface;
tier 0 is a lesson *pointer*, not lesson prose.

| Role | Token | Size | Weight | Line height | Phase 6 use |
|------|-------|------|--------|-------------|-------------|
| Label | `text-xs` | 12px | 400 | 1.4 | Tier headers, unlock-condition lines, mode chip, provenance, duration lines |
| Body | `text-body` | 16px | 400 | 1.5 | Item stem, options, authored hint bodies, status copy |
| Heading | `text-heading` | 20px | 700 | 1.2 | `Hints` section heading; report section headings |
| Display | `text-display` | 32px | 1.1 | 700 | Report page heading only. **Never** used for a verdict. |

Exactly two weights: 400 and 700. No semibold tier. Hierarchy comes from structure and space.

### 3.1 Voice assignment — LOCKED, and this is where B7 bites

Voice is assigned by **who authored the string**, never by visual preference
(`.planning/UI-SPEC.md` §7.3: *"A new surface that cannot say which of the four voices a string
belongs to has found a spec gap, not a free choice."*).

| String | Voice | Why |
|---|---|---|
| Item stem, options, and the **body** of tiers 2–5 (trap, picked-option rationale, discriminator, reveal) | `--font-paper` | A human author wrote them into the bank. |
| Tier header (`TIER 2 · trap`), locked-tier unlock condition, unavailable-tier notice, mode chip, verdict string, duration line, evidence/attempt counts, depth-readout table | `--font-ledger` | These are claims **the runtime guarantees**. The dashed lock plus the Ledger label is the visual signature of "the runtime holds the key." |
| `I'm stumped — show the next hint`, `Check answer`, disclosure summaries, form labels, settings | `--font-chrome` | The tool speaking about itself. |
| The learner's echoed canonical response; tier-0's slug/anchor identifier | `--font-code` | The machine's own representation. |
| **A generated hint or a model-suggested mark (Phase 8)** | `--font-chrome`, **inside a labelled container** | See §3.2. |

### 3.2 A model gets no typographic voice of its own — LOCKED (B7)

`.planning/UI-SPEC.md` §7.2 item 3, quoted: *"It carries **no typographic voice of its own**.
Generated text renders in **Chrome voice** inside the already-specified 'Generated synthesis'
labeled container. Paper voice is the author's; Ledger voice is the runtime's. A model gets
neither — it is a guest, and the label plus the container say so."*

Binding consequences for Phase 6, even though Phase 6 ships no model:

1. The generated-support slot in the support column renders in **Chrome voice inside a container
   whose visible label names it as generated**. Never Ledger. Never Paper. Never a voice invented
   for it. Research §0.1 B7's reasoning is the one to keep in the plan: *"A model that gets its own
   face is a model that looks like an authority."*
2. **A generated hint never occupies a numbered tier card.** The authored ladder's six numbered
   cards are the runtime's structure; a generated augmentation sits *beneath* the ladder in its own
   labelled container and carries the tier it was granted as a Ledger-voice provenance line
   (`granted at tier 2 · generated`). If a model's output could take a tier's slot, the ladder
   would stop being a record of authored content.
3. **Phase 6 renders no empty generated container.** With no model configured — which is every
   Phase 6 sitting — the slot is **absent with a stated reason**, per `.planning/UI-SPEC.md` §8.9:
   *"Run/model-only actions become explicit unavailable controls; do not render a disabled button
   with no reason."*

---

## 4. Color

**LOCKED** — 60/30/10 inherited from `.planning/UI-SPEC.md` §7. `surfaces/theme.py` derives every
value; Phase 6 introduces no hex.

| Role | Token | Usage in this phase |
|------|-------|---------------------|
| Dominant (60%) | `--bg`, `--ink` | Page field, activity canvas, primary text |
| Secondary (30%) | `--card`, `--chip`, `--line` | `--card` = a **shown** tier card. `--chip` = a **locked** tier card. `--line` = every tier border, solid when shown and **dashed when locked**. |
| Accent (10%) | `--accent`, `--accent-soft` | Focus rings; the single primary action `Check answer`; the current nav item. |
| Semantic | `--ok`, `--bad`, `--warn`, `--unknown`, `--pending` | See the reservations below. |

**Accent is reserved for exactly:** (1) the 2px focus outline with offset; (2) the one primary
submit control per view (`Check answer` / `Run code` / `Check response`); (3) the current/selected
navigational item in the global nav. **Nothing else.**

### 4.1 What accent and semantic tokens may never touch here — LOCKED

| Element | Forbidden token | Ground |
|---|---|---|
| `I'm stumped — show the next hint` | `--accent`, `--bad`, `--warn` | `.planning/UI-SPEC.md` §4 `HintLadder`: *"'I'm stumped — show next hint' is a normal button, not a warning."* It is a legitimate learning action (D-05), not an escape hatch and not a failure. |
| Locked tier card | `--bad`, `--warn`, `--accent` | A lock is **not an error and not a hazard**. It is ordinary runtime state. Using a warning token would say the learner did something wrong by being on tier 1 of 6. `--chip` + dashed `--line` only. |
| Unavailable tier card (D-08, authored content missing) | `--bad`, `--warn` | The item's author omitted a trap; the learner did nothing. `--unknown` + `--unknown-bg` with its text label, per §7's never-colour-alone rule. |
| Pending manual-review response | `--ok`, `--bad`, any number, any fraction, any check or cross glyph | `.planning/UI-SPEC.md` §7.2 items 1–2. `--pending` + its text label only. |
| Any tier card | `--ok` / `--bad` | A hint is not a verdict. Verdict colour lives only in the status region, and only in modes where a verdict is legal (§6.2). |

**Never colour alone — LOCKED.** Every state above carries a visible text label. Research §2.1
rejects Anki's four coloured grade buttons on exactly this ground: *"four coloured buttons is
meaning-by-colour and a UI-SPEC §7 violation, and it trains the learner to read colour as verdict,
which is precisely what the `--pending` surface must not do."*

---

## 5. The visible-lock card — the centre of gravity

### 5.1 The anti-pattern this rejects, first

**REJECTED — naked Socratic dialogue as the refusal surface.** Research §2.1, quoted: *"Reject
naked Socratic dialogue as the refusal surface. Its top documented complaint is that a learner who
wants help gets a question. The refusal must be **structural and visible**, not conversational — a
card that says a tier is locked, not a tutor that declines. This is the single strongest
anti-pattern in the whole landscape."*

This is not only a usability finding. A refusal rendered as *model reluctance* misattributes the
decision, and Directive §4.1 is: *"The **runtime**, not a model, decides what reaches the
learner."* A first-person "I'd rather you tried again first" says a personality chose. A dashed
card saying `Tier 3 unlocks after another attempt` says the rule chose. Only the second one is
true, and only the second one survives a learner arguing with it.

ROADMAP Phase 6 criterion 8 states the same conclusion as a success criterion: *"A locked tier is
*visible runtime state*, never first-person model reluctance: the UI says 'Tier 3 unlocks after
another attempt' in a dashed-border locked card."*

### 5.2 Locked tier card — rendering contract, LOCKED

```
┌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┐
╎ TIER 2 · TRAP                           ╎   ← --font-ledger, text-xs, letter-spaced
╎                                         ╎
╎ Tier 2 unlocks after another attempt.   ╎   ← --font-ledger, text-xs
╎ Or unlock it now with "I'm stumped".    ╎   ← --font-ledger, text-xs
└╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┘
   background: var(--chip)
   border: 1px dashed var(--line)
   border-radius: var(--r-2)
   padding: space-3   (identical to a shown card — §2 exception 2)
```

| Property | Value | Status |
|---|---|---|
| Container | `<li>` inside the ladder `<ol>`; **not** a button, **not** focusable, **not** `aria-disabled` | LOCKED |
| Background | `--chip` | LOCKED |
| Border | `1px dashed var(--line)` | LOCKED |
| Header | `TIER {n} · {fixed tier name}` in Ledger voice | LOCKED |
| Body | The unlock condition **only** — see §5.3 copy table | LOCKED |
| DOM contents | Header + unlock condition. **Nothing else.** No hint body, no availability flag, no `title`, no `aria-label`, no CSS-off text, no data attribute carrying content. | LOCKED |

**No-leak rule — LOCKED.** `.planning/UI-SPEC.md` §11.1 requires a *"fixture asserts no key,
unshown tier, accepted visual target, expected code output, or diagnostic/exam verdict is present
in HTML, JSON, ARIA, CSS-off text, or accessible names before legal disclosure."* §4 `HintLadder`
restates it: *"Hidden tiers have no DOM text/ARIA label."*

**Availability is disclosed only at the moment a tier is shown. — LOCKED, and this is a new call
this document makes.** D-08 says a missing authored tier produces an explicit *unavailable* tier
that keeps its numbered slot. It is tempting to render `TIER 2 · trap — unavailable` while still
locked. **Do not.** Whether this item has an authored trap is undisclosed authored state, and
learning it early is a weak but real signal about the item's distractor design. A locked card
therefore shows number + fixed tier name + unlock condition, and nothing about whether content
exists behind it. The unavailable state appears the instant the tier is shown, never before.

### 5.3 Locked-tier copy — LOCKED

The copy must name **what** unlocks the tier and **when**, so the learner can read the rule instead
of negotiating with a personality. There are exactly two unlock paths (D-05: *"Each genuine wrong
attempt can unlock at most one additional tier … Practice mode also exposes an explicit **stumped**
action"*), so the copy names both, and only where both are actually available.

| Card position | Copy (Ledger voice) | Note |
|---|---|---|
| The **next** locked tier | `Tier {n} unlocks after another attempt.` <br> `Or unlock it now with "I'm stumped".` | Line 1 is ROADMAP criterion 8's string verbatim. Line 2 is the second true path; omitting it would make the rule look stricter than it is, which is its own dishonesty. |
| Any **further** locked tier | `Tier {n} unlocks after tier {n-1}.` | Truthful and terse. The stumped control unlocks exactly one tier, so promising it here would be false. |
| Tier 5 while locked | `Tier 5 unlocks after tier 4.` — same rule, no special language | The reveal gets no dramatic framing. Calling it out invites treating the ladder as a countdown to the answer. |

Two things the locked card never says: **no first person** (no "I", no "let's", no "I'd like you
to"), and **no encouragement** (no "you're close", no "keep going"). Both convert a rule into a
personality, which is the §5.1 anti-pattern arriving through the copy door.

### 5.4 Shown tier card

```
┌─────────────────────────────────────────┐
│ TIER 1 · OBJECTIVE                      │  ← --font-ledger, text-xs
│                                         │
│ Distinguish OPA from NPA by level of    │  ← --font-paper, text-body
│ consciousness and gag reflex.           │
└─────────────────────────────────────────┘
   background: var(--card); border: 1px solid var(--line)
```

Tier 0 is a **pointer**, not prose: `TIER 0 · LESSON` header, then a Chrome-voice link
`Read: Airway adjuncts` whose slug renders in Code voice. Phase 6 does not parse or inline lesson
text — 06-01's key_links already bind this (*"tier 0 returns the existing renderer-neutral lesson
pointer; Phase 6 does not parse lesson text"*).

Tier 3 is response-specific (D-09). Its header carries the fact in Ledger voice:
`TIER 3 · RATIONALE FOR B`. Changing the answer changes the tier-3 payload but **never erases a
previously shown card** — earlier tier-3 cards stay in the rail with their own option letter, which
is what makes the rail a record rather than a display.

### 5.5 Unavailable tier card (D-08)

```
┌─────────────────────────────────────────┐
│ TIER 2 · TRAP                           │
│ This item has no authored trap.          │  ← --font-ledger, --unknown + label
└─────────────────────────────────────────┘
```

**LOCKED:** it keeps its numbered slot and later content never slides into it. Research and D-08
agree; the anti-pattern in `06-RESEARCH.md` is explicit: *"Tier content slides into an earlier
missing tier: missing authored content becomes accidental answer leakage."* Colour is `--unknown`
paired with the sentence — never colour alone, never `--warn`.

---

## 6. Layout, states, and the three lines every element carries

Per research §0.1, every element below names `keyboard/SR:`, `print:`, and `degraded:`.

### 6.1 Hint ladder placement — BOTH, behind `hint_display`

Directive §3, quoted: *"When two designs both look defensible and neither is clearly wrong, **do
not arbitrate**. Implement both behind one interface and make the choice a setting."*

| Setting | Value | Renders | Default |
|---|---|---|---|
| `hint_display` | `rail` | Research **§2.3 Option H1** — vertical stack of all six tier cards in the support column | **≥768px** |
| `hint_display` | `slot` | Research **§2.3 Option H2** — most recent shown tier as one card, earlier shown tiers behind `<details>` labelled `Hints shown (2)`, plus the next locked card and the next legal action | **<768px** |

**Reason for the picks, citing the option labels.** H1 is the recommended default because it is the
only option in which *the learner sees the whole shape of the ladder at once*, and research §2 is
unambiguous that this is the differentiator: *"the structural lock differentiates only if the
learner can see that it is structural."* H1's named cost is real — "on tier 1 of 6 [it] can read as
a long road" — and §6.2's `hint_locked_preview` setting is the answer to it rather than a reason to
drop H1. H2 is not a fallback; it is *better* at 375px and it is the right answer if the ladder ever
grows past six tiers. Both render the same server-side payload with different CSS and one
`<details>` wrapper, so this is one component with a variant, not a fork.

`keyboard/SR:` the ladder is an `<ol>` in the support column, after the activity in DOM order per
`.planning/UI-SPEC.md` §3; each shown tier is a plain list item with a real heading; locked items
are non-focusable and carry no hidden text; the stumped control is a normal `<button>` in a
`<form method="post">`. In `slot`, `<details>`/`<summary>` is natively operable and announces its
own state. Tier arrival is announced **once** through the single existing `role=status` region
(`presentation.state_panel`), with **no focus jump** — §8.3: *"After submit, keep focus on
submitted control unless an error needs focus; status is announced without a focus jump."*

`print:` shown tiers print with their bodies; **locked tiers print as their visible locked text**;
in `slot`, the `<details>` is forced open. A printed page is a record of a sitting, and "tier 3 was
never unlocked" is part of that record.

`degraded:` shown tiers are server-rendered and the stumped control is a form POST, so the whole
ladder is operable before any script loads and over a flaky link. With the **model** unreachable or
out of credits the authored ladder is untouched — this is `CLAUDE.md:57`'s requirement that *"the
core loop must **degrade, never block**"* — and the generated slot is absent with the LOCKED string
in §7.

**REJECTED — Option H3, inline-under-the-item stack.** Ground: it puts hint content inside the
activity canvas, which `.planning/UI-SPEC.md` §3 reserves for the active task and whose support
column is where `hints` contractually live. Research §2.3 states the disposition plainly: *"Do not
ship H3 without changing UI-SPEC §3, which is out of scope for a Phase 6 UI-SPEC."* Recorded as
blocked on a shell decision, not as a bad idea.

### 6.2 How much of the ladder to preview — BOTH, behind `hint_locked_preview`

The one place research §2.3 names a genuine cost with no verdict ("also sees how far they have to
go, which on tier 1 of 6 can read as a long road"). Directive §2 says decide and record rather than
ask, and Directive §3 says ship both rather than arbitrate.

| Setting | Value | Renders | Default |
|---|---|---|---|
| `hint_locked_preview` | `full` | All remaining locked tiers, each with its unlock condition | **yes** |
| `hint_locked_preview` | `next` | Only the next locked tier, plus a Ledger-voice count line `3 more tiers after this one.` | |

`full` is the default because the whole shape *is* the differentiator, and because the count line in
`next` is a strictly weaker version of the same information. `next` exists for the learner who finds
six cards discouraging, and it remains honest: the count is stated, so nothing is concealed.

`keyboard/SR:` identical DOM in both; `next` renders fewer `<li>`s and one extra Ledger line. `print:`
`full` prints every locked card; `next` prints the count line. `degraded:` server-rendered.

### 6.3 Wireframes

**Desktop, `hint_display: rail`, practice mode, held after one wrong attempt**

```
┌ ContextLine ──────────────────────────────────────────────────────────────┐
│ EMT › Airway · OPA indications · 3 / 8 · Practice · [Details]              │
├───────────────────────────────────────┬───────────────────────────────────┤
│ [A] ActivityCanvas                    │ [B] Contextual support            │
│                                       │                                   │
│ Which airway adjunct is indicated?    │  Hints                            │
│ ( ) A  ( ) B  ( ) C  ( ) D            │  ┌─ TIER 0 · LESSON ───────────┐  │
│                                       │  │ Read: Airway adjuncts       │  │
│ [Check answer]                        │  └─────────────────────────────┘  │
│                                       │  ┌╌ TIER 1 · OBJECTIVE ╌╌╌╌╌╌╌┐  │
│ ┌ status (role=status, reserved) ───┐ │  ╎ Tier 1 unlocks after       ╎  │
│ │ Not correct. Try a different      │ │  ╎ another attempt.            ╎  │
│ │ answer, or open the next hint.    │ │  ╎ Or unlock it now with       ╎  │
│ └───────────────────────────────────┘ │  ╎ "I'm stumped".              ╎  │
│                                       │  └╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┘  │
│ [D] Evidence disclosure               │  ┌╌ TIER 2 · TRAP ╌╌╌╌╌╌╌╌╌╌╌╌┐  │
│                                       │  ╎ Tier 2 unlocks after tier 1.╎  │
│                                       │  └╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┘  │
│                                       │  … tiers 3, 4, 5 same form …     │
│                                       │                                   │
│                                       │  [I'm stumped — show the next     │
│                                       │   hint]                           │
└───────────────────────────────────────┴───────────────────────────────────┘
```

`[A]` is the focus landing point and never loses focus on an ordinary submit. `[B]` follows `[A]`
in DOM order. There is exactly **one** `role=status` region and it lives in `[A]`.

**Narrow (<768px), `hint_display: slot`**

```
EMT › Airway · 3 / 8 · Practice
Which airway adjunct is indicated?
( ) A  ( ) B  ( ) C  ( ) D
[Check answer]
┌ status ───────────────────────────────┐
│ Not correct. Try a different answer,  │
│ or open the next hint.                │
└───────────────────────────────────────┘

Hints
┌─ TIER 1 · OBJECTIVE ──────────────────┐
│ Distinguish OPA from NPA by level of  │
│ consciousness and gag reflex.         │
└───────────────────────────────────────┘
▸ Hints shown (2)
┌╌ TIER 2 · TRAP ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┐
╎ Tier 2 unlocks after another attempt.╎
╎ Or unlock it now with "I'm stumped". ╎
└╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌┘
[I'm stumped — show the next hint]
```

### 6.4 Motion, and why tier arrival gets none — LOCKED

`.planning/UI-SPEC.md` §2.5, quoted: *"No points, badges, levels, streak-recovery prompts,
countdown pressure, or celebratory motion."* A new tier card therefore appears with **no entrance
animation, no highlight pulse, and no scroll-into-view**. Research §2.1 records the same rejection
against Brilliant: *"Reject celebration motion and the branching progress map. LOCKED §2.5.
Brilliant spends its motion budget on exactly what our contract bans."* The announcement is one
`role=status` update. The 150ms functional-transition budget in §1 is available for focus and
disclosure states, not for tier arrival.

### 6.5 The four feedback modes — state and copy

| Mode | Activity canvas | Support column | Ladder |
|---|---|---|---|
| **Drill** (D-10) | Verdict, then the correct answer and explanation immediately, then advance | Ladder block **absent with a stated reason** | Does not run |
| **Practice** (D-11) | Verdict + held cursor; the learner's answer stays visible adjacent to the feedback | Full ladder + stumped control | Runs |
| **Diagnostic** (D-12) | Recording acknowledgement, no verdict, no answer, no explanation | Ladder block **absent with a stated reason** | Does not run |
| **Exam** (D-13) | Recording acknowledgement, no verdict | Ladder block **absent with a stated reason** | Does not run |

**"Absent with a stated reason", never a rail of greyed cards. — LOCKED.** `.planning/UI-SPEC.md`
§8.9: *"Run/model-only actions become explicit unavailable controls; do not render a disabled
button with no reason."* A row of dimmed tier cards in exam mode would also be a §11.1 hazard for
no gain — the tier names would be in the DOM of a sitting where no tier can ever be legal.

**Mode is immutable per sitting (D-14).** The context-line mode chip is Ledger voice and is not a
control. There is **no mid-sitting mode switcher** anywhere in the UI. Starting another sitting is
the reversible path, and the settings surface says so.

**Exam-sim preset (ROADMAP criterion 9).** The context-line chip reads `Exam sim`; every
withholding rule is exam-mode's, unchanged. It is a preset over one command, not a fifth mode, and
it introduces no new UI state.

`keyboard/SR:` the mode chip is plain text inside the `<header>`; screen readers receive the mode
name with the rest of the context line. `print:` the mode prints — an attempt record without its
mode is unreadable evidence. `degraded:` mode is persisted in the session file and is available
before any script runs.

### 6.6 What the ladder must never render — LOCKED

**A recorded skip is not a hint event.** ROADMAP criterion 10, quoted: *"a skipped gate advances
the *reading position* and never the *hint tier*, and skipping is not an attempt. A `gate_skip`
event and a hint-tier advance are different events about different things."* Therefore: **the hint
ladder renders no skip, no skip count, and no skip-derived state**, and a `gate_skip` never
produces a tier card. Phase 6.2 owns the skip control's own rendering and its `Read ahead without
answering` copy; that copy is inherited, not locked here.

---

## 7. Copywriting Contract

Rows marked **LOCKED (inherited)** are reproduced verbatim from `.planning/UI-SPEC.md` §7 and were
neither edited nor re-voiced. Rows marked **LOCKED (new)** are settled by this document and other
phases build against them. Rows marked **DEFAULT** are revisitable.

| Element | Copy | Voice | Status |
|---|---|---|---|
| Primary CTA (submit) | `Check answer` (type-specific: `Run code`, `Check response`) | Chrome | LOCKED (inherited) |
| Hint CTA | `I'm stumped — show the next hint` | Chrome | LOCKED (inherited) — §7: *"LOCKED Phase 6 wording"* |
| Next locked tier | `Tier {n} unlocks after another attempt.` / `Or unlock it now with "I'm stumped".` | Ledger | LOCKED (new) — line 1 is ROADMAP criterion 8 verbatim |
| Further locked tier | `Tier {n} unlocks after tier {n-1}.` | Ledger | LOCKED (new) |
| `hint_locked_preview: next` count line | `{k} more tiers after this one.` | Ledger | DEFAULT |
| Shown tier header | `TIER {n} · {LESSON\|OBJECTIVE\|TRAP\|RATIONALE FOR {letter}\|DISCRIMINATOR\|REVEAL}` | Ledger | LOCKED (new) |
| Unavailable tier (D-08) | `This item has no authored {trap\|discriminator\|…}.` | Ledger | LOCKED (new) |
| Practice wrong, tier available | `Not correct. Try a different answer, or open the next hint.` | Ledger | DEFAULT |
| Practice wrong, tier 5 already shown | `The answer is shown above. Move on when you're ready.` | Ledger | DEFAULT |
| **Duplicate resubmission** (D-04) | `That is the same answer as before. Change it, or use "I'm stumped" to open the next hint.` | Ledger | LOCKED (new) — acceptance scenario 5 requires *"Duplicate/empty retry says what is required without tier advancement"* |
| **Empty submission** (D-04) | `Enter an answer before checking. An empty answer does not open a hint.` | Ledger | LOCKED (new) |
| Drill, ladder absent | `Drill mode shows the answer straight away. The hint ladder does not run here.` | Ledger | LOCKED (new) |
| Diagnostic, during sitting | `Diagnostic mode records your answers and shows nothing until the sitting ends.` | Ledger | LOCKED (new) |
| Diagnostic, at completion | `The sitting is complete. Here is the review.` | Ledger | DEFAULT |
| Exam, during sitting | `Exam mode holds all feedback until this attempt has been marked.` | Ledger | LOCKED (new) — D-13: reaching the last item is **not** the release condition, and the copy must not imply it is |
| Pending manual review | `A review is pending. This attempt counts as work, not as mastery yet.` | Ledger | LOCKED (inherited) |
| Model unavailable | `Generated help is unavailable. You can keep learning with the lesson and authored hints.` | Ledger | LOCKED (inherited) |
| Policy-blocked model output | `Generated help is unavailable for this step. Continue with the available hint or try another attempt.` | Ledger | LOCKED (inherited) |
| Recorded duration (the record) | `Time on this attempt: {d} (recorded by the runtime, from served to submitted).` | Ledger | LOCKED (new) — §7.1 |
| Duration unavailable (offline build) | `Time not recorded — this sitting was taken from an offline file.` | Ledger | LOCKED (new) — §7.1 |
| Client-measured latency, when shown | `First input after {d}, measured in this browser. Not recorded for every client.` | **Chrome, in a labelled container** | LOCKED (new) — §7.1 |
| Depth readout denominator | `Of {n} correct responses in modes where the ladder runs` | Ledger | LOCKED (new) — ROADMAP criterion 11 |
| No destructive action | *(none)* | — | Phase 6 has no destructive or irreversible learner action. There is nothing to confirm, and inventing a confirmation would make the stumped control feel like a transgression, which §4.1 forbids. |

### 7.1 The duration ruling — LOCKED, and it binds every surface that shows a time

Research §2.2's ruling, quoted: *"any surface displaying a duration must say which of the two it is
showing, and must never present a nullable client field as the record. A report that quietly falls
back from one to the other has invented a number."*

**This maps onto fields the repo already ships**, which the plans should know before they estimate:
`surfaces/session.py` writes `served_ts` into the session on serve and computes
`response_time_ms = ms_since(served_ts)` on submit. Both ends are server-side. **`response_time_ms`
is already the record**, in all three clients, and ROADMAP criterion 7 is therefore mostly a matter
of not breaking it.

| Field | Provenance | Nullable | Voice | Is it the record? |
|---|---|---|---|---|
| `response_time_ms` | Server-side: `received` minus `served_ts`. Present in browser, CLI, and daemon paths today. | Only on the offline static build (§7.1c) | Ledger | **Yes** |
| `item_elapsed_ms` | Server-side: `received` minus the item's **first** serve in this session, across the whole cursor hold | No | Ledger | **Yes** — a second record, not a substitute |
| `first_input_ms` | **Client-measured.** Time from render to first keystroke/selection. | **Yes, explicitly** | Chrome, in a labelled container | **No** |

Three consequences, each binding:

**(a) The hold makes `response_time_ms` ambiguous, so both readings are recorded. — LOCKED.**
Before Phase 6 the cursor always advanced, so "since served" and "since first served" were the same
number. A held cursor separates them, and both are defensible: per-attempt duration answers "how
long did this attempt take", cumulative answers "how long did this item cost". Directive §2 names
*"an append-only evidence field"* as a stop condition, and the way to satisfy it **without stopping**
is to write both — strictly more information, foreclosing nothing, no ambiguity to resolve later.
`response_time_ms` keeps its existing meaning (since the **latest** serve/re-serve, so it is
re-stamped when a held item is re-rendered); `item_elapsed_ms` is new and is never re-stamped.
Any surface showing either **names which one it is showing**.

**(b) `first_input_ms` has no Ledger voice, and that is the correct outcome.** Research §2.2:
*"there is no voice available for a claim the browser makes, and that is the correct outcome."*
It therefore renders exactly like a model suggestion does — Chrome voice inside a labelled
container — for exactly the same reason: the runtime does not guarantee it. It is off by default
(`latency_display: record`, §8) and it is **never** substituted for a missing record.

**(c) The offline static build records no serve time, and says so.** `itembank build` produces a
file with no daemon and no `served_ts`. A client-measured elapsed value must **not** be written into
`response_time_ms` — that would put a browser's claim into the runtime's field, which is the exact
failure §2.2 names. The field is `null`, and any surface showing it prints the stated-reason string
in §7. This is `.planning/UI-SPEC.md` §2.7: *"they never fake an answer, confidence, score, or model
result."*

**(d) No running timer, anywhere in the learning workspace. — LOCKED.** A visible per-item clock is
countdown pressure, and §2.5 bans *"countdown pressure"* by name. Durations appear on the report
surface and in the evidence disclosure, never beside an active item.

### 7.2 Depth-distribution readout (ROADMAP criterion 11) — BOTH, behind `depth_readout`

| Setting | Value | Renders | Default |
|---|---|---|---|
| `depth_readout` | `table` | Research **§2.5 Option D1** — a plain `<table>`, rows are tiers, columns are count and share, denominator stated in words above it | **yes** |
| `depth_readout` | `table+bar` | Research **§2.5 Option D2** — the same table with one CSS-only labelled bar above it | |

Reason for the picks: D1 is "boring and unimpeachable — nothing about it can be read as a score
about the learner", which is the property criterion 11 exists to protect. D2 is genuinely easier to
read and it is the shape that reveals the failure this measure exists to catch — *"a ladder nobody
climbs past tier 0"* — but research §2.5 warns *"a bar is one CSS change away from looking like
progress, and UI-SPEC §2.5 forbids progress framing."* So D2 ships with two conditions, both LOCKED:
the table is always beneath it, and **no segment renders as a fill against a 100% track**.

**Two copy rules, LOCKED:**
1. The denominator is stated **in words above the table**: `Of 84 correct responses in modes where
   the ladder runs`. A ratio with an unstated denominator is a number pretending to be a measure.
2. **This readout lives on the report surface and never in the learning workspace.** ROADMAP
   criterion 11: *"it is never shown to the learner with a target."* Research §2.5 sharpens it: *"A
   distribution shown next to an active item is a target no matter how it is worded."*

`keyboard/SR:` a real `<table>` with header cells; narrow viewport uses the labelled
horizontal-scroll wrapper §8 already requires. In `table+bar` the bar is decorative over the table
and is `aria-hidden`; the table is the accessible representation. `print:` the table prints
natively; the bar needs text labels inside each segment because print may drop backgrounds.
`degraded:` both are server-computed from live events; no client arithmetic.

---

## 8. Named settings (Directive §3 registrations)

Four settings, each a **registration behind one interface, not a fork** — the same server-side
payload rendered differently. Each lands in `itembank.json` under the existing settings schema with
an `x-itembank-phase: 6` marker, so `itembank config` reports it as inert until its reader ships.

| Setting | Values | Default | Interface | Research option |
|---|---|---|---|---|
| `hint_display` | `rail` \| `slot` | `rail` ≥768px, `slot` <768px | One `hint_ladder` component, one `<details>` wrapper, CSS class swap | §2.3 H1 / H2 |
| `hint_locked_preview` | `full` \| `next` | `full` | Same `<ol>`, fewer `<li>` + one count line | §2.3 H1's named cost |
| `depth_readout` | `table` \| `table+bar` | `table` | Same table, one optional `aria-hidden` bar above | §2.5 D1 / D2 |
| `latency_display` | `record` \| `record+client` | `record` | Same report row, one optional labelled Chrome-voice container | §2.2 |

**Where Directive §3 stops.** It stops *"when the two options need **two parsers, two scorers, or
two evidence stores**."* None of these four does — all four are renderer-side reads of one payload.
The one place this document **does** pick rather than ship both is §7.1(a)'s duration semantics, and
the reason is that it is an evidence-shape question rather than a rendering question; the resolution
there is to record both fields, which is the same instinct applied at the correct layer.

---

## 9. Payload additions this contract requires from 06-01 / 06-02

**This section exists because a plan must not discover a UI requirement at execution time.** None
of the following contradicts a written plan line; each is an **addition** that the plans' current
text does not cover, and each is named here so the planner can fold it in rather than the executor
inventing it.

| # | Addition | Which plan | Why the UI cannot proceed without it |
|---|---|---|---|
| A1 | The transition payload carries a **`ladder` array covering all six tiers**, each entry `{index, name, state: shown\|unlocked\|locked, unlock_condition}`, where `locked` entries carry **no body and no availability flag**. | 06-01 (runtime), 06-02 (payload passthrough) | 06-02 Task 3 currently says the browser *"renders only the returned progressive ladder"* — i.e. shown tiers. ROADMAP criterion 8 requires rendering **locked** tiers too. If the payload omits them, the browser must compute the ladder shape client-side, which would be a second policy engine and a Directive §4.1 violation. |
| A2 | `unlock_condition` is a **runtime-supplied enum** (`next_attempt_or_stumped`, `after_prior_tier`, `mode_ladder_absent`), not a client-side string table. | 06-01 | The locked-card copy is the differentiator's whole text. Three surfaces (CLI, API, browser) rendering it from three local string tables is how they drift apart. Copy strings map from the enum in one place. |
| A3 | `item_elapsed_ms` written on every response event alongside the existing `response_time_ms`; `response_time_ms` re-stamped on re-serve after a hold. | 06-01 Task 3 (`evidence.py`, `schemas/response.schema.json`) | ROADMAP criterion 7 is non-deferrable: *"The evidence log is append-only; a field not written now can never be backfilled."* §7.1(a). |
| A4 | `first_input_ms` present in the response schema as **explicitly nullable**, written only where a client measured it, never derived or defaulted. | 06-01 Task 3 | §7.1(b). Adding it later is impossible for every event already written. |
| A5 | `response_time_ms` is `null` on the offline static-build path, never a client-measured substitute. | 06-01 Task 3 / `surfaces/quiz.py` | §7.1(c). |
| A6 | The `report` payload carries the **depth distribution with its denominator**, computed server-side. | 06-01 Task 3 (`evidence.teaching_outcomes`) | ROADMAP criterion 11; §7.2. A client-computed share would be a second derivation of evidence. |

**Supersession:** none. No line of `06-01-PLAN.md` or `06-02-PLAN.md` is contradicted by this
document. A1 and A2 extend 06-02 Task 3's `must_haves` truth *"The ladder renders accumulated
returned tiers in fixed order, marks unavailable tiers honestly"* to also cover locked tiers;
A3–A6 extend 06-01 Task 3's evidence contract, which its own checkpoint (Task 1,
`checkpoint:decision`) is the correct place to confirm — that gate already exists precisely to fix
irreversible fields before the first append.

---

## 10. UI Considerations

State coverage for this phase's surfaces. Empty-state and error-state **copy** lives in §7; this
table covers state coverage and references those rows.

Applicable state considerations resolved: **11 covered, 2 backstop, 1 unresolved**

| Category | Element(s) | Status | Resolution / Reason |
|----------|------------|--------|---------------------|
| empty | hint ladder, first render before any attempt | ✅ covered | With no attempt yet the ladder block is absent entirely, not an empty rail — nothing has been unlocked and nothing is pending. The support column shows goal/prerequisite only. |
| empty | ladder in drill / diagnostic / exam | ✅ covered | Block absent with the stated reason from §7, never greyed cards (§6.5, UI-SPEC §8.9). |
| empty | generated-support slot with no model | ✅ covered | Slot absent with a stated reason; never an empty labelled box (§3.2 item 3). |
| loading | submit in flight | ✅ covered | The submit control is disabled **only while the request is in flight** (UI-SPEC §4 `AttemptPanel`); status region reads a static progress label, no looping animation. |
| error | duplicate resubmission | ✅ covered | §7 duplicate row; tier does not advance; focus stays on the submitted control. |
| error | empty submission | ✅ covered | §7 empty row; states what is required. |
| error | daemon unreachable mid-sitting | ✅ covered | `StatusNotice` with `role=alert` (action-blocking) plus a learner-initiated retry; the already-rendered ladder and stem stay readable. Degrade, never block (`CLAUDE.md:57`). |
| partial | manual-review `short` response pending | ✅ covered | `--pending` token + the LOCKED pending copy; not wrong, not correct, ladder does not advance (D-06). |
| partial | authored tier missing (D-08) | ✅ covered | Unavailable card in its own numbered slot (§5.5); availability disclosed only on show (§5.2). |
| overflow | ladder grows to six shown cards on a 375px viewport | ✅ covered | `hint_display: slot` is the <768px default; earlier tiers collapse behind `<details>` (§6.1). |
| long-text | a long tier-5 reveal or a long picked-option rationale | ✅ covered | Prose wraps at `--measure-prose`; no ellipsis, no clamp — a truncated hint is a hint that lies about its length. |
| zero-one-many | tier-3 cards across several different picked options | 🧪 backstop | Held-out UI-state test: three genuine attempts picking B, then C, then B again must leave three tier-3 cards each labelled with its own option letter, with none erased (D-09). |
| overflow | depth readout with a tier count of zero in some rows | 🧪 backstop | Held-out UI-state test: a distribution where tiers 3–5 are all zero must render as stated zeroes with the denominator, never as an omitted row or an empty bar segment. |
| long-text | context line at 375px with a long bank name, objective, and `Exam sim` chip | ⚠ unresolved | Planner treats as an assumption: the context line may wrap to two rows per UI-SPEC §3, but Phase 6 adds the mode chip to an already-full line and no fixture proves the two-row case at 375px. Verify in a responsive snapshot before completion. |

---

## 11. Required verification gates for this phase

Every browser-facing Phase 6 plan carries all six gates from `.planning/UI-SPEC.md` §11, plus the
four below which are specific to this surface.

1. **Locked-tier no-leak fixture.** Assert that for a practice item held at tier 1, the served HTML,
   the JSON payload, the accessibility tree, CSS-off text, `title` attributes, and every accessible
   name contain **none** of the item's trap, discriminator, per-option analysis, rationale, or key
   strings — built from the fixture bank rather than hard-coded. This is §11.1 applied to the exact
   object this phase invents.
2. **Locked-tier visible-text fixture.** Assert the locked card's rendered text is exactly the §7
   string for its position, that its computed border style is `dashed`, and that its background token
   is `--chip` and not `--warn`/`--bad`. Criterion 8 is a *visual* success criterion; a test that
   only checks the string would pass on a card styled as an error.
3. **Mode-absence fixture.** In drill, diagnostic, and exam, assert the ladder block is **absent**
   from the DOM (not hidden, not disabled) and that the stated-reason string is present.
4. **Duration provenance fixture.** Assert that `response_time_ms` and `item_elapsed_ms` are present
   and server-derived on the daemon path; that `first_input_ms` is absent or null and never
   populated server-side; that the offline build path writes `response_time_ms: null`; and that no
   rendered surface prints a client-measured value inside a Ledger-voice string.

---

## 12. Rejections recorded, each with the ground it actually stands on

| Rejected | Ground | Not the ground |
|---|---|---|
| Naked Socratic dialogue as the refusal surface | Research §2.1's strongest anti-pattern + Directive §4.1 — a conversational refusal misattributes the decision to a personality | Not "chat is bad"; a single-turn contextual diagnostic question after a granted tier remains legal (UI-SPEC §9) |
| Option H3, inline hint stack in the activity canvas | Requires a `.planning/UI-SPEC.md` §3 shell change; out of scope for a Phase 6 spec | Not a layout preference — H3 is genuinely the best narrow-viewport behaviour and is worth revisiting when the shell is next opened |
| Anki's four coloured grade buttons | UI-SPEC §7 never-colour-alone; trains colour-as-verdict, which `--pending` must not do | Not "self-rating is bad" — self-rating is legitimate where nothing is scored |
| Celebration motion, tier-arrival animation, progress framing on the ladder | UI-SPEC §2.5 LOCKED: *"No points, badges, levels, streak-recovery prompts, countdown pressure, or celebratory motion."* | — |
| Depth readout anywhere in the learning workspace | ROADMAP criterion 11: *"it is never shown to the learner with a target"* | — |
| A running per-item timer | UI-SPEC §2.5 bans *"countdown pressure"* | Not a claim that duration is unimportant — it is recorded on every event (§7.1) |
| Greyed/disabled ladder in non-practice modes | UI-SPEC §8.9: *"do not render a disabled button with no reason"*; plus a needless §11.1 surface | — |
| A generated hint occupying a numbered tier card | UI-SPEC §7.2 item 3 (B7) — a model gets no face and no slot in the runtime's structure | Not a claim generated hints are low value; they are Phase 8's whole point |
| Mid-sitting mode switcher | D-14 — evidence produced under one policy must not be relabelled as another | — |
| A confirmation dialog on `I'm stumped` | UI-SPEC §4: *"a normal button, not a warning"* — a confirmation would style a legitimate learning action as a transgression | — |

---

## 13. Open questions for a later phase

Named so they are revisited deliberately rather than rediscovered.

1. **OPEN — where the generated hint sits once Phase 8 ships.** This document locks that it is
   Chrome voice, in a labelled container, beneath the ladder, carrying its granted tier as Ledger
   provenance. It does **not** settle whether it is collapsed by default, nor what `suggestion_reveal:
   after-self-mark | on-request | never` renders at each value. Phase 8's UI-SPEC owns that, and
   research §2.4 (P1/P2/P3) is the option set.
2. **OPEN — whether `hint_display: rail` survives a seven-tier ladder.** Research §2.3 records that
   H2 *"is the right answer if the ladder ever grows past six tiers, and the wrong answer today."*
   The trigger is a seventh tier, not a date.
3. **OPEN — H3 and the shell.** If `.planning/UI-SPEC.md` §3 is ever reopened, H3's narrow-viewport
   advantage is the strongest argument on the table for revisiting where hints live.
4. **OPEN — no usability evidence exists for a visible-lock hint UI specifically.** Research §8
   records this honestly: the H1 rail *"rests on the structural argument … not on a measured
   comparison. Falsify at plan time with a UAT, not after building."* Phase 6's UAT should ask a
   learner to explain, unprompted, why tier 3 is not available. If they answer with a rule, the card
   works. If they answer with a personality, it does not.
5. **OPEN — `item_elapsed_ms` semantics across a resumed session.** If a learner resumes a held item
   the next day, cumulative elapsed includes the overnight gap. Recorded as an assumption
   (the number is honest but not comparable across resumes); Phase 10 owns whether pacing reads it
   raw or windowed.

---

## Registry Safety

| Registry | Blocks Used | Safety Gate |
|----------|-------------|-------------|
| None | None | Not applicable. This project uses no component registry, npm, CDN, or third-party UI block. No third-party registry was declared, so the `shadcn view` vetting gate has no input. |

## Checker Sign-Off

- [x] Dimension 1 Copywriting: PASS
- [x] Dimension 2 Visuals: PASS
- [x] Dimension 3 Color: PASS
- [x] Dimension 4 Typography: PASS
- [x] Dimension 5 Spacing: PASS
- [x] Dimension 6 Registry Safety: PASS

**Approval:** APPROVED — gsd-ui-checker, 2026-08-10. 6/6 dimensions PASS.
