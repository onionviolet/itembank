# Constraint Audit — cargo-culted rules in the planning corpus

- **Date:** 2026-08-10
- **Scope swept:** `.planning/ROADMAP.md`, `.planning/STATE.md`, `.planning/research/*.md`, `.planning/phases/**/*.md`, both `RESEARCH-BRIEF-*` files, both `POST-RESEARCH-PROMPTS-*` files
- **Authorities read first:** `.planning/PLANNING-DIRECTIVES.md` (all six sections), `.claude/CLAUDE.md` (Constraints as amended 2026-08-09, and the HISTORICAL note at lines 74-78), `.planning/UI-SPEC.md` (LOCKED vs RECOMMENDED, §8 gates), `.planning/PROJECT.md`, `.planning/REQUIREMENTS.md`
- **Status:** proposal only. **No file outside this one was edited.** Every fix below is a suggested rewording, not an applied change.

---

## 0. What actually binds (established by reading, before any finding)

| Claim | Authoritative text | Binds? |
|---|---|---|
| Runtime, not model, decides what reaches the learner | DIRECTIVES §4.1; CLAUDE.md Core Value | **YES** |
| One parser, one scorer, one evidence store | DIRECTIVES §4.2 | **YES** |
| Evidence and banks on disk, no telemetry | DIRECTIVES §4.3; CLAUDE.md Data residency | **YES** |
| Format changes additive, proven by a byte-identical fixture | DIRECTIVES §4.4 | **YES** |
| Accessibility gates in `UI-SPEC.md` | DIRECTIVES §4.5 → `UI-SPEC.md` §8 (nine numbered gates) | **YES** |
| Bank-authored JavaScript is refused | REQUIREMENTS `VIS-01`; `UI-SPEC.md:609` anti-pattern | **YES** (and it is the ground several findings below should have used) |
| Core loop degrades, never blocks, with the **network** unplugged | CLAUDE.md:57; REQUIREMENTS `MODEL-03` | **YES** — a resilience rule about the network, nothing else |
| Python stdlib only | CLAUDE.md:56, marked *(relaxed 2026-08-09)*; brief §1 table | **NO — preference** |
| No install / no build step | Same amendment | **NO — preference** |
| Python only | Same amendment | **NO — preference** |
| Offline-first / local-first | Same amendment; DIRECTIVES §1 "survives as a preference" | **NO — preference** |
| **No JavaScript** | **Nowhere.** `UI-SPEC.md:309` explicitly permits "embedded HTML/CSS/**vanilla JS**"; `CLAUDE.md:83` "No Node.js, JavaScript" is inside the block marked HISTORICAL at lines 74-78 | **NO — does not exist** |
| **A print path / print output** | **Nowhere.** `UI-SPEC.md` §8 has nine accessibility gates; none mentions print. No requirement mentions print output | **NO — does not exist** |
| **"Directive §4.5" forbids JS or requires print** | §4.5 reads, in full: *"The accessibility gates in `.planning/UI-SPEC.md`."* Those gates are §8 items 1-9: semantic HTML first, keyboard path, focus, no-leak to screen readers, semantic equivalents for visual items, accessible math/code, status semantics, WCAG AA contrast, and offline/degraded honesty | **NO** |

Two structural notes that make the pattern legible:

1. **The no-JS floor is a real design preference with no authoritative backing.** It first appears as a *choice* in round-one research (`RESEARCH-BRIEF-learning-platform-2026-08-09.md:299`, `:301`) — "server-rendered textarea + lint list is the no-JS floor", "glossary-appendix no-JS fallback". Round two then cites it as a **veto** attached to a Directive number. That is the whole failure mode in one lineage.
2. **`stdlib-only` is doing more veto work than every other constraint combined.** It appears as an active rejection ground in at least 18 places across `.planning/phases/**`, including five places where it stands in as a *security control*.

---

## 1. Summary table — ranked by blast radius

