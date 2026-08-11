# Style Registry Mechanics — R1.2 through R1.7

- **Created:** 2026-08-10
- **Brief:** `.planning/RESEARCH-BRIEF-2-lesson-styles-2026-08-10.md` §2, questions R1.2–R1.7
- **Binding:** `.planning/PLANNING-DIRECTIVES.md`, all six sections
- **Scope:** the *mechanics* of a style registry. The catalogue of styles themselves
  (R1.1/R1.1a) is a sibling artifact; this one assumes roughly ten named styles exist
  and designs the machinery that holds them.
- **Lands in:** Phase 3.1 (criteria 3, 3a, 3b), Phase 9 (R1.7), Phase 11 (restyle),
  Phase 6.2 (`[!CHECK]`).

---

## 0. What the codebase actually is, verified

Claims below are read from source, not assumed.

**The grammar that exists today** (`model.py`, `surfaces/lesson.py`):

| Element | Where | Note |
|---|---|---|
| `## LESSON` section in the bank preamble | `model.py:parse_lesson()` (167) | returns `source`, `body`, `intro`, `headings[]`, `error`, `detail` |
| `[LESSON-SRC: <path>]` external lesson file | `model.py:213` | directory-contained; external wins over inline; failure is `lesson.src_unreadable`, never a raise |
| `###` heading walk → `{text, slug, body}` in document order | `model.py:236-250` | the only structural unit inside a lesson |
| `lesson_slug()` — one slugifier for lookup key **and** anchor id | `model.py:145` | deliberately one call, not two |
| `LESSON-REF` item→heading link, backlinks both ways | `surfaces/lesson.py:339 backlinks()` | matches on stored slug |
| Renderable blocks: `####+` headings, one level of `-`/`1.` list, pipe tables, fenced code, `` ` ` ``, `**`, `_`, `[]()` | `surfaces/lesson.py:_render_blocks()` (242), `render_markdown()` (311) | explicitly "no attempt at CommonMark completeness"; structure resolved first, `html.escape` second |
| `[ID:]` 12/16-hex + `[HASH: sha256:]` content fingerprint | `model.py:259 content_fingerprint()`, `297 new_item_id()` | `lesson_ref` deliberately excluded from the fingerprint |
| One scorer: `runtime.score_response()` | `runtime.py:120` | canonical-form equality; constructed response returns `None`, never `False` |

**What Phase 3.1 already commits to adding:** `## TERMS` + `[[term]]` with a runtime
`glossable()` gate and `term_lookup` events; `[!KEY]` GitHub-compatible callout with
minted `[ID:]`/`[HASH:]`, `{{cloze}}`, Anki `#guid` round-trip, `key_review` events;
callouts, figures, print CSS; an optional per-item Educational Objective line; a
reserved `zh=` TERMS meta field.

**What Phase 9 already commits to:** vendored KaTeX rendered offline; a `## SCENARIO`
staged-reveal container where *the runtime* stages the reveal; WeBWorK-style
random-point numeric equivalence behind one accept rule.

Two facts from this that constrain everything below:

1. There is **one renderer** and it is a hand-rolled ~100-line block classifier. Any
   style needing a construct that classifier cannot reach in one added branch is a
   second parser, and is rejected under Directive §4.2 on that basis alone.
2. A lesson's only structural unit is the `###` heading. Every style below is
   therefore expressed as *what a section must contain and in what order*, because
   that is the only thing the format can talk about. This is a constraint, and it
   turns out to be the right one.

---

## 1. R1.2 — The minimum shared block vocabulary

### Verdict

**Twelve blocks, of which nine already exist or are already committed. The registry of
ten styles costs exactly three new containers, and all three are the same parser
shape.**

**The shared vocabulary (the floor every style is written in):**

