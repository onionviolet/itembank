---
phase: 7
slug: selection-engine
status: approved
shadcn_initialized: false
preset: none
created: 2026-08-10
reviewed_at: 2026-08-10
inputs:
  - .planning/research/2026-08-10-ui-inspiration-missing-surfaces.md §0, §0.1, §4 (OPTION SET)
  - .planning/PLANNING-DIRECTIVES.md §2, §3, §4, §4a, §5
  - .planning/UI-SPEC.md (project-level; §7 copy and §8.1-9 gates LOCKED)
  - .planning/phases/07-selection-engine/07-CONTEXT.md (D-01..D-15)
  - .planning/phases/07-selection-engine/07-01..07-06-PLAN.md
  - .planning/ROADMAP.md § Phase 7 (11 success criteria)
supersedes:
  - "07-06-PLAN.md Task 2, render_trace paragraph — line ordering replaced by §3.2's locked grammar; header extended; ASCII-only added. Reason in §3.6."
extends:
  - "07-01-PLAN.md Task 2, trace shape paragraph — three additive fields. The plan itself sanctions this: 'Its shape, which every later plan extends rather than replaces'."
---

# Phase 7 — UI Design Contract: Selection Engine

> **The design goal is inspectability.** A selection decision rendered without its reason
> is an oracle, and an oracle deciding what the learner sits next is the same failure mode
> as a model deciding what reaches them. This phase is mostly headless; its entire visual
> surface is the trace. So the trace is the product.

---

## 0. Scope, and what this phase actually renders

| # | Element | Built in Phase 7? | Owner |
|---|---|---|---|
| E1 | `itembank select <bank> --explain` rendered trace (plain text, stdout) | **Yes** — 07-06 Task 2 | `surfaces/selection_cli.py:render_trace()` |
| E2 | Trace header block (mode, bank, evidence snapshot, notes, preview disclaimer) | **Yes** — 07-06 Task 2 | same |
| E3 | Per-item trace block — the four-line grammar (§3.2) | **Yes** | same |
| E4 | `POST /api/start` `"preview": true` → `trace` JSON | **Yes** — 07-06 Task 3 | `surfaces/daemon.py` |
| E5 | `Why this item?` `<details>` in the support column | **No — Phase 10** | contract locked here (§4) |
| E6 | Corpus-reach readout (ROADMAP crit. 10) | **computed** in 7, **rendered** in 10 | §6 |
| E7 | Persistent "why" workspace panel | **REJECTED** — research §4.4 S3 | never; see §8 |

**Option picks, with the reason and the label** (from research §4 — the option set; no new
survey was run, per instruction):

| Pick | Option | Reason |
|---|---|---|
| Trace shape | **§4.3 "the four-line trace"** | It is the narrow path between §4.1's two named failure modes: enough structure to be argued with, no number that implies measurement. |
| Layout | **§4.4 S1 — CLI-first, `<details>` on the web** | "One text artifact, two renderings, no divergence possible." Cheapest place to honour the project-wide CLI-twin rule. Cost **S**. |
| Variant | **§4.4 S2 — candidate table**, scoped to pair/blueprint cases only | Materially clearer where "why this over that" *is* the question; materially more surface otherwise. Registered, not defaulted. |
| Rejected | **§4.4 S3 — persistent "why" panel** | Rejection **stands**. Grounds: project `UI-SPEC.md:63` defers the full panel to Phase 10, and `UI-SPEC.md:607`/`:611` ("A mastery percentage, BKT/FSRS model, predictive learning analytics"; "model-driven selection") sit in §13 Do Not Build Yet. Recorded so the discuss step does not re-open it. |

---

## 1. Design System