| # | Location | Constraint invoked | Verdict | Decision survives? |
|---|---|---|---|---|
| **F1** | `ROADMAP.md:312` (mirrored `research/2026-08-10-lesson-style-catalogue.md:606,609,715,744`; `RESEARCH-BRIEF-2:346`; `research/2026-08-10-style-registry-mechanics.md:127`) | "breaks the no-JS and print paths, violating Directive §4.5" | **CARGO-CULTED** | **Yes — for a better reason** (bank-authored JS is forbidden by `VIS-01` / `UI-SPEC.md:609`) |
| **F2** | `phases/05-.../05-RESEARCH.md:168`, `05-CONTEXT.md:134`, `05-UI-SPEC.md:65` vs `ROADMAP.md:421` | "CodeMirror/Monaco/Ace explicitly forbidden — vendored-asset exception spent on KaTeX, CDN forbidden by the stdlib/no-network posture" | **CARGO-CULTED, and counterfactually false** | **No — already reversed**; the stale veto is still shaping Phase 5's plan list |
| **F3** | `ROADMAP.md:351` (Phase 3.2 SC1) | "through stdlib ZIP+SQLite reads alone" | **CARGO-CULTED** — and may make the criterion unmeetable | **Partly — REVISIT** |
| **F4** | `phases/11-.../11-RESEARCH.md:15`, `11-CONTEXT.md:19` (D-03); pre-loaded at `ROADMAP.md:750` and `REQUIREMENTS.md:200` | "under the stdlib constraint", "PDF/DOCX which stdlib cannot parse well" | **CARGO-CULTED** | **No — REVISIT**, Phase 11 is unplanned |
| **F5** | `01-SECURITY.md:75`, `02-01-PLAN.md:403`, `02.1-01/02/08-PLAN.md`, `10-03-PLAN.md:128`, `10-06-PLAN.md:130` | "no third-party supply chain exists, enforced by the zero-dependency constraint" | **EROSION-BY-OMISSION** — a preference is standing in as a security control | **No — the risk acceptance no longer follows** |
| **F6** | `ROADMAP.md:313-314` + `research/2026-08-10-style-registry-mechanics.md:279-289` | "the lock column is what makes the registry safely model-writable" | **EROSION-OF-A-REAL-RULE (latent)** — §4.1/§4.5 enforced by a file a model may write, with suppression available | **Yes, if hardened — see fix** |
| **F7** | `phases/03-.../03-RESEARCH.md:228`, `03-CONTEXT.md:158`, `03-04-PLAN.md:79` | "Forbidden outright by CLAUDE.md's stdlib-only constraint... Not evaluated further"; table rendering droppable "if a stdlib table renderer proves out of proportion" | **CARGO-CULTED** | **Renderer choice: yes, for a better reason. Table deferral: REVISIT** |
| **F8** | `ROADMAP.md:312` (second clause); `catalogue.md:386,714`; `style-registry-mechanics.md:45` | "branching is a second parser per Directive §4.2" | **OVERSTATED** | **Yes — for a sharper, concrete reason** |
| **F9** | `phases/02.1-.../02.1-RESEARCH.md:56` | "PyInstaller/py2exe explicitly ruled out by DEL-02's 'no build step, still plain Python inside'" | **MISCITED** — `DEL-02` contains no "no build step" clause | **Yes for Phase 2.1, but it now collides with Phase 13 SC1** |
| **F10** | `phases/02.1-.../02.1-RESEARCH.md:353,380`; `02.1-03-PLAN.md:69,228,385` | `pywebview` rejected on stdlib-only grounds "regardless of legitimacy" | **CARGO-CULTED** | **Yes on other grounds (reversal cost), but the wording is the confession** |
| **F11** | `UI-SPEC.md:309` | "No shadcn, registry, npm, or external component dependency" — used to waive the registry gate in `02/04/05/08-UI-SPEC.md` | **CARGO-CULTED inside an authoritative file** (not marked LOCKED) | **Waiver stands in effect; the stated reason does not** |
| **F12** | `phases/01-.../01-RESEARCH.md:210` → `01-06-PLAN.md:55` | "`jsonschema` violates the stdlib-only constraint... not viable here" | **CARGO-CULTED (historic)** | **Yes now — sunk; record the cost honestly** |
| **F13** | `ROADMAP.md:354` | "using stdlib winnowing over fingerprints only" | **OVERSTATED** | **Yes — the real ground is in the same sentence** |
| **F14** | `ROADMAP.md:644` | "roughly 200 stdlib lines", `sympy` "may later" | **OVERSTATED** | **Yes — determinism, not dependency count** |
| **F15** | `ROADMAP.md:214-215,222` (Phase 2.1 SC2) vs `ROADMAP.md:766` (Phase 13 SC1) | "still plain Python inside... without unpacking a build step" | **STILL VALID** (`DEL-02` is real) **but in open conflict** | **Both stand; the roadmap owes a reconciliation sentence** |
| **F16** | `phases/08-.../08-AI-SPEC.md:166`, `phases/11-.../11-AI-SPEC.md:177` | Arize Phoenix rejected on "no telemetry / no external dependency" | **HALF VALID** | **Yes — on the telemetry half only** |
| **F17** | `phases/01-.../01-VALIDATION.md:25`, `03-VALIDATION.md:21`, `05-RESEARCH.md:1194,1235`, `05-VALIDATION.md:63` | "no pytest, no test-runner dependency, by the stdlib-only constraint" → UAT items fall back to manual because "no JS test harness exists" | **CARGO-CULTED** | **REVISIT — it is costing verification coverage** |
| **F18** | `phases/02-.../02-RESEARCH.md:170,459` | Flask/aiohttp/bottle "rejected outright — the project's hard constraint" | **CARGO-CULTED (historic)** | **Yes — `http.server` was right anyway** |
| **F19** | `phases/02.1-.../02.1-DISCUSSION-LOG.md:68` | git-tag version derivation rejected: "couples runtime to a build step the project deliberately avoids" | **CARGO-CULTED** | **Yes — a `.pyz` has no git context at runtime regardless** |
| **F20** | `phases/02.1-.../COVERAGE.md:34` | webhooks "contradicts the local-first, no-server constraint outright" | **OVERSTATED** | **Yes — §4.3 (no telemetry) is the real ground** |