| # | Block | Status | Which styles need it |
|---|---|---|---|
| 1 | `### heading` (the section = one idea) | exists | all |
| 2 | paragraph prose | exists | all |
| 3 | list (one level, ordered/unordered) | exists | all |
| 4 | pipe table | exists | expository, cookbook, reference |
| 5 | fenced code | exists | Bottom-Up, Runestone, Execute Program, cookbook |
| 6 | inline emphasis / code / link | exists | all |
| 7 | `## TERMS` + `[[term]]` | Phase 3.1 committed | all (it is house, not style) |
| 8 | `[!KEY]` memorizable block | Phase 3.1 committed | all except pure-narrative |
| 9 | callout (`[!NOTE]`/`[!WARNING]`/`[!TIP]`) | Phase 3.1 committed | all |
| 10 | figure (incl. the 6.1 manipulable SVG) | Phase 3.1 committed | math, EMT, CS |
| 11 | **`[!CHECK: <item-id>]`** | **NEW** | Execute Program, Brilliant, Runestone, Socratic, Bottom-Up, both math styles, Phase 6.2 |
| 12 | **`[!EXAMPLE]` with annotated steps** | **NEW** | Math Academy / worked-example, Runestone, cookbook, both math styles |
| 13 | **`## SCENARIO` staged reveal** | **NEW** (already named in Phase 9 §7, never specified) | case narrative, EMT |

That is 13 rows and three new blocks. Nine of ten styles are expressible in blocks
1–10 alone.

### Why these three and no more

**`[!CHECK: <item-id>]` is the single highest-leverage new block in the project.** It
is the seam between reading and testing, and six of the ten styles are *defined* by
where it goes. Critically it holds **no content**: it is a reference to an item that
already exists, the mirror image of the `LESSON-REF` that already exists on the item
side. The parser cost is one regex and one resolution against the already-loaded
question list. The renderer cost is one branch in `_render_blocks()` emitting an
embed placeholder. The scorer cost is **zero** — the embedded item submits through
`runtime.score_response()` exactly as it does on the quiz surface. Phase 6.2's gated
loop is `[!CHECK]` plus a hold; without this block Phase 6.2 has to invent its own
anchor and we get two ways to say the same thing.

**`[!EXAMPLE]` is a container with ordered annotated steps** — each step is a line
plus a *why*, which is exactly the worked-example effect the evidence supports (see
§6). It is syntactically a callout with a list inside, so it costs one entry in the
callout kind table, not a new parse path. Its steps are `1.`-list items the existing
classifier already handles; the container only adds semantics the linter can check
(`style.require`, `style.order`) and the renderer can style.

**`## SCENARIO`** is the one genuine new *document-level* container and Phase 9
already owes it. It is a `##` section peer to `## LESSON` and `## TERMS`, containing
`###` stages. Its grammar is the sibling R3.2's job; R1.2's only ruling is that it is
in the shared vocabulary rather than a case-narrative-private construct, because EMT
and any future clinical/legal case style both want it.

### The Brilliant ruling — one-idea-per-screen is a renderer, not a block

Brilliant's loop is the most-cited style in the brief and it needs **zero new
grammar**. "One idea per screen with a prediction before the reveal" decomposes into:
a `###` section that contains exactly one idea (a `style.density` lint rule), ending
in a `[!CHECK]` (a `style.require` rule), rendered **one section per screen** (a
pagination *render mode* over the heading walk `parse_lesson()` already returns).

Making pagination a render mode rather than a block is the load-bearing decision in
this whole artifact. It means the same lesson file prints, reads continuously, reads
paginated, and exports to audio without the author choosing, and it keeps Directive
§4.4 trivially satisfiable. If pagination were grammar, every style would need a
page-break block and every consumer would have to understand it.

### Styles rejected on parser cost, named

Per the brief's instruction to reject styles whose cost is a second parser:

| Rejected | What it would cost | What we ship instead |
|---|---|---|
| **Literate/notebook style** (interleaved authored prose and *captured execution output* cells, Jupyter-shaped) | An output block whose content is generated at build time, not authored — a second content source with its own staleness, plus a second renderer for rich output. Also breaks `[HASH:]`: the file's content changes without an author edit. | `[!CHECK]` + Phase 5's `check` type. The learner runs the code; we never store its output as content. |
| **Branching narrative** (choose-your-own-path case) | A graph document model: node ids, edge conditions, non-linear traversal. Kills `lesson_slug()`'s one-anchor-per-heading invariant and therefore kills `LESSON-REF` backlinks (an item would reference a path, not a heading). | `## SCENARIO` linear staged reveal, where the runtime controls pace. Gets the pedagogy of "you don't see the vitals until you ask" without a second document model. |
| **Dialogue/tutorial transcript style** (Socratic rendered as a two-voice script) | A speaker-attributed block, and worse, it structurally invites a model to voice one of the speakers — which collides with the round-one visual ruling that a model gets no typographic voice of its own. | Question-first Socratic as an *ordering* rule: `[!CHECK]` opens the section, prose answers it. Same pedagogy, zero grammar, no fake interlocutor. |
| **Spatial/canvas style** (Andy-Matuschak-style two-column margin notes as authored structure) | A layout grammar in the content file. Content would encode presentation, which the print and audio exports then have to undo. | Margin notes are a *render mode* over `[!NOTE]` callouts. Same decision as pagination. |