| Property | Value |
|----------|-------|
| Tool | **none** — no shadcn, no npm, no component registry. Verified: no `components.json`, no `package.json`, no `tailwind.config.*` in the repo. |
| shadcn gate | **Not applicable.** The gate fires for React/Next/Vite stacks. This is stdlib Python emitting HTML/CSS (`.claude/CLAUDE.md` Technology Stack; project `UI-SPEC.md:309`). |
| Component approach | Native semantic HTML; `<details>`/`<summary>` for E5. No framework, no JS required for E5. |
| Palette source | `surfaces/theme.py` — **LOCKED** single palette source (project `UI-SPEC.md:317`). This phase adds **zero** palette entries. |
| Voice/measure tokens | `surfaces/presentation.py` SHARED_CSS. Verified **not yet shipped** — `--font-ledger`, `--measure-prose` etc. are specified in project `UI-SPEC.md` §7.1 (adopted 2026-08-10) but absent from `presentation.py` today. E5 is Phase 10 work and must consume the tokens, not literals. |
| Icon library | none. Callout kinds are distinguished by **icon + Ledger-voice label + structure** per §7.3; this phase uses **no icon at all** (§3.5). |
| Font | `--font-ledger` for the trace. Resolves to `ui-monospace, SFMono-Regular, Menlo, Consolas, monospace` when no face is vendored (§7.4 Ruling 1 unruled ⇒ not vendored ⇒ today's look, unchanged). |

**A property worth naming:** a terminal is monospace by construction, so **the CLI render *is*
Ledger voice natively.** That is the strongest argument for S1's CLI-first ordering — the
canonical artifact is produced in the medium whose default typography already encodes its
authority, and the web render is the one that has to work to match it.

---

## 2. Voice assignment — LOCKED

Voice is assigned by **who authored the string**, never by visual preference
(project `UI-SPEC.md:416`).

| String | Voice | Why |
|---|---|---|
| Every line of the trace — pool, strategy, comparison, invariant, notes | **Ledger** (`--font-ledger`) | The trace is runtime output about a deterministic decision. Research §4.5: *"The trace is runtime output about a deterministic decision, so it renders in Ledger voice."* Project `UI-SPEC.md:352` puts "evidence counts", "snapshot/session/write ids" and "gate outcomes" in Ledger. |
| Evidence snapshot marker, response counts, item `[ID:]` / `Qn` refs | **Ledger** | Same. Ids are Ledger by §7.1. |
| `Why this item?` summary text, `Start practice` button, form labels | **Chrome** (`--font-chrome`) | The tool speaking, not the runtime. |
| Item stem / options shown in a preview payload | **Paper** (`--font-paper`) | Authored content; arrives via `runtime.public_item()`. |
| A model paraphrase of a trace | **Chrome, inside a labelled container** — and the trace **does not move** | **B7, LOCKED.** Research §4.5: *"If a model ever paraphrases a trace for readability, that paraphrase is a separate, labelled, Chrome-voice object sitting next to the trace, and the trace does not move. A rationale a model rewrote is a rationale the runtime no longer guarantees."* |

**B7 in this phase, stated as a prohibition to inherit.** Phase 7 has no model at all — 07-CONTEXT
`<domain>` excludes "Model-assisted selection of any kind." So B7 costs nothing here and is
recorded *because Phase 8, 10 and 11 will be tempted*: a rationale sentence *feels* like generated
prose. It is not. Any surface that cannot say which of the four voices a trace string belongs to
has found a spec gap, not a free choice.

---

## 3. The trace — E1/E2/E3

### 3.1 The two failure modes this grammar exists to avoid

Restated from research §4.1 because every rule below is derived from them:

- **Black box.** "Recommended for you." Nothing inspectable.
- **Score theater.** "Priority 0.87." A number that looks like measurement, is the output of
  weights someone chose, and cannot be argued with. *Worse* than the black box, because it is a
  black box wearing a lab coat.

**The load-bearing rule — LOCKED:** *the trace names a field and a comparison, never a weight and
never a total.* `Q31 was served 2 days ago` is arguable. `Q31 scored 0.62` is not. Where a strategy
genuinely is numeric, it states **its input, not its output**. This is the single rule a Phase 10
weight will pull hardest against; it does not bend.

### 3.2 The four-line grammar — LOCKED

Every per-item block is exactly these lines, in this order. Lines 4 and 5 are conditional.

```
Q07  emt:airway:opa-indications                          [id 4f2a9c1e]
  1  Objective emt:airway:opa-indications, any type, any difficulty
     - 14 of 38 items in this bank matched.
  2  Ranked by: prerequisites you have already passed.
  3  Chosen over Q31. Q31 was served 2 days ago and is inside the
     20-response cooldown window; this item was last served 19 days ago.
  4  Pending marks were not read.
```

| Line | Name | Contract | Source |
|---|---|---|---|
| 0 | **Identity** | `Qn`, objective, and the opaque `[ID:]`. Identity is `[ID:]`, never the item number — numbers move when a bank is edited (07-CONTEXT canonical refs). | 07-01 trace block |
| 1 | **Filter and pool** | Every filter that was applied, in words, then `N of M items in this bank matched`. **M is stated** — a share without its denominator is not inspectable. | research §4.3 line 1 |
| 2 | **Strategy, by name** | `Ranked by: <strategy_label>` — the *human* label, never the machine id. | research §4.3 line 2; ROADMAP crit. 9 |
| 3 | **The one field that separated winner from runner-up** | Names the runner-up by `Qn`, then one field and one comparison. **Exactly one field.** A block that needs three fields to justify itself is a ranking nobody can argue with. | research §4.3 line 3; D-04/D-05 |
| 4 | **What was *not* used** | `Pending marks were not read.` — always present. | research §4.3 line 4; ROADMAP crit. 11 |
| 5 | **Override, if used** | Present *only* when the learner overrode the prerequisite fringe: `Prerequisites for this objective are not yet passed. You chose to work it anyway on YYYY-MM-DD.` | ROADMAP crit. 7 ("A learner may override, and the override is recorded") |

**Why line 4 is unconditional and not omitted when true.** ROADMAP criterion 11 makes
"a pending model-suggested mark influences selection in no way" a **selection-side invariant**, and
research §4.3 gives the reason it must be visible: *"an invariant nobody can see is an invariant
nobody maintains."* An invariant printed only when interesting is an invariant nobody audits.

**Why line 2 prints a label, not an id.** D-05 requires "plain terms, not rule ids", and ROADMAP
criterion 9 requires `select --explain` to name the strategy. Both are satisfiable at once:
**each registered strategy declares two strings** — `strategy_id` (machine, e.g.
`prerequisite-fringe`, used in the JSON trace and in settings) and `strategy_label` (human, e.g.
`prerequisites you have already passed`, used in every rendered line). The rendered text prints the
label; the JSON carries both. This is a gap fill, not an arbitration — see §7.

### 3.3 The header block — LOCKED

Printed once, above the blocks. 07-06 Task 2 already requires four of these five lines; the fifth
is added here.

```
Selection preview - selection_bank.md - practice mode
Evidence: _evidence/evidence.jsonl, 214 responses in this bank.
Note: every candidate was inside the cooldown window; the 4 oldest-seen
      items were readmitted in age order so the session is not empty.
Preview only - no session was started and nothing was recorded.
```

| Line | Contract |
|---|---|
| Header | selection mode, bank basename. Uses the **`--selection-mode`** vocabulary, never `--mode` (D-11: the two words are two axes and must not alias). |
| Evidence | log path and row count. **This is the snapshot the decision rested on** (D-09/D-10, TREND-05). |
| Notes | every `trace["notes"]` entry, verbatim. Degradation announces itself (§3.4). |
| **Preview disclaimer — new** | `Preview only - no session was started and nothing was recorded.` **Rationale:** 07-06 Task 2 makes the write-nothing property a hard truth, and 07-05 makes `itembank start` write for real. Two commands, one output shape, opposite consequences. An unlabelled preview is the one place this surface can mislead. Ledger voice — it is a claim about the filesystem the learner can check. |

### 3.4 `degraded:` — B2, LOCKED

**What "degraded" means on this surface:** the daemon or the evidence store is unavailable. The
trace **says exactly what is unavailable and never fakes a queue, a confidence, or a due count.**

| Condition | Rendered line | Never |
|---|---|---|
| No `_evidence/` directory | `No evidence store was found, so no item was excluded for recency.` (Ledger; `--unknown` token + this text in E5) | Never silently produce a recency-free ranking that *looks* history-aware. `trace.evidence.responses` is `0` and `source` is `none` — 07-05 already requires this. |
| sqlite3 index absent, JSONL present | `Read from the event log directly; the index was not available.` | Never omit the line — the two paths must be distinguishable when a result is questioned. |
| Every candidate inside the cooldown | The 07-05 readmission note, verbatim, in the header | Never return an empty session silently. |
| Daemon unreachable (E5 only) | The `<details>` renders from the **already-served** trace payload, or is **absent with a stated reason** — never an empty disclosure and never a disabled control with no reason (project §8.9). | Never a spinner. |
| Model unavailable | **No effect whatsoever, and the surface says nothing about it.** | The selector is rule-based (SEL-05, D-01). A model-status line here would imply the model had a vote. |

**Deliberately NOT reused: the LOCKED sparse-evidence copy.** Project `UI-SPEC.md:466` locks
`Not enough evidence to make a recommendation yet.` for the *recommendation* situation. A missing
evidence store here does **not** block selection — it removes cooldown and recency only, and the
selection still happens correctly. Borrowing the recommendation copy would overstate the failure.
Recorded so a checker does not read the divergence as a copy-contract breach.

### 3.5 Rendering rules for the CLI (E1) — LOCKED

1. **ASCII only.** No `·`, no `—`, no box-drawing. **Measured, not assumed:** on this machine
   (Python 3.13.5, Windows) `sys.stdout.encoding` is `cp1252`, not UTF-8, and a redirected
   `print('a · b — c')` writes cp1252 bytes with **exit code 0** — silent corruption for
   anything that pipes, diffs, or feeds the output to an agent. This **amends research §4.3's
   example lines**, which use `·`. Separators are ` - ` and `, `. Reason is robustness and cost,
   not taste.
2. **No ANSI colour, ever.** Not as a channel, not as decoration. Never-colour-alone (project §7)
   has no meaningful "alone" on a pipe.
3. **Structure by indentation, not by glyphs.** The runner-up is a continuation of line 3 under its
   winner. The winner/runner-up distinction is **structural + the word "over"** — never colour,
   never a symbol.
4. **No JSON, no braces, no field names.** 07-06 Task 2 acceptance already asserts no `{` or `}`.
5. **No tables in the CLI render.** A screen reader reading stdout gets a linear stream; column
   alignment becomes noise. The S2 table variant is an **HTML-only** variant (§4).
6. **Wrapping.** Wrap prose at 72 columns and indent continuations to the line's own indent.
   72 mirrors the project's LOCKED 72ch maximum readable measure (§8 Responsive).

`keyboard/SR:` stdout is linear text in reading order; no glyph carries meaning; no colour carries
meaning; every distinction is a word or an indent. Nothing on this surface is pointer-only because
nothing on it is a pointer target.
`print:` redirecting stdout to a file **is** the print form and it is byte-identical to the console
form (rule 1 is what makes that true).
`degraded:` §3.4.

### 3.6 What this supersedes, and why

**Superseded:** `07-06-PLAN.md` Task 2, the `render_trace` paragraph — *"each naming the item by
its `[ID:]` and its `Qn` reference, its objective, the sentence saying why it was chosen, and an
indented line naming the runner-up and why it lost."*

That is three lines. §3.2 locks five (two conditional). **Reason:** the plan predates ROADMAP
criteria 9 and 11 (round-two, research-derived). Criterion 9 requires the strategy be named;
criterion 11 requires the pending-mark invariant be a selection-side assertion. Neither has a home
in a three-line block. The plan's header requirement, its no-jargon requirement (D-05) and its
no-JSON requirement are **kept verbatim**; only the block grammar is replaced and the header gains
one line.

**Extended, not superseded:** `07-01-PLAN.md` Task 2's trace shape. The plan states its own
extension clause — *"Its shape, which every later plan extends rather than replaces"* — so the
following are additive and no field is removed:

| Added | Where | Serves |
|---|---|---|
| `pool: {"filters": [...], "matched": int, "bank_total": int}` | per block | line 1 |
| `strategy: {"id": str, "label": str}` | per block | line 2, ROADMAP crit. 9 |
| `invariants: [str]` | trace level | line 4, ROADMAP crit. 11 |
| `override: {...}` or `None` | per block | line 5, ROADMAP crit. 7 |

---

## 4. `Why this item?` on the web — E5, contract only

**Phase 7 does not build this.** Project `UI-SPEC.md:63` (plan 07-06 disposition):
*"CLI/API explanation is required; defer a full workspace panel to Phase 10, but contract-test copy
with a future `Why this item?` renderer."* The contract is locked here so Phase 10 transcribes it.

- Element: `<details>` in the **support column**, following the activity in DOM order
  (project §3 workspace rules, §6 `[B]`).
- Summary text: **`Why this item?`** — verbatim from the project wireframe at `UI-SPEC.md:243`.
  Chrome voice. Not re-invented here.
- Body: **the identical lines the CLI prints**, one `<pre>`-equivalent block per item, Ledger voice.
  One text artifact, two renderings — divergence is impossible by construction.
- Collapsed by default. Activity-first is LOCKED (project §2.1).
- **Never takes focus after an ordinary submit** (project §6 `[B]`).

`keyboard/SR:` `<details>`/`<summary>` is natively operable and announces its own open/closed state.
No JS required. Zero ARIA needed.
`print:` **forced open** — `details { display: block } summary { ... }` under `@media print`. A
printed sitting record should carry why each item was served (research §4.4 S1).
`degraded:` §3.4 row 4.

### 4.1 Withheld during diagnostic and exam sittings — LOCKED

In a live sitting whose **feedback mode** is `diagnostic` or `exam`, E5 is **not rendered and its
text is not in the DOM** until sitting completion.

**Reason, quoted:** project `UI-SPEC.md:187` — *"diagnostic has no correctness/hint/explanation
until sitting completion; exam holds feedback until accepted mark. The DOM/ARIA tree must not
contain concealed correctness information."* A trace is not correctness, but line 1 names the
objective and the filter, and on a discrimination pair (`[PAIR:]`, D-07) naming the objective
narrows the answer domain. The safe reading is cheap and the unsafe reading is a B4 leak; this is
not a case for building both.

**No contradiction with the plans:** `itembank select --explain` is a *preview* — 07-06 requires it
write no session — so no sitting is underway and nothing is withheld there. This rule binds the
**sitting-time** render, which is Phase 10's.

### 4.2 Registered variants (Directive §3)

Directive §3, quoted: *"When two designs both look defensible and neither is clearly wrong, **do not
arbitrate**. Implement both behind one interface and make the choice a setting."* It lists
**selection strategy** by name. Registrations:

| Setting | Values | Default | Owner | Reason both ship |
|---|---|---|---|---|
| `selection.explain_render` | `lines` \| `table` | `lines` | Phase 10 | Research §4.4 names this interface. S2's two-row candidate table is materially clearer for a `[PAIR:]` or blueprint-weighted request, where "why this over that" *is* the question; it is materially more surface everywhere else (narrow-viewport table treatment, and the third-column drift that turns a table into a dashboard). Same data, same strategy interface, one extra template. |
| `selection.explain_visibility` | `on-request` \| `always` | `on-request` | Phase 10 | Both defensible. `always` **must render after the activity in DOM order**, never above it, so project §2.1 holds under either value. DEFAULT, revisitable. |
| `selection.strategy` (optional spec field) | any registered `strategy_id` | absent ⇒ the mode's default | Phase 7, **pending replan** — see §7 | Directive §3 names selection strategy explicitly. Optional and additive; absent means today's behaviour exactly. |
| `selection.reach_readout` | `table` \| `table+bar` | `table` | Phase 10 | §6. |

**Hard stop where §3 stops.** Directive §3: *"It stops being affordable, and the rule stops
applying, when the two options need two parsers, two scorers, or two evidence stores."* None of
the four above crosses that line — each is one renderer reading one trace from one selector. The
one thing that **would** cross it, and is therefore arbitrated rather than registered: a second
"why" derivation computed at render time. D-04 already forbids it — *"`select()` returns a trace
alongside the items — never a second derivation."* A rendered explanation that recomputes is a
second selector wearing a template.

---

## 5. Spacing Scale

Inherited unchanged from project `UI-SPEC.md:321`. This phase introduces **no new spacing value**.

| Token | Value | Usage in this phase |
|-------|-------|---------------------|
| space-1 | 4px | gap between the two metadata lines of a block |
| space-2 | 8px | `<summary>` padding; indent step for the runner-up continuation |
| space-3 | 16px | default element spacing inside the `<details>` body |
| space-4 | 24px | gap between per-item blocks |
| space-5 | 32px | gap between the header block and the first item block |
| space-6 | 48px | not used in this phase |
| space-7 | 64px | not used in this phase |

**Exceptions (2), both stated rather than smuggled:**

1. **44px minimum interactive target** applies to the `<details>` summary (project §4 `ContextLine`
   row, §8 Tablet). The summary's text is `text-body`; padding brings the row to 44px.
2. **The CLI has no pixel grid.** E1's spacing unit is the **character cell**: indent 2 for the
   line body, indent 5 for a wrapped continuation, one blank line between blocks. This is not a
   violation of the 4px scale; it is a different medium, and saying so is cheaper than pretending
   `space-2` means something on a terminal.

---

## 6. Typography

Inherited from project `UI-SPEC.md:319-327` and §7.1. **No new size and no new weight.**

| Role | Token | Size / LH | Weight | Voice | Used for |
|------|-------|-----------|--------|-------|----------|
| Trace prose (lines 3, 4, 5, notes) | `text-body` | 16px / 1.5 | 400 | `--font-ledger` | the sentences a learner actually argues with |
| Trace metadata (lines 0, 1, 2, header) | `text-xs` | 12px / 1.4 | 400 | `--font-ledger` | ids, filters, counts, snapshot marker — project §7 puts "labels, provenance, compact status" here |
| `<summary>` `Why this item?` | `text-body` | 16px / 1.5 | 700 | `--font-chrome` | the one control on this surface |
| Section heading in a report render | `text-heading` | 20px / 1.2 | 700 | `--font-chrome` | §6 reach readout only |
| Display | `text-display` | 32px / 1.1 | 700 | — | **not used in this phase** |

- **Exactly two weights: 400 and 700.** Project §7: *"exactly two weights; use structure rather
  than a semibold tier."*
- **Inherited discrepancy, flagged not fixed:** `surfaces/presentation.py` SHARED_CSS ships
  `font-weight:600` in seven places today. That predates this phase and this phase creates none of
  it. **New elements use 400/700 only.** Reconciling the shipped 600s is Phase 4 debt, not Phase 7
  scope; recorded here so a checker attributes it correctly.
- **`text-lesson` (18px/1.65) is not used.** It is scoped to sustained authored lesson prose in
  Paper voice (project §7). A trace is neither.

---

## 7. Color

Palette source is `surfaces/theme.py`, LOCKED. Values below are **read from that file**, not
invented. This phase adds **zero** palette entries.

| Role | Light | Dark | Usage in this phase |
|------|-------|------|---------------------|
| Dominant (60%) | `--bg` `#f3f5f4` / `--ink` `#171d1c` | `#0e1413` / `#e4ebe9` | page field, trace text |
| Secondary (30%) | `--card` `#ffffff`, `--chip` `#eef2f1`, `--line` `#dfe5e3` | `#161e1d`, `#1d2726`, `#26312f` | the `<details>` container, its border, the per-block separator |
| Muted | `--mut` `#5f6d6a` | `#8fa19d` | `text-xs` metadata lines only |
| Accent (10%) | derived `--accent` / `--accent-soft` | derived | **see reserved list below** |
| `--unknown` / `--unknown-bg` | `#566067` / `#edf0f2` | `#9aa7ad` / `#1b2325` | the *stated* "no evidence store was found" state, and nothing else |
| Destructive | — | — | **none — this phase has no destructive action** |

**Accent reserved for, in this phase, exactly:**
1. the focus ring on the `<details>` summary;
2. the `Start practice` primary action, when a preview is followed by starting;
3. nothing else.

**Forbidden colour uses on this surface — LOCKED:**

| Forbidden | Reason, quoted |
|---|---|
| Colour distinguishing winner from runner-up | Project §7: accent is *"never correctness, mastery, warning, or all buttons"*; semantic tokens are *"paired with text/icon/structure; never color alone."* The distinction is the word "over" plus an indent. |
| `--ok` / `--bad` anywhere in a trace | A selection is not a verdict. Importing verdict colour teaches the learner to read a selection as a grade — which is exactly Anki's four-coloured-buttons anti-pattern research §2.1 already rejects. |
| `--pending` anywhere in a trace | ROADMAP crit. 11: a pending mark **influences selection in no way**. It is therefore invisible to the selector, and the *only* place it may appear on this surface is line 4's sentence saying it was not read. A `--pending` chip on a selection surface would assert the opposite of the invariant. |
| A progress-shaped fill, bar, ring, or percentage | Project §2.5 calm progress, LOCKED, and §13's "no mastery percentage / false precision". |
| Recall probability, ease, retrievability shown as a percentage | Research §4.2: *"Reject surfacing R as a percentage to a learner. A recall probability shown next to an item is a prediction about the person."* Project §13 forbids predictive learning analytics. |

---

## 8. Copywriting Contract

| Element | Copy | Source |
|---------|------|--------|
| Primary CTA | **`Start practice`** | Project `UI-SPEC.md:463`, LOCKED. Not re-invented — the action after previewing a selection *is* starting a practice sitting. |
| Web disclosure summary | **`Why this item?`** | Project `UI-SPEC.md:243` wireframe, verbatim. |
| Preview disclaimer | `Preview only - no session was started and nothing was recorded.` | New, §3.3. |
| Invariant line | `Pending marks were not read.` | New, ROADMAP crit. 11. |
| Empty state — heading | `No item matched this request.` | New. |
| Empty state — body | `Filters applied: objective emt:airway:opa-indications, type mc, difficulty recall. 0 of 38 items in this bank matched. Drop a filter and try again: itembank select <bank> --objective emt:airway:opa-indications` | New. Follows round-one F10 (research §5.1): *"the empty state names the one command that fills it."* It states the denominator, so the learner can tell "wrong filter" from "empty bank". |
| One-candidate state | `No other item matched this request, so there was nothing to choose it over.` | Required by 07-01 Task 2: *"`runner_up` is `None` only when no other candidate existed at all, and the block's own `reason` says so in words."* |
| No evidence store | `No evidence store was found, so no item was excluded for recency.` | §3.4. |
| Cooldown readmission | 07-05's note, verbatim: every candidate was inside the window, the oldest-seen were readmitted in age order, and the count. | 07-05 must_have. |
| Error — unknown profile | `No profile named "emt-drll". Profiles in this settings file: cs-review, emt-drill.` | Matches 07-06 Task 3 exactly: *"an unknown name raises SystemExit naming it and listing the profiles that do exist."* |
| Error — bank fails lint | Existing `lint` error grammar, unchanged. Recovery is `itembank lint <bank>`; `--force` is named only where it already is. | Existing behaviour; this phase adds no new lint copy. |
| Destructive confirmation | **none.** `itembank select` writes no session and appends no evidence event. There is no destructive action in this phase and therefore no confirmation UI. | 07-06 must_have. |

**Copy rules — LOCKED:**

1. **Never state a selection outcome the learner cannot inspect.** Research §2.1's Execute Program
   finding lands here as a copy rule: users disliked the opaque *"day 64, never again"* cutoff.
   Every number in the trace is either a count the learner can recount (`14 of 38`,
   `214 responses`) or an interval they can check against the log (`19 days ago`). No number in a
   trace is ever the output of a weighting.
2. **A field and a comparison, never a weight and never a total** (§3.1).
3. **No rule identifiers in rendered text** (D-05). Machine ids live in JSON; labels live in prose.
4. **Canonical flag is `--selection-mode`.** D-11 makes `selection_mode` a distinct field because
   `"remediation"` already means a *feedback* mode in three shipped contracts. Note: `07-VALIDATION.md`
   line 97 writes `--mode practice` in its manual-verification instruction — that is a stale
   pre-D-11 string and should be corrected to `--selection-mode practice` at replan.

---

## 9. UI Considerations

State coverage for E1–E4 (what Phase 7 builds). E5/E6 states are Phase 10's and are listed in §10.

Applicable state considerations resolved: **9 covered, 2 backstop, 1 unresolved.**

| Category | Element(s) | Status | Resolution / Reason |
|----------|------------|--------|---------------------|
| empty | E1/E4 candidate pool | ✅ covered | Zero candidates render the §8 empty-state copy naming the filters applied and the `N of M` denominator, and exit 0 — an empty result is a fact, not an error. |
| zero-one-many | E3 runner-up | ✅ covered | 0 other candidates ⇒ `runner_up: None` and the block says so in words; 1 ⇒ that item is the runner-up; many ⇒ the highest-placed loser is the runner-up and only it is named. |
| populated | E1 full trace | ✅ covered | Header + N blocks, each carrying lines 0-4 with non-empty text and a named runner-up. |
| partial | E2 degraded evidence | ✅ covered | Missing evidence store, index-absent fallback, and cooldown readmission each render their own §3.4 line; `trace.evidence.source` distinguishes `index` / `log` / `none`. |
| error | E1 unknown profile, unparseable bank | ✅ covered | Non-zero exit naming the profile and listing known ones (07-06 T3); lint errors keep the existing grammar. |
| error | E4 forbidden field on the preview branch | ✅ covered | `API_FORBIDDEN_FIELDS` still 400s on `session`/`bank_path`/`out` with `"preview": true` (07-06 T3 acceptance). |
| overflow | E1 30-item preview | ✅ covered | Blocks stream; no pagination, no truncation, no "…and 20 more". A preview that hides items is not a preview. |
| long-text | E1 long objective namespaces and ids | ✅ covered | Wrap at 72 columns, continuations indented to the line's own indent (§3.5 rule 6). Ids never wrap mid-token; they move to their own line. |
| no-leak | E1/E4 | ✅ covered | 07-01 `check_trace_leaks_no_key` and 07-06 `check_explain_renders_plain_text` build the forbidden-string list **from the parsed bank**, applied to the rendered text. Preview items are `public_item()` payloads. |
| encoding | E1 redirected stdout | 🧪 backstop | Measured: `sys.stdout.encoding` is `cp1252` here and non-ASCII redirects silently. A held-out check should assert `render_trace(...).isascii()` is `True`. No explicit evidence at verify ⇒ `insufficient_spec`, never a silent pass. |
| readability | E1 "reads as plain English to a human" | 🧪 backstop | `07-VALIDATION.md` already books this as manual-only for SEL-05, and correctly: legibility is a judgment a test cannot make. The five-line grammar makes the manual read *checkable* (each line present, each line a sentence) rather than impressionistic. |
| loading / in-flight | E4 `/api/start` preview | ⚠ unresolved | A preview costs one bank parse plus one history read on a loopback daemon (T-07-02, accepted). No in-flight state is specified because no caller renders one in Phase 7. **Planner treats as an assumption**; Phase 10's E5 owes an in-flight state. |

---

## 10. Corpus reach — E6, ROADMAP criterion 10

Criterion 10: *"The share of the bank's items the selector has ever served, over items eligible
under any mode — a property of the selector, not of the learner."*

The display contract borrows research §2.5's depth-distribution rules, and the borrow has a stated
reason: **it is the same class of measure** — a ratio about the system that becomes harmful the
moment it reads as a score about the person.

- **Ledger voice, plain table, denominator stated in words above it**, e.g.
  `Of the 312 items in this bank eligible under any mode:` then rows and counts.
  (Research §2.5 D1, recommended: *"boring and unimpeachable. Nothing about it can be read as a
  score about the learner."*)
- **`selection.reach_readout: table | table+bar`, default `table`.** The bar ships only *with the
  table beneath it*, `aria-hidden` over the table as the accessible representation, text labels on
  each segment so print (which may drop backgrounds) still reads, and **no percentage above 100
  rendered as a fill** (research §2.5 D2).
- **Report surface only. Never in the learning workspace, and never with a target.**
  Research §2.5's binding copy rule: *"A distribution shown next to an active item is a target no
  matter how it is worded."* Project §13 forbids a metric dashboard above the next instructional
  action.
- **It is a defect detector, not a goal.** Its purpose is to make "an engine that keeps re-serving
  the same fifty items" visible. Phrase it so a low number reads as a finding about the selector.

`keyboard/SR:` a real `<table>` with headers; narrow viewport uses the labelled horizontal-scroll
wrapper project §8 already requires. `print:` natively; the bar variant needs its text labels.
`degraded:` server-computed from the same evidence snapshot; with no evidence store it renders
`--unknown` plus `No evidence store was found, so reach cannot be computed.` — never `0%`
(project §4 `RecommendationCard`: *"Unknown is an explicit state, not `0%`"*).

---

## 11. LOCKED / DEFAULT register

**LOCKED — do not change in a plan:**

| # | Item |
|---|---|
| L1 | The trace renders in **Ledger voice**; a model paraphrase is a separate Chrome-voice labelled object and the trace does not move (B7). |
| L2 | **A field and a comparison, never a weight and never a total.** |
| L3 | The five-line block grammar and its order (§3.2). |
| L4 | Line 4 (`Pending marks were not read.`) is **unconditional**. |
| L5 | The header's **preview disclaimer** line. |
| L6 | **ASCII-only** rendered trace, both surfaces (measured reason, §3.5). |
| L7 | No colour, no glyph, no symbol distinguishes winner from runner-up — structure and the word "over". |
| L8 | `--ok`, `--bad`, `--pending` and any progress-shaped fill are forbidden on this surface. |
| L9 | No recall probability, ease, retrievability, or mastery percentage — ever, in any phase, on this surface. |
| L10 | E5 is **withheld and absent from the DOM** during a `diagnostic` or `exam` sitting until completion (§4.1). |
| L11 | `Why this item?` and `Start practice` are verbatim project copy; not re-worded. |
| L12 | The trace is a **return value, never a second derivation** (D-04). No render-time recompute. |
| L13 | S3 (persistent "why" panel) stays rejected. |

**DEFAULT — revisitable with a stated reason:**

| # | Item | Revisit when |
|---|---|---|
| D1 | `explain_render: lines` | A `[PAIR:]` or blueprint request makes the two-row table the common case. |
| D2 | `explain_visibility: on-request` | UAT shows learners never open the disclosure. |
| D3 | `reach_readout: table` | The table alone fails to make a re-serving defect visible. |
| D4 | 72-column wrap | Someone measures a better figure against real objective namespaces. |
| D5 | `text-xs` for metadata lines | If 12px proves unreadable for ids at 375px, promote to `text-body`; do **not** invent a fifth size. |
| D6 | `selection.strategy` as a spec field | See §12 item 1. |

---

## 12. Open questions a later phase must revisit

1. **`selection.strategy` costs a replan of 07-06 Task 1.** That task's acceptance criterion asserts
   `sorted(schema.properties) == sorted(selection.SPEC_FIELDS)`, so adding one optional field is a
   deliberate two-file change, not a drive-by. **Recommended but not assumed.** If the replan
   declines it, ROADMAP criterion 9 is still satisfied — the trace still names the strategy the
   *mode* selected; only the learner's ability to override it is lost.
2. **ROADMAP criteria 7-11 are not covered by plans 07-01..07-06.** Verified by search: the strings
   `strategy`, `fringe`, `blueprint`, `[CASE:]`, `corpus`, `reach`, and `pending mark` appear in no
   plan file. Those criteria are round-two additions that postdate the 2026-08-08 plans. **A replan
   is owed before execution**, and this spec exists partly so that replan has a design contract
   rather than a blank page. Not a UI defect — recorded because the UI contract above assumes
   criteria 7, 9, 10 and 11 get built.
3. **`[CASE:]` group traces (criterion 8).** Does a case group that serves as one unit produce one
   trace block or N? DEFAULT recommendation: **one block for the group**, naming the group and the
   count, plus one line per member giving its `Qn` — because the *decision* was to serve the group,
   and N near-identical blocks would misreport N decisions. Owed a real answer at replan.
4. **Blueprint-weighted ordering (criterion 8) versus L2.** A blueprint proportion is a weight. The
   trace must therefore state its **input** — `The exam blueprint asks for 30% airway items; 2 of
   the 7 chosen so far are airway.` — and never its output. Phase 10 will meet this collision at
   full force; naming it now is the cheap moment.
5. **Whether a printed sitting record includes the trace by default.** §4 says force-open in print.
   Phase 10 should confirm against a real printed report before locking it, since a 20-item sitting
   adds ~100 lines of trace to a printout.
6. **In-flight state for E4** (§9's unresolved row).

### What Phase 10 inherits

| Inherited | Consequence for Phase 10 |
|---|---|
| The five-line grammar | A weight-derived ranking fills line 2's `strategy_label` and line 3's field-and-comparison. It does **not** get a sixth line and it does **not** get a number. |
| L2 (field and comparison, never a weight) | This is the rule TREND-01/SCHED-01 will pull hardest against. A due-date computation states the **evidence it rests on**, not the score it produced — which is also TREND-05's own requirement. |
| L9 (no recall probability) | FSRS-style D/S/R may be *computed*; R may never be *shown* as a percentage next to an item. Research §4.2 and project §13. |
| D-08's soft penalty | Recency lowers ordering; the trace states *when* an item was last served, never by how much its rank moved. |
| `explain_render` / `explain_visibility` / `reach_readout` | Three registered settings arrive already named; Phase 10 builds the renderers, not the interfaces. |
| L10 | The sitting-time `<details>` must consult feedback mode before rendering, and must satisfy project §11.1's public-payload fixture. |
| The `Why this item?` string | Phase 10 does not get to re-word it. |

---

## 13. Required verification gates for this phase

Mapped onto project `UI-SPEC.md` §11. E1–E4 are not browser-facing, so gates 3 and 4 apply in their
CLI-equivalent form and gate 4's snapshots defer to Phase 10 with E5.

| Gate | This phase's form |
|---|---|
| 1. Public-payload inspection | Already planned: `check_trace_leaks_no_key` (07-01 T3) and `check_explain_renders_plain_text` (07-06 T3), both building the forbidden-string list from the parsed bank. **Add:** the rendered text contains no `CORRECT` letter, no option text, no `WHY BEST`, no `DA:` string. |
| 2. State fixture | §9's table: empty pool, one candidate, populated, no-evidence-store, index-fallback, cooldown-readmission, unknown profile, forbidden field, 30-item overflow, long objective id. |
| 3. Keyboard/SR equivalent | CLI form: assert the render carries **no ANSI escape**, no box-drawing, and that `render_trace(...).isascii()` is `True`. A linear text stream needs no focus-order test; it needs a "nothing here means anything except the words" test. |
| 4. Responsive snapshots | **Deferred to Phase 10 with E5.** Recorded as deferred, not skipped. |
| 5. Offline/degraded fixture | Run `itembank select --explain` in a directory with no `_evidence/`, and with the sqlite3 index deleted; assert both render their §3.4 line and neither invents a recency claim. |
| 6. Evidence trace | 07-06 already asserts the preview writes no session file and appends no event, by directory listing and log byte size. **Add:** the same seed and spec produce the identical ordered `item_ref` list from preview and from a real start (07-06 T3 already books this). |

---

## Registry Safety

| Registry | Blocks Used | Safety Gate |
|----------|-------------|-------------|
| None | None | **Not applicable.** No component registry, no npm, no CDN, no third-party UI blocks. Verified: no `components.json`, no `package.json`, no `tailwind.config.*`. This phase vendors no asset of any kind. |

**Supply chain (Directive §4a):** no third-party artifact enters in this phase, so the KaTeX-precedent
vetting gate has nothing to run against. Recorded explicitly rather than left blank, because
Directive §4a warns that *"the absence of dependencies is no longer a mitigation"* — the correct
statement is "no artifact added", not "dependency-free is safe".

---

## Checker Sign-Off

- [x] Dimension 1 Copywriting: PASS
- [x] Dimension 2 Visuals: PASS
- [x] Dimension 3 Color: PASS
- [x] Dimension 4 Typography: PASS
- [x] Dimension 5 Spacing: PASS
- [x] Dimension 6 Registry Safety: PASS

**Approval:** APPROVED - gsd-ui-checker, 2026-08-10. 6/6 dimensions PASS.