Not flagged, verified sound and left alone: `ROADMAP.md:102/763` (Phase 13 keeps Python because a port would temporarily create two scorers — a correct §4.2 application); `ROADMAP.md:421` "a second markdown engine is forbidden" (§4.2, correct); `ROADMAP.md:496` "bank-authored JavaScript is refused" (`VIS-01`, correct); `ROADMAP.md:616-620` and Extensibility Rule 8 (these *strengthen* §4.1/§4.2 and must not be eroded); `enforcement-and-loose-threads.md:416` rejecting `on-elapsed` (cites `UI-SPEC.md:105`, which is genuinely LOCKED and genuinely says no countdown pressure — a correctly-grounded §4.5 citation, and the model for how the others should read); `02-06-PLAN.md:30` (LAN default-closed on local-first — this is §4.3 wearing a preference's label, and it binds).

---

## 2. Findings in detail

### F1 — "no-JS and print paths, violating Directive §4.5" — CARGO-CULTED

**Where.** `ROADMAP.md:312`, Phase 3.1 criterion 3a:

> "...and explorable explanations (per-lesson JS is a renderer fork that breaks the no-JS and print paths, violating Directive §4.5)."

Propagated from `research/2026-08-10-lesson-style-catalogue.md:606` ("breaks the no-JS fallback the 3.1 render pass owes, breaks print, and collides with `UI-SPEC.md`'s accessibility gates (Directive §4.5)"), `:609` ("**Verdict: REJECT. NO CHEAP FIX — and it violates Directive §4.5**"), `:715`, `:744`; `RESEARCH-BRIEF-2-lesson-styles-2026-08-10.md:346`; and the same phrasing at `research/2026-08-10-style-registry-mechanics.md:127` ("kills print, kills the no-JS floor").

**What the authoritative text says.** DIRECTIVES §4.5, in full: *"The accessibility gates in `.planning/UI-SPEC.md`."* Those gates are `UI-SPEC.md` §8 items 1-9. Item 4 forbids leaking key or unshown hint text to assistive technology "via hidden labels, alt text, CSS-off content, title attributes, or live regions". Item 9 requires that "Offline/degraded state preserves readable lesson/source and authored feedback". **Neither is a no-JavaScript rule, and none of the nine mentions print.** `UI-SPEC.md:309` affirmatively permits "embedded HTML/CSS/**vanilla JS**". The "No Node.js, JavaScript" line at `.claude/CLAUDE.md:83` sits inside the block the 2026-08-09 note at lines 74-78 designates "historical fact, **not forward constraints**".

**Verdict: CARGO-CULTED.** A style was vetoed by a Directive number whose text does not contain the rule. The artifact's own §4 even concedes the evidence was thin and that the rejection rests on §4.5 — `catalogue.md:744`: *"I am rejecting it on Directive §4.5 (accessibility/renderer), which stands independently, not on the evidence."* It does not stand independently; it does not stand at all.

**Does the decision survive? Yes, on a real and stronger ground.** "Per-lesson bespoke JavaScript" is precisely **bank-authored JavaScript**, which `REQUIREMENTS.md` `VIS-01` and `UI-SPEC.md:609` forbid outright — a genuine authority/security rule, not a stylistic one. Add the honest secondary grounds already in the artifact: one hand-rolled renderer (§4.2), and thin evidence (`catalogue.md:590-600`).

**Corrected justification (proposed wording for `ROADMAP.md:312`):**

> ...and explorable explanations (per-lesson bespoke JavaScript is **bank-authored executable code, which `VIS-01` and `UI-SPEC.md:609` refuse outright**; it is also a second renderer against §4.2, and the evidence base is thin. The salvageable part is Phase 6.1's SVG protocol.)

**Same correction owed at** `catalogue.md:606,609,715,744`, `RESEARCH-BRIEF-2:346`, `style-registry-mechanics.md:127`. In each, replace "no-JS / print / §4.5" with "bank-authored JS (`VIS-01`)" and, where the argument is about a graph document model, with the concrete cost named in F8.

### F2 — CodeMirror "explicitly forbidden" — CARGO-CULTED and now false

**Where.** `phases/05-check-item-type-code-editor/05-RESEARCH.md:168`:

> "Hand-rolled textarea+gutter | CodeMirror / Monaco / Ace | Explicitly forbidden — vendored-asset exception is spent on KaTeX (Phase 9), external CDN forbidden by the stdlib/no-network posture"

Echoed at `05-CONTEXT.md:134` ("no external asset, no build step — the stdlib-only, no-install constraint applies to the [editor]") and `05-UI-SPEC.md:65`.

**What the authoritative text says.** The 2026-08-09 amendment: *"Dependencies, bundlers, npm, and non-Python components are permitted when they earn their cost... **do not reject an idea for needing a dependency**."* There is no "vendored-asset exception budget" anywhere; `CLAUDE.md:56` names KaTeX as an example, not a quota. And `ROADMAP.md:421` now records the opposite decision: *"CodeMirror 6 (MIT, ~300KB) is the editor."*

**Verdict: CARGO-CULTED, and counterfactually falsified by the roadmap itself.** **Highest live blast radius in this audit**, because the veto is still shaping unexecuted work: `ROADMAP.md:450` still lists plan `05-05-PLAN.md — The code editor: field, gutter, Tab/Shift-Tab`, which is the hand-rolled artifact the dead veto produced, while `ROADMAP.md:433` carries "ruling 5" OPEN on whether CM6 reaches the learner surface at all. Phase 5 currently contains two incompatible editor plans.

**Does the decision survive? No — it is already reversed and the corpus has not caught up.** Ruling 5 should be decided on merit (CM6's `Diagnostic{from,to,severity,message}` mapping 1:1 onto our lint records, versus the cost of a JS build/vendoring pipeline for the learner surface), **not** on an asset budget that does not exist. Note for whoever resolves it: `UI-SPEC.md` §8 item 2 (no keyboard trap, Tab-insertion-only inside the editor, Escape returns to navigation) is a **real** gate CM6 must be configured to satisfy — that is the one legitimate constraint on this choice.

**Corrected justification:** annotate `05-RESEARCH.md:168` as **SUPERSEDED 2026-08-09/08-10**, and restate the open question as: *does the learner-facing editor need CM6's capabilities enough to justify a vendoring and update pipeline, given `UI-SPEC.md` §8.2 must hold either way?*

### F3 — "stdlib ZIP+SQLite reads alone" — CARGO-CULTED, and possibly unmeetable

**Where.** `ROADMAP.md:351`, Phase 3.2 SC1:

> "An existing Anki `.apkg` imports into a bank through stdlib ZIP+SQLite reads alone..."

**What the authoritative text says.** Same amendment as F2. Nothing requires stdlib.

**Verdict: CARGO-CULTED**, and unusually costly because it is baked into an **acceptance criterion**, which is a contract on the executor. Flag for plan time: modern Anki exports (2.1.50+) ship `collection.anki21b` **zstd-compressed** inside the zip, and the Python standard library has no zstd decoder. If that holds, this criterion cannot be met as written for any recent `.apkg` — a fake constraint would have produced a feature that silently only imports legacy exports. **Verify this at plan time before writing the plan, not after.**

**Does the decision survive? Partly — REVISIT.** The real requirement is *lossless, reportable import with a per-note account of what converted and why* — which is criterion 1's own second clause and is the part that matters. The implementation route should be chosen at plan time from what actually reads current `.apkg` files.

**Corrected justification:** *"An existing Anki `.apkg` imports into a bank with a per-note report of what converted, what was skipped, and why — no note silently dropped. Prefer stdlib `zipfile`/`sqlite3`; if the archive's compression requires a dependency, take one and record it."*

### F4 — PDF/DOCX deferred "under the stdlib constraint" — CARGO-CULTED

**Where.** `phases/11-.../11-RESEARCH.md:15` and `11-CONTEXT.md:19` (D-03): markdown/UTF-8 are first-class *"under the stdlib constraint"*, PDF/DOCX pushed behind a later adapter. The framing is pre-loaded upstream at `REQUIREMENTS.md:200` (*"PDF and DOCX which stdlib cannot parse well"*) and repeated at `ROADMAP.md:750` as an open decision.

**Verdict: CARGO-CULTED.** The open decision is stated in terms of a constraint that no longer binds, so it is not actually open — it is pre-answered by a dead rule.

**Does the decision survive? No — REVISIT, and it is cheap to revisit** because Phase 11 has no plans yet. A syllabus is very often a PDF. The honest question is whether a PDF text extractor earns its dependency for the auditor's ingestion path; the answer is plausibly yes, and it was never asked.

**Corrected justification:** *"Markdown and UTF-8 text are the guaranteed first-class inputs because they are lossless and locator-stable. PDF/DOCX are a dependency decision to make on merit at plan time — the 2026-08-09 amendment permits one — and the deciding question is locator fidelity for citation, not stdlib coverage."*

### F5 — the supply-chain risk acceptances no longer follow — EROSION-BY-OMISSION

> **Repaired 2026-08-10 for phases 01, 02, 02.1** via `/gsd-secure-phase`. `01-SECURITY.md` (T-1-SC row, R-2 rationale, audit trail), `02-01`…`02-06-PLAN.md`, and `02.1-01/02/03/08-PLAN.md` now state the vendoring policy as the control. **Still outstanding:** `10-03-PLAN.md:128`, `10-06-PLAN.md:130`, and the `PLANNING-DIRECTIVES.md` §4a block in §3 below.

**Where.** `01-SECURITY.md:75` (*"Stdlib-only constraint means no third-party package supply chain exists in this phase"*), `02-01-PLAN.md:403` (*"enforced by the project's zero-dependency constraint... There is nothing to audit"*), `02.1-01-PLAN.md:402`, `02.1-02-PLAN.md:235`, `02.1-08-PLAN.md:273` (*"the stdlib-only constraint is the mitigation"* for T-02.1-SC), `10-03-PLAN.md:128`, `10-06-PLAN.md:130`.

**Verdict: EROSION-BY-OMISSION.** This is the inverse of the other findings and is the most concrete repair item in the audit. A *preference* was serving as a *security control*. When the preference was relaxed on 2026-08-09, the control vanished and nothing replaced it — while the roadmap simultaneously adopted CodeMirror 6 (~300KB of vendored JS, `ROADMAP.md:421`), contemplated vendoring two OFL font files (`UI-SPEC.md` §7.4), reserved `sympy` (`ROADMAP.md:644`, `:890`), named `edge-tts` (`ROADMAP.md:686`), and scheduled a Tauri/Rust/NSIS toolchain (Phase 13). Every one of those is a real supply chain, and the threat tables still say there is nothing to audit.

**Does the decision survive? No.** The accepted risk needs a real mitigation.

**Corrected justification:** replace *"no dependency exists, therefore no supply-chain risk"* with a stated policy — proposed: **every third-party artifact is vendored at a pinned version with a recorded checksum and a named license review, following the KaTeX precedent already set at `ROADMAP.md:666` (`09-03-PLAN.md — Approve one immutable KaTeX release before vendoring`).** That plan is the existing model; generalize it rather than inventing something. This is worth writing into `PLANNING-DIRECTIVES.md` alongside the constraint-basis block in §3 below.

### F6 — "the lock column is what makes the registry safely model-writable" — EROSION-OF-A-REAL-RULE (latent)

**Where.** `ROADMAP.md:313` and `research/2026-08-10-style-registry-mechanics.md:279-289`. House rows carry a `lock` column whose locked set is *"exactly the encoding of the five non-negotiables in prose-rule form"* — including *"no lesson text that asserts a verdict or a score (the runtime decides, §4.1)"* and *"the accessibility rules from `UI-SPEC.md` (§4.5)"*. Overriding a locked row is `style.override_locked` (error). The concluding claim: *"Without the lock column, a style file is a governance file that a model can write. With it, the registry is safely model-writable, which is the whole point."*

**Verdict: EROSION-OF-A-REAL-RULE, latent.** The design is thoughtful and probably right, but as written it moves the enforcement of §4.1 and §4.5 into **a parsed markdown file** that the system explicitly intends a model to be able to write — and `ROADMAP.md:314` grants, in the same phase, local `<!-- style-ignore: -->` suppression plus the ability for a style to *"enable, disable, re-severity, and parameterize a check"*. Two shipped affordances (suppression, re-severity) plus one file a model may write is a short path to a non-negotiable being demoted to a warning by an ordinary-looking authoring action. Nothing in the corpus yet states that suppression cannot reach a locked row.

**Does the decision survive? Yes, if hardened — and the hardening is small.** Three sentences, owed at `/gsd-discuss-phase 3.1`:

1. The locked house rows are **code constants in the linter**, not rows read out of `styles/house.md`; `house.md` documents them and cannot define or remove them.
2. `<!-- style-ignore: -->` **cannot suppress a locked rule**, and attempting it is itself an error.
3. A style may not re-severity a locked rule in any direction; `severity: off` on a locked id is `style.override_locked`.

Without those, the phrase "safely model-writable" is a claim the mechanism does not yet keep — which is exactly the objection the corpus itself levels at hard gates (`enforcement-and-loose-threads.md:489`).

### F7 — "Forbidden outright by CLAUDE.md's stdlib-only constraint... Not evaluated further" — CARGO-CULTED

**Where.** `phases/03-.../03-RESEARCH.md:228` on `markdown`/`mistune`/`commonmark`. Cascades to D-08 (`03-CONTEXT.md:112-115`, a deliberately small renderer with "no attempt at CommonMark completeness") and, most consequentially, to `03-CONTEXT.md:158` / `03-04-PLAN.md:79`, which grant leave to **drop table rendering** *"if a stdlib table renderer proves out of proportion"*.

**Verdict: CARGO-CULTED.** "Not evaluated further" is the tell — the option was never weighed.

**Does the decision survive? Split.**
- **The single hand-rolled renderer: yes, for a better reason.** §4.2 forbids a second parser, and `ROADMAP.md:421` commits the Phase 5 preview to reuse *our own* renderer via `data-line` sync. Swapping engines now would fork rendering across shipped surfaces. That is a real argument and it does not need stdlib.
- **The table-rendering deferral: REVISIT.** `ROADMAP.md:640` (Phase 9 SC4) requires that "An EMT lesson renders prose and tables correctly", and `UI-SPEC.md` §8 Narrow requires tables to "preserve headers using horizontal-scroll wrappers with an accessible name or stacked definition rows". A learner-facing feature with a §8 obligation is being held hostage to an effort estimate that only exists because a library was refused unread.

**Corrected justification:** *"One renderer, ours, because §4.2 forbids a second parser and Phase 5's preview reuses it via `data-line` sync — not because a library is forbidden. Table rendering is required by Phase 9 SC4 and carries a `UI-SPEC.md` §8 obligation; it is not droppable on effort."*

### F8 — "branching is a second parser per Directive §4.2" — OVERSTATED

**Where.** `ROADMAP.md:312` (written Socratic); `catalogue.md:386` (*"a **second parser** in everything but name, and Directive §4.2 kills it on sight"*), `:714`; `style-registry-mechanics.md:45` (*"any style needing a construct that classifier cannot reach in one added branch is a second parser, and is rejected under Directive §4.2 on that basis alone"*).

**What the authoritative text says.** §4.2: *"Exactly one parser, one scorer, one evidence store."* Its subject is the format contract and the runtime that reads it. `style-registry-mechanics.md:45` stretches it into a general rule that *anything the current ~100-line block classifier cannot reach in one added branch* is forbidden — which would forbid Phase 3.1's own new blocks, and is plainly not what §4.2 means. §4.2 forbids a **second** parser; it does not freeze the **one** parser's grammar. That is §4.4's job, and §4.4 permits additive growth proven by a byte-identical fixture.

**Verdict: OVERSTATED.** A rule about *count* is being used as a rule about *complexity budget*.

**Does the decision survive? Yes, and the artifact already contains the sharper argument.** `style-registry-mechanics.md:127` names the actual costs of a branching narrative: *"Kills `lesson_slug()`'s one-anchor-per-heading invariant... kills backlinks (an item would reference a path, not a heading)."* That is concrete, checkable, and independent of §4.2. Add the independent W7 ground (`catalogue.md:381`) — unbranched, a written Socratic sequence collapses into the rhetorical questions round one already banned.

**Corrected justification:** *"Written Socratic — rejected. A branching traversal needs a graph document model, which breaks `lesson_slug()`'s one-anchor-per-heading invariant and therefore `LESSON-REF` backlinks. Unbranched it collapses into the rhetorical questions W7 bans. Its pedagogy is kept in the hint ladder (Phase 6) and the tutoring model (Phase 8), where a real interlocutor exists and the runtime gates the tier."*

The general form at `style-registry-mechanics.md:45` should be reworded to what it actually means: *a construct requiring a document model other than the heading tree is out of scope for a style file, because a style constrains sequence, not grammar.*

### F9 — "DEL-02's 'no build step, still plain Python inside'" — MISCITED

**Where.** `phases/02.1-.../02.1-RESEARCH.md:56`, ruling out PyInstaller and py2exe.

**What the authoritative text says.** `REQUIREMENTS.md:149`, `DEL-02`, in full: *"The artifact is still plain Python inside, so a person or an agent can open and edit it."* **There is no "no build step" clause.** The phrase was added inside quotation marks around a requirement that does not contain it. (`DEL-01` does mandate stdlib `zipapp` for *the double-clickable artifact*, which is a real and separate requirement, and it is satisfied.)

**Verdict: MISCITED.**

**Does the decision survive? For Phase 2.1, yes** — `DEL-01` independently mandates `zipapp`, and the phase is complete. **But it now collides with Phase 13** (`ROADMAP.md:766`), whose SC1 mandates *"a PyInstaller-onedir Python sidecar"*. The corpus currently says PyInstaller is ruled out by requirement and required by roadmap. See F15.

### F10 — `pywebview` rejected "regardless of legitimacy" — CARGO-CULTED

**Where.** `02.1-RESEARCH.md:353` (*"a third stdlib-only exception with no clean reversal path. Rejected for v1"*), `:380` (*"excluded from the plan on stdlib-only-constraint grounds **regardless of legitimacy**"*), propagated to `02.1-03-PLAN.md:69`, `:228`, `:385` — the last of which records that because the option was rejected on stdlib grounds, *"no legitimacy checkpoint is reachable"*, i.e. the constraint pre-empted the security review that would otherwise have been owed.

**Verdict: CARGO-CULTED.** "Regardless of legitimacy" is the corpus admitting in writing that merit was not the deciding factor.

**Does the decision survive? Yes, on the other half of the same sentence** — "no clean reversal path" is a real argument, and Phase 2.1 shipped. Note only that Phase 13 now takes the native-shell route the constraint had forbidden, which is the relaxation working as intended.

### F11 — `UI-SPEC.md:309` — CARGO-CULTED inside an authoritative file

**Where.** `UI-SPEC.md:309`, §7 System table: *"Tool | None — stdlib Python with embedded HTML/CSS/vanilla JS. No shadcn, registry, npm, or external component dependency."* Not marked **LOCKED** (contrast `UI-SPEC.md:317`, which is). Cited to waive the component-registry gate in `02-UI-SPEC.md:43`, `04-UI-SPEC.md:264`, `05-UI-SPEC.md:65`, `08-UI-SPEC.md:43`, and reaffirmed at `UI-SPEC.md:503` ("Registry safety checked — unchanged. No component registry, no npm, no CDN").

**Verdict: CARGO-CULTED, in the one place it does most damage** — a stale preference sitting in an authoritative document, where downstream agents reasonably read it as binding. It also directly contradicts `ROADMAP.md:421`'s CodeMirror 6 adoption.

**Does the decision survive? The outcome does, the reason does not.** No component registry is genuinely wanted here; that is a taste and architecture judgement, and a good one. But it should be stated as **RECOMMENDED**, not as a constraint, and it must stop being the reason a phase waives its registry-safety gate — a vendored 300KB editor needs *more* supply-chain scrutiny, not a waiver.

**Note:** `UI-SPEC.md` is being edited by another agent. **This finding is a proposal to hand to that agent, not an edit.** Suggested wording: *"**RECOMMENDED:** no component registry, npm-managed component library, or CDN. Vendored third-party assets (KaTeX, CodeMirror 6, OFL fonts) are permitted at a pinned version with a recorded checksum and license review. **LOCKED:** no runtime fetch from a third-party origin, and no bank-authored JavaScript (`VIS-01`)."* That last clause is the part that is actually non-negotiable, and it is currently the part not stated in §7 at all. This line is also the corpus's own best disproof of the no-JS rule: it permits vanilla JS in plain words.

### F12 — `jsonschema` "not viable here" — CARGO-CULTED (historic)

`01-RESEARCH.md:210` rejected `jsonschema` on stdlib grounds, producing the hand-rolled 12-keyword validator (`01-06-PLAN.md:55`) and its fail-loud-on-unsupported-keyword design, which exists only because the validator is a subset of the spec. Shipped and working; **do not reverse.** The correction owed is honesty: record in `01-RESEARCH.md` that the validator's subset-ness is a **cost paid for a preference**, so that if unsupported-keyword failures become a recurring friction in Phases 5-11, the option is known to be open rather than remembered as forbidden.

### F13 — "stdlib winnowing over fingerprints only" — OVERSTATED

`ROADMAP.md:354`. The load-bearing clause is in the same sentence — *"the source text itself is never stored, which is also the defensible posture for AAOS-derivative EMT content"* — and it is grounded in §4.3 and in the accepted-risk note at `CLAUDE.md:62`. "Stdlib" is decoration on a good rule. **Reword to lead with fingerprints-only and drop "stdlib"**; the algorithm choice is a plan-time detail.

### F14 — "roughly 200 stdlib lines" — OVERSTATED

`ROADMAP.md:644` and `research/2026-08-10-tiered-verdicts.md:374`. The real ground is already correct and is stated at `ROADMAP.md:650`: random-point evaluation qualifies as reproducible **only once its seed derives from `content_hash`**, making sample points a pure function of the item. That is the authority rule (Extensibility Rule 8), and it is why the sampler is the default. `tiered-verdicts.md:374` already ships `sympy` as the alternative per §3. **Reword:** *"a small deterministic sampler is the default because its verdict is reproducible from the item alone; `sympy` implements the same accept rule as a registered alternative. The rule, not the library, is the contract."* Drop the line count and the word stdlib.

### F15 — Phase 2.1 SC2 versus Phase 13 SC1 — STILL VALID, in open conflict

`ROADMAP.md:215` (*"still plain Python inside — a person or an agent can open and edit it without unpacking a build step"*) and `:222` are grounded in a real requirement, `DEL-02`. `ROADMAP.md:766` (Phase 13 SC1) mandates a PyInstaller-onedir sidecar. Both are defensible: the `.pyz` stays the agent-editable artifact, the Tauri app is a separate distribution of the same runtime. **Neither is cargo-culted; the roadmap simply never says they coexist.** Proposed one-line addition to Phase 13: *"`DEL-02` continues to bind the `.pyz` artifact, which remains the agent-editable distribution. The frozen sidecar is an additional packaging of the same runtime, not a replacement for it, and every capability stays reachable from the CLI without the shell (SC5)."*

### F16 — Phoenix rejected on "no telemetry / no external dependency" — HALF VALID

`08-AI-SPEC.md:166`, `11-AI-SPEC.md:177`. **The telemetry half is a real non-negotiable (§4.3) and stands.** The "external dependency" half does not. The distinction matters because a *locally-deployed, nothing-leaves-the-box* eval tracer is no longer excluded by anything, and Phases 8 and 11 are the two phases most in need of eval tooling. **Reword to:** *"rejected because its tracing model sends evidence off the machine, which §4.3 forbids. A local-only tracer that writes nothing off-disk is permitted; the dependency itself is not the objection."*

### F17 — no test framework "by the stdlib-only constraint" — CARGO-CULTED, costing coverage

`01-VALIDATION.md:25`, `03-VALIDATION.md:21`. Downstream consequence at `05-RESEARCH.md:1194`, `:1235`, `05-VALIDATION.md:63`: UAT items fall back to **manual verification** because "no JS test harness exists in this project". With CodeMirror 6 arriving in Phase 5 and `UI-SPEC.md` §8 gates (keyboard path, focus, no-leak) that genuinely need automated checking, this is a fake constraint converting real accessibility gates — the one thing that *is* non-negotiable — into manual spot checks. **REVISIT at `/gsd-plan-phase 5`:** the question is whether a test runner earns its cost, and the §8 gates are the argument that it does.

### F18-F20 — historic or reducible

- **F18** `02-RESEARCH.md:170,459`: Flask/aiohttp/bottle "rejected outright — the project's hard constraint". Cargo-culted phrasing, right answer: `http.server` was already in use, a framework would have added surface for zero gain, and one-daemon/one-runtime is untouched either way. Historic; annotate only.
- **F19** `02.1-DISCUSSION-LOG.md:68`: git-tag version derivation rejected as coupling the runtime to a build step. The real reason is better and simpler: a distributed `.pyz` has no git context at runtime. Reword.
- **F20** `02.1-COVERAGE.md:34`: webhooks "contradict the local-first, no-server constraint outright". Local-first is a preference now, but **§4.3 (evidence on disk, no telemetry) independently kills an outbound webhook carrying evidence.** Right answer, wrong rule cited. Reword to §4.3.

---

## 3. Proposed "Constraint basis" block for `PLANNING-DIRECTIVES.md`

Proposed only — **not applied.** Suggested placement: immediately after §4, as §4a, so it is read with the non-negotiables it disambiguates.

```markdown
## 4a. Constraint basis — what binds, what does not, and how to cite it

A rejection, deferral, or "must" in any planning artifact is only as good as the
text behind it. Before you invoke a constraint, open the file and read the line.

**These five bind, and nothing else does.** They are §4.1-§4.5 above. Cite them by
number only when you have read the numbered text and it says what you need it to
say. §4.5 is exactly nine gates: `UI-SPEC.md` §8 items 1-9. It is not a general
accessibility instinct and it is not a renderer policy.

**These are preferences, per the 2026-08-09 amendment. They may inform a choice.
They may never veto one, and they may never be the whole stated reason:**
Python-stdlib-only, no install step, no build step, Python-only, offline-first,
local-first. A plan that rejects an option "because it needs a dependency" has
not made an argument. Report the real cost and decide on merit.

**These do not exist. Do not enforce them:**

- *No JavaScript.* `UI-SPEC.md` §7 permits embedded vanilla JS in plain words; the
  product vendors CodeMirror 6. The "No Node.js, JavaScript" line in
  `.claude/CLAUDE.md` sits inside the block marked HISTORICAL and non-binding.
- *A print path.* No authoritative file requires printable output. "It breaks
  print" is not a veto.
- *A vendored-asset budget.* KaTeX is an example, not a quota.
- *No dependencies as a security control.* See the supply-chain rule below.

**The three rules most often stretched past their scope:**

- §4.2 forbids a **second** parser, scorer, or evidence store. It does not freeze
  the one parser's grammar — additive growth is §4.4's subject and is permitted,
  proven by a byte-identical fixture. "This needs a new parse branch" is not a
  §4.2 violation. "This needs a second document model" is.
- §4.3 forbids evidence and banks leaving the disk. It is not a general
  ban on networked components; the network rule is `CLAUDE.md:57` — the core loop
  **degrades, never blocks**, which is a resilience requirement, not an offline
  mandate.
- §4.1 forbids a model deciding what reaches the learner. It is not a ban on a
  model *producing* anything; the gate is who accepts.

**Bank-authored JavaScript is refused** (`REQUIREMENTS.md` VIS-01,
`UI-SPEC.md:609`). This is real, it is the correct ground for rejecting per-lesson
executable content, and it is not the same thing as a no-JS rule.

**Supply chain.** Dependencies are permitted, so the absence of dependencies is no
longer a mitigation. Every third-party artifact — library, font, JS bundle,
toolchain — is vendored at a pinned version with a recorded checksum and a named
license review, following the KaTeX precedent (`09-03-PLAN.md`). A threat table
that accepts supply-chain risk on the grounds that "no dependency is installed" is
stale and must be rewritten.

**Citation discipline, binding on every artifact.** Any rejection that names a
Directive section quotes the sentence it relies on. A citation that cannot be
quoted is not a citation, and the finding it supports is void. If the honest reason
is cost, taste, or churn, say cost, taste, or churn — those are legitimate reasons
and they survive being stated plainly.
```

---

## 4. Recommended order of action

1. **F2 (Phase 5 / CM6)** — a live contradiction inside an unexecuted phase's plan list. Decide ruling 5 on merit before `/gsd-plan-phase 5`.
2. **F5 (supply chain)** — a security control that evaporated. Fix in `PLANNING-DIRECTIVES.md` and reopen the T-*-SC rows.
3. **F1 (no-JS / §4.5)** — reword in six places; the decision does not move.
4. **F6 (model-writable style registry)** — three hardening sentences owed at `/gsd-discuss-phase 3.1`, which is the very next action per `ROADMAP.md:809`.
5. **F3, F4, F7, F17** — four decisions to genuinely revisit, all in unplanned or unexecuted phases, all cheap to reopen now.
6. **F8-F16, F18-F20** — rewordings; no decision moves.