**Cost of R1.2:** 3 new blocks, 1 new parse branch each (`[!CHECK]` regex,
`[!EXAMPLE]` callout-kind entry, `## SCENARIO` section peer), 1 new render mode
(pagination) that touches no grammar, 0 new scorers, 0 new dependencies, 0 changes to
`score_response()`. One byte-identical no-op fixture per block per Directive §4.4 and
Extensibility Rule 3.

---

## 2. R1.3 — The shape of a style definition file

### Verdict

**One file per style at `styles/<style-id>.md`, each declaring at most one parent, with
exactly one level of inheritance permitted (`house` → style, never style → style).**

Round one's internal shape survives intact — a prose voice zone the human reads and a
machine-parsed `## Rules` pipe table — and gains two sections. The file is:

```
# Style: Worked Example → Variation → Formalization

[STYLE-ID: math-worked]
[STYLE-PARENT: house]
[STYLE-SUBJECTS: math]

## Voice
(prose. Written for the human maintainer. NOT sent to the authoring model verbatim —
see R1.5. This is where the pedagogy, the rationale, and the do-not-do-this notes live.)

## Rules
| id | kind | params | severity | prompt |
|---|---|---|---|---|
| example-before-formal | order.before | [!EXAMPLE], [!KEY] | error | yes |
| one-check-per-section | style.require | [!CHECK], 1 | error | yes |
| example-steps-annotated | style.require | step-why, all | warn | yes |
| section-density | density.max | idea, 1 | warn | no |
| open-with-claim | open.with | paragraph | warn | no |

## Exemplar
### Completing the square
(one real, lintable lesson section written in this style)
```

### Why one-file-per-style beats the two alternatives, on maintenance cost

| Shape | Cost when N grows to 10 | Cost to add style 11 | Cost to remove a style | Can a bank vendor a private style? | Verdict |
|---|---|---|---|---|---|
| **One file per style** | Flat. Each file is ~80 lines and independently readable. | New file + registry index line. | Delete the file; a bank referencing it fails with `style.unknown` naming the id. | Yes — drop a file in the bank's directory. | **Adopted** |
| One file with named sections | The file is ~800 lines. Every style edit touches the same file, so a two-person (or two-agent) edit is a merge conflict every time. Diff blast radius is the whole registry. A reader answering "what does `emt-case` require" reads past nine other styles. | Edit the shared file. | Edit the shared file; nothing stops a dangling reference. | No. | Rejected |
| Deep inheritance chains (style → style → house) | Rule resolution becomes a debugging surface. "Why did `example-before-formal` fire at `warn` here" needs a tool to answer. That tool is a new surface nobody budgeted. | Cheapest to *write*, most expensive to *reason about*. | Removing a mid-chain style breaks its children silently. | Yes, and confusingly. | Rejected |

The decisive argument is not aesthetics, it is **the diff**. Every style edit in this
project is reviewed by a human and executed by a model. One-file-per-style makes the
review unit equal to the change unit. A single 800-line registry file makes every
style edit look like a registry edit, and that is exactly how a governance file drifts.

### Why exactly one inheritance level

Two levels are cheap to implement and expensive to own. The concrete failure: a
`math-explore` style inheriting from `math-worked` inheriting from `house` means a
change to `math-worked`'s ordering rule silently reverses `math-explore`'s entire
pedagogy, because `math-explore` exists precisely to invert that ordering. Flat
inheritance forces `math-explore` to state its own ordering, which is the thing a
reader most needs to see. Cost of the restriction: a handful of duplicated rows across
sibling styles. That is the correct trade.

`[STYLE-PARENT:]` accepting anything other than `house` is `style.parent_not_house`
(error). This is a one-line guard that prevents the chain from ever forming.

### Reuse

The `## Rules` pipe table parses with the cell splitter that already exists
(`surfaces/lesson.py:_split_cells()` 153, `_is_separator_row()` 162). The `##`/`###`
walk is `parse_lesson()`'s, generalized. The realistic new code is one
`model.load_style(path)` returning a resolved rule dict, plus a registry index.

**Cost of R1.3:** ~1 new loader (~120 lines), 1 registry index file, 3 new lint codes
(`style.unknown`, `style.parent_not_house`, `style.exemplar_violates`), 0 dependencies,
0 renderer change. One plan in Phase 3.1.

---

## 3. R1.4 — The house/style split and the inheritance mechanism

### The split rule, stated testably

> **A rule is house-wide if and only if violating it would still be wrong in every
> other style.** A rule is style-specific if some other shipped style could
> legitimately require the opposite.

Apply it and the split falls out cleanly, because the two categories turn out to be
about different objects:

- **House rules constrain the artifact**: truthfulness, provenance, safety, register,
  accessibility, sentence-level mechanics. "No fabricated citation" is wrong in every
  style. "Every `[SRC:]` resolves in `## SOURCES`" is wrong in every style. "No
  second-person hectoring" is wrong in every style.
- **Style rules constrain the sequence**: what a section opens with, what must precede
  what, how many ideas before a check, how long a section runs. "Worked example
  precedes the formal statement" is *required* by `math-worked` and *forbidden* by
  `math-explore`. That is the test firing correctly.

Round one's 18 machine-checkable rules split roughly **14 house / 4 style-shaped**.
The 4 style-shaped ones (example ordering, idea density, check cadence, section
opening) are the seeds of the six rule *kinds* below.

### The cost control that makes a registry affordable: rule kinds, not rule codes

The brief's worry — "with a registry, that count multiplies" — is real if each style
contributes bespoke rules. It does not multiply if styles are restricted to
**parameterizing a fixed set of rule kinds**. Ten styles × ~5 rules each = 50 rule
*rows*, but only **six lint codes**:

| Rule kind | Params | Checks | Example use |
|---|---|---|---|
| `order.before` | block A, block B | within a section, every A precedes every B | worked example before formal statement |
| `density.max` | unit, N | at most N of unit per section | one idea per section (Brilliant) |
| `style.require` | block, N | section contains ≥ N of block | every section ends in a `[!CHECK]` |
| `style.forbid` | block | section contains no such block | case narrative forbids `[!KEY]` mid-narrative |
| `cadence.section` | min, max words | section length band | expository chapter's ramp |
| `open.with` | block kind | section's first block is of this kind | Socratic opens with `[!CHECK]` |

Adding style #11 costs **zero new lint codes and zero new parser branches** — it is a
file of rows over kinds that already exist. That is Phase 3.1 criterion 3a satisfied
literally rather than rhetorically. It also converts a rule the linter cannot run into
a detectable authoring error rather than silent decoration: a row naming a `kind` the
linter does not implement is `style.rule_unimplemented` (error), which is round one's
Q3 guarantee generalized.

A style needing a seventh kind is a real signal and should be a deliberate,
human-reviewed addition — not a thing an authoring model can introduce by writing a
style file.

### The inheritance mechanism

Resolution is by the `id` column, one pass, in this order:

1. Load `styles/house.md`'s rule table.
2. Load the style's rule table.
3. For each child row, if `id` matches a house row, the child row **replaces** it
   entirely (kind, params, severity). Otherwise it is appended.
4. `severity: off` on a child row disables an inherited rule.
5. Resolution is recorded: `itembank style show <id>` prints each effective rule with
   `inherited` / `overridden` / `own`. There is no way to get a surprise here, because
   the resolved table is one flat printable list.

**The guard that protects Directive §4.** House rows carry a `lock` column. A locked
house rule cannot be overridden or disabled by any style; attempting it is
`style.override_locked` (error). The locked set is small and is exactly the encoding of
the five non-negotiables in prose-rule form:

- no fabricated citation / every claim traceable to a resolvable `[SRC:]`
- no lesson text that asserts a verdict or a score (the runtime decides, §4.1)
- no block that would make a bank not using it render differently (§4.4)
- the accessibility rules from `UI-SPEC.md` (§4.5)
- no instruction to the reader to send anything anywhere (§4.3, no telemetry)

Without the lock column, a style file is a governance file that a model can write.
With it, the registry is safely model-writable, which is the whole point.

**Cost of R1.4:** 6 rule-kind lint codes + `style.rule_unimplemented` +
`style.override_locked` = **8 new lint codes total for the entire registry**, plus the
3 from R1.3 = **11**. Compare: implementing round one's single style was already
budgeted at ~18. The registry is *cheaper per style* than the single style was. One
new CLI subcommand (`itembank style show`). Zero dependencies.

---

## 4. R1.5 — How the authoring model consumes a style

This is the question that decides whether D3 is a differentiator or decoration, so the
verdict is stated as a mechanism, not a preference.

### Verdict

**Not verbatim. Distilled instructions capped at seven, placed last in the prompt, plus
exactly one exemplar, plus the lint output on retry. Adherence is produced by the
closed loop, not by the prompt — so the style contract is *enforced at lint* and merely
*advertised at prompt*.**

Named interface: **`StylePrompt`** — one function, `style.prompt_context(style_id,
attempt_n, lint_findings)`, returning the three parts. Every authoring caller (Phase
3.2 seeding, Phase 11 authoring) goes through it; nobody assembles style text by hand.

### What the evidence supports

Three findings from current work, and each one changes the design:

1. **Exemplars alone do not buy adherence.** Recent large-scale instruction-following
   work finds that adding three-shot exemplars produces no statistically significant
   gain in format adherence or robustness, while explicit instructions do improve
   compliance without closing the gap between semantically identical prompt
   formulations. *Design consequence:* exemplars stay, but as a shape-anchor for a
   thing hard to describe in prose (what an annotated worked-example step looks like),
   not as the adherence mechanism. One exemplar, not three.

2. **Instruction count is the binding constraint, and position matters.** Adherence is
   strong at roughly 3–5 simultaneous instructions, degrades substantially past ~10,
   with a clear recency advantage and the worst compliance for middle-positioned
   instructions. *Design consequence, and this is the load-bearing one:* pasting a
   style file verbatim — 14 house rules plus 5 style rules plus a prose voice zone — is
   **exactly the regime where adherence collapses**. Round one's "one `LESSON-STYLE.md`
   the model reads" was under-specified in a way that would have failed quietly. So:
   the `## Voice` prose zone is **for the human and is never sent**; the model receives
   a compiled block of at most seven imperatives, drawn from rows marked `prompt: yes`,
   placed at the end of the prompt.

3. **Verifiable instructions are the ones you can hold a model to.** The IFEval line of
   work is built on exactly this distinction — constraints amenable to objective,
   automated verification, scored without a judge model. *Design consequence:* a style
   rule's `prompt` column should be `yes` primarily for rules the linter can also
   check. A rule we can check but do not mention still gets enforced on retry; a rule
   we mention but cannot check is a hope. Ranking the seven promptable slots by
   "lintable and frequently violated" is the correct allocation.

### The mechanism

```
attempt 1:  [task] [source passages] [one exemplar section] [≤7 imperatives]  → draft
            → lint → findings
attempt 2:  [task] [source passages] [the draft] [the lint findings, verbatim, last]
            → revision
            → lint → findings
attempt 3:  as attempt 2. Then stop and hand to the human.
```

Three attempts, then human. The lint findings are already machine-readable with dotted
codes and offending fields (Phase 1, `lint --json`), which means the retry prompt is
*specific* — "section 'Completing the square' violates style.order: [!KEY] precedes
[!EXAMPLE]" — rather than a restatement of the rule. Specific violations are the
highest-value tokens in the whole loop, and they cost nothing to produce because Phase 1
already built them.

**The prompt budget becomes a property of a style file.** A style whose `prompt: yes`
rows exceed seven emits `style.prompt_budget` (warning). This is a genuinely new
constraint and it is the right kind: it caps style complexity at the point where the
evidence says adherence dies, instead of letting a style accumulate rules until it
stops working and nobody knows why.

### The exemplar doubles as the fixture

`## Exemplar` in the style file is (a) the few-shot example sent to the model and (b)
the linter's self-test. A style whose own exemplar fails its own rule table is
`style.exemplar_violates` (error). One artifact, two jobs, and it makes an
unimplementable style impossible to merge. This is the cheapest quality gate in the
design.

### Both-and, per Directive §3

Distilled-vs-exemplar is not actually a two-good-answers case requiring both behind an
interface — the evidence ranks them. But *verbatim* is worth keeping reachable for one
reason: a human reviewing a style wants the whole file. So `StylePrompt` exposes a
`mode` of `compiled` (default, shipped) and `verbatim` (available, off, documented as
inferior with the reason). Cost of shipping the second mode: one branch, no second
parser. It costs almost nothing and it makes the claim falsifiable when Phase 11 can
measure it.

**Cost of R1.5:** 1 named interface (`StylePrompt`), 1 new lint code
(`style.prompt_budget`) + `style.exemplar_violates` (counted in R1.3), 1 new column in
the rule table (`prompt`), 0 dependencies. Reuses `lint --json` unchanged. One plan in
Phase 3.1 (the compiler), consumed by 3.2 and 11.

---

## 5. R1.6 — How the learner chooses, and the content/style boundary

### Verdict on scope

**Three declarative scopes with one resolution order, plus a per-session *render mode*
that is not a style.**

```
[STYLE: id] in the lesson file        (most specific)
  → [STYLE: id] in the bank preamble
    → subject profile default          (Phase 9's profile config)
      → house                          (fallback, always resolves)
```

Per-lesson wins because a bank can legitimately mix — an EMT bank's pharmacology
chapter is expository and its cardiac chapter is a case narrative. Bank-level exists
because most banks are homogeneous and repeating the directive 40 times is churn.
Subject profile exists because Phase 9 already has that config object and "math banks
default to `math-worked`" is exactly what it is for. An unresolvable id is
`style.unknown` (error) naming the missing id — never a silent fallback to house,
because a silent fallback means a lesson is being linted against rules its author did
not choose.

**Per-reading-session style switching is rejected as a *style* choice and shipped as a
*render mode* choice.** The learner toggles: paginated / continuous / print / margin-
notes / audio-export. Those are presentation over the same parsed heading walk, cost
nothing, and satisfy Weibao's let-the-learner-choose instinct in the place where it is
actually free. Letting a learner say "render this case narrative as an expository
chapter" is not free, and the next section says exactly why.

### The content/style boundary, stated precisely

> **A style may change ordering, chunking, and the presence of framing blocks. It may
> not change what claims the lesson makes.**

Operationally, and this is the test to apply: **re-rendering into a second style is
possible if and only if the transform is a permutation or partition of blocks that
already exist in the source.** If the target style requires a block whose content is
not derivable from the source, it is authoring, not rendering.

Two named operations, and conflating them is the mistake to avoid:

| | `render_style` | `restyle` |
|---|---|---|
| Who | runtime | Phase 11 authoring loop |
| Model in the loop | **no** | yes |
| Output | HTML, transient | a **new** lesson file with its own `[SRC:]` provenance |
| Human gate | none needed | required |
| Reversible | trivially | it is a new artifact; the original is untouched |

`render_style` never invents. That is not a policy, it is a structural property: it has
no model.

### What is mechanically possible

- expository ↔ one-idea-per-screen (pagination over `###` — pure partition)
- any style → print, continuous, margin-notes, audio drill (Phase 9.1)
- worked-example → expository (drop the `[!CHECK]` embeds, inline the examples — a
  deletion, always safe)
- cookbook → expository (reorder; both are the same blocks)

### What is impossible, concretely

- **expository → case narrative.** Requires a patient, a timeline, a presentation, and
  clinical findings that are nowhere in the source. Producing them is fabrication, and
  under Directive §4.1 the runtime cannot fabricate. The brief's own example, confirmed.
- **expository → Socratic.** Requires questions *with keys*. A key is an assessment
  artifact with an `[ID:]` and a `[HASH:]`; deriving one from prose is item authoring.
- **expository → worked-example.** Requires a solved instance. If the source contains
  no worked instance, there is nothing to permute; if it does, the transform is legal
  and is the previous bullet's inverse.
- **anything → Bottom-Up.** Requires a runnable artifact that produces a visible result.
  Not derivable from prose, ever.
- **case narrative → anything.** The narrative's claims are entangled with its
  sequence; the reveal order *is* the pedagogy. Flattening it produces a chapter that
  asserts things the case only implied.

The honest summary is that **re-rendering is a real feature for roughly half the style
pairs and an illusion for the other half**, and the boundary is exactly whether the
target needs a block the source cannot supply. Shipping `render_style` as if it were
universal would be the failure mode; naming its domain in the style file is the fix.
Each style file therefore declares `[STYLE-RENDERABLE-FROM: id, id]`, the linter checks
the declared pairs are block-compatible, and the reader offers only the reachable ones.

**Cost of R1.6:** 1 new directive (`[STYLE:]`, one regex, valid in both the lesson
preamble and the bank preamble), 1 optional style-file field, `style.unknown` (counted
in R1.3), render modes are renderer-only. One plan in Phase 3.1, one criterion added to
Phase 11 for `restyle`.

---

## 6. R1.7 — What `??? for math` turns out to be

### Verdict

**Two styles, named, shipped together, differing only in the order of four blocks.**

- **`math-worked` — "Worked Example → Variation → Formalization."** The default.
- **`math-explore` — "Experience First, Formalize Later."** For review and enrichment.

First, dispose of the assumption in the question. **KaTeX is delivery, not form.** The
`???` was never about notation — Phase 9 already renders LaTeX offline from a vendored
asset, and that answers "how does the symbol appear," not "what shape is the lesson."
Likewise the 6.1 manipulable SVG protocol is a **figure inside a section**, not a style
of its own; a manipulable diagram is how one worked example is illustrated, and making
it a style would mean math lessons without diagrams belong to a different pedagogy,
which is false.

### `math-worked`, the shipped shape

One `###` section = one knowledge point. Five slots, in this order:

1. **One-sentence claim.** What this section lets you do. Prose.
2. **`[!EXAMPLE]`** — a fully worked instance, *annotated per step*. Each step is a
   line plus a why. Not a solution; a solution with its reasoning exposed.
3. **`[!CHECK: <item-id>]`** — one variation differing from the example on **exactly
   one dimension**. Scored by `runtime.score_response()`, with Phase 9's random-point
   numeric equivalence behind the one accept rule.
4. **`[!KEY]`** — the formal statement, *after* the example. Memorizable, Anki-
   exportable, `key_review`-emitting, per Phase 3.1.
5. Optional figure, including the 6.1 manipulable SVG.

Three to four such sections per lesson.

The evidence: Math Academy's actual published structure is introduction → worked
example → two or three near-identical practice problems, bundled as a "knowledge
point," three to four per lesson, explicitly justified by cognitive-load management and
the testing effect. Worked-example pedagogy generally rests on the same finding —
studying a solved instance before attempting one reduces working-memory load so
attention goes to the reasoning rather than the search. Slot 4's position is the
non-obvious part and it is deliberate: **the formal statement comes after the example,
not before.** A definition read cold is a string; a definition read after you have
watched it work is a compression of something you already have.

### `math-explore`, and why it ships too

Same four blocks, inverted: an exploratory `[!CHECK]` **first** (a question the learner
cannot yet answer formally), then prose on what they noticed, then `[!EXAMPLE]`, then
`[!KEY]` naming the thing at the moment naming becomes necessary. This is the Experience
First / Formalize Later shape used in current math-curriculum practice, where students
work with a concept in their own language and the formal vocabulary is attached at the
point of need rather than pre-taught.

**This is the ideal Directive §3 case and it should be said loudly.** The two styles
are literally the same block vocabulary in two orders. Shipping both costs **one extra
file in `styles/`**: zero new blocks, zero new lint codes, zero parser change, zero
renderer change, zero new dependency. If the registry mechanics in §§1–4 are right,
this is what "adding a style is a file" means in practice, and math is the proof.

Defaults, because the evidence is not symmetric: **`math-worked` for first exposure,
`math-explore` for review and enrichment.** The counter-evidence to exploration-first
is specific — at early stages of learning, added variation and open exploration impose
working-memory demands that interfere with building the foundation. Exploration is
strongest when there is something to explore *with*. So the default is not a coin flip,
and the subject profile encodes it while a lesson may override per §5.

### Cost of R1.7

Two style files. `[!EXAMPLE]` and `[!CHECK]` are already counted in R1.2 (both are
needed by non-math styles regardless). Phase 9 gains one success criterion naming
`math-worked` as the shipped default form and asserting that a math lesson renders
identically with KaTeX absent except for unrendered LaTeX. **Zero new dependencies.**

---

## 7. Consolidated cost

| Item | Count | Notes |
|---|---|---|
| New blocks | 3 | `[!CHECK]`, `[!EXAMPLE]`, `## SCENARIO` |
| New parse branches | 3 | one per block; `[!EXAMPLE]` is a callout-kind entry |
| New render modes | 4 | paginated, continuous, print, margin-notes — grammar-free |
| New lint codes | **11** | 6 rule kinds + `rule_unimplemented`, `override_locked`, `unknown`, `parent_not_house`, `exemplar_violates`, `prompt_budget` (12 named; `unknown` covers both style and parent misses if merged → 11) |
| New lint codes per additional style | **0** | the point of the whole design |
| New directives | 2 | `[STYLE:]`, `[!CHECK:]` |
| New interfaces named | 2 | `StylePrompt`, `render_style` / `restyle` split |
| New CLI subcommands | 1 | `itembank style show <id>` |
| New dependencies | **0** | pure stdlib; KaTeX already vendored |
| Changes to `score_response()` | **0** | `[!CHECK]` submits through the existing path |
| New parsers / scorers / evidence stores | **0** | Directive §4.2 intact |
| Style files shipped at 3.1 | ~4–6 | house + expository + `math-worked` + `math-explore` + at least one CS and one EMT from the sibling catalogue |
| Plans added to Phase 3.1 | ~3 | registry loader + resolution; rule-kind linter; `StylePrompt` compiler |
| No-op fixtures owed | 3 | one per new block, byte-identical, Directive §4.4 |

---

## 8. What could not be determined

1. **Whether prose-*structure* linting has real prior art.** Vale, textlint, proselint
   and write-good operate at the sentence and term level. Nothing found operates on
   heading cadence, example-before-abstraction ordering, or idea density per section.
   Our six rule kinds may therefore be novel — which means no external validation of
   their false-positive behavior. This is sibling question R2.2's territory and the
   answer materially affects R1.4's severity assignments; if the kinds prove noisy,
   `density.max` and `cadence.section` should ship at `warn` and never at `error`.
2. **No measured adherence numbers for pedagogical-structure conditioning
   specifically.** The instruction-following literature measures format and constraint
   compliance. Extrapolating the ≤7-instruction budget and the recency placement to
   "write a lesson in this style" is a reasoned extrapolation, not a measured result.
   It should be treated as a testable default and measured in Phase 11.
3. **Whether the exemplar earns its prompt tokens for this task.** The evidence says
   three-shot adds nothing for format compliance; whether *one* exemplar helps for
   structural pedagogy is untested. `StylePrompt` should make the exemplar toggleable
   so Phase 11 can measure it rather than assume it.
4. **The `## SCENARIO` grammar itself** is deliberately out of scope here (R3.2 owns
   it). R1.2 rules only that it belongs to the shared vocabulary rather than to the
   case-narrative style privately.
5. **Whether `[!CHECK]` should be able to reference an item in a *different* bank.**
   It would help reuse and it breaks the current one-bank-one-file load path. Left open;
   default is same-bank only, which is strictly narrower and therefore additive later.

---

## 9. Sources

- [When Models Can't Follow: Testing Instruction Adherence Across 256 LLMs](https://arxiv.org/abs/2510.18892)
- [How Many Instructions Can LLMs Follow At Once?](https://arxiv.org/pdf/2507.11538)
- [Instruction-Following Evaluation for Large Language Models (IFEval)](https://arxiv.org/pdf/2311.07911)
- [The Atomic Instruction Gap: Instruction-Tuned LLMs Struggle with Simple, Self-Contained Directives](https://arxiv.org/html/2510.17388)
- [Large Language Model Instruction Following: A Survey of Progresses and Challenges](https://direct.mit.edu/coli/article/50/3/1053/121669/Large-Language-Model-Instruction-Following-A)
- [Math Academy — How It Works](https://www.mathacademy.com/how-it-works)
- [Math Academy, part 8 (frankhecker.com) — lesson and knowledge-point structure](https://frankhecker.com/2025/02/15/math-academy-part-8/)
- [Experience First, Formalize Later — Math Medic](https://mathmedic.com/blog/experience-first-formalize-later-effl/)
- [Exploration before explanation — Maths No Problem](https://mathsnoproblem.com/blog/teaching-practice/exploration-before-explanation)
- [Teaching Mathematics Through Student Worked Examples — WestEd](https://www.wested.org/resource/teaching-mathematics-through-student-worked-examples/)
