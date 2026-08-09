---
date: 2026-08-09
topic: "Q5 extraction standard, Q6 per-subject best fit, Q7 bilingual reader"
brief: .planning/RESEARCH-BRIEF-learning-platform-2026-08-09.md (sections 1-3 binding)
confidence:
  q5_provenance_grammar: HIGH
  q5_coverage_map: HIGH
  q5_paraphrase_lint: HIGH
  q6_emt: HIGH
  q6_math: HIGH (checker) / MEDIUM (manipulables licensing)
  q6_cs: HIGH
  q7_bilingual: HIGH (fork line) / MEDIUM (exact field syntax, needs D1 grammar finalized in 03.1)
---

# Research: Extraction Standard, Per-Subject Fit, Bilingual Reader

Answers brief §4 questions Q5, Q6, Q7. Every finding is tagged
**FORMAT / RENDERER / RUNTIME / CONVENTION**, with cost (S/M/L dev effort) and
target phase. Non-negotiables honored throughout: runtime gates the learner;
one parser/scorer/evidence store; additive format; no real banks in repo.

---

## Q5 — Extraction Standard (→ insert 03.2 + Phase 11)

### Q5.1 The `[SRC:]` tag grammar — FORMAT, cost S, phase 03.2

**Prior art surveyed.**
- CSL (the citation model behind Zotero) attaches a citation to a *source id*
  plus exactly one *locator* made of a typed label and value — labels include
  `page`, `chapter`, `paragraph`, `section`, `figure`, `verse`, `version`
  [VERIFIED: zotero.org/support/dev/citation_styles + CSL schema discussion,
  confirmed via web search 2026-08-09]. CSL supports only one locator per
  citation, which users find limiting [CITED: forums.zotero.org/discussion/68937].
- Legal pinpoint citation composes source + page + subdivision
  (`id. at 214 ¶ 3`) — the compositional shape we want [ASSUMED — training
  knowledge of Bluebook conventions, not re-verified].
- 1EdTech **CASE** is the machine-readable standard for competency frameworks:
  every objective in a framework gets a GUID, frameworks are hierarchical, and
  "Common Alignments" link content to objective ids
  [VERIFIED: imsglobal.org/spec/case/v1p0, 1edtech.org/standards/case/about].
- The **2021 National EMS Education Standards** (NHTSA/ems.gov) are the
  official objective source for EMT; the document is a numbered,
  module-structured PDF [CITED: ems.gov/assets/EMS_Education_Standards_2021_Updated2_24_25forEO.pdf].
  Exact internal numbering convention not extracted this session — the
  03.2 planner should pull real ids from the PDF or the course syllabus
  [ASSUMED that they are stable, citable ids].
- Textbook publisher LO codes (AAOS/Jones & Bartlett chapter objectives like
  "7-1.2") exist per chapter [ASSUMED — not verified against a current
  edition; the private bank side can confirm against the actual AAOS-12e TOC].

**Recommended grammar.** Two tags, one registry. Keep provenance (*where it
came from*) and alignment (*what it teaches*) as separate tags, because the
Phase 11 auditor consumes them differently.

```
[SRC: <source-id> <locator> ...]        provenance — where this content came from
[OBJ: <framework-id>/<objective-id>]    alignment — which syllabus objective it serves

<source-id>   := slug registered in a `## SOURCES` section (see below)
<locator>     := <label><value>[-<value>]      one or more, space-separated
<label>       := ch | p | para | sec | fig | tbl | obj   (CSL-derived label set, extensible)
```

Examples:

```
[SRC: aaos12e ch7 p214-215 para3]
[SRC: emt-syllabus-f26 sec4 obj4.2]
[OBJ: nemses2021/airway.2.3]   [OBJ: emt-syllabus-f26/wk3.2]
```

Registry — a new optional bank section, additive (a bank without it parses
unchanged):

```
## SOURCES
aaos12e         | AAOS, Emergency Care and Transportation of the Sick and Injured, 12e | isbn:9781284243758 | fingerprint:_sources/aaos12e.fp.json
emt-syllabus-f26| EMT-B Fall 2026 syllabus | file:syllabus.md | -
```

Design decisions and why:
1. **Space-separated typed locators, not free text** — machine-lintable
   (regex per label), human-writable, and composes chapter+page+paragraph the
   way legal pinpoint cites do; fixes CSL's one-locator limitation.
2. **Source-id indirection through `## SOURCES`** — full bibliographic data
   lives once per bank; items carry only the slug + locator, so citations stay
   short and the linter can flag an unregistered slug (dangling citation).
3. **`[OBJ:]` uses `framework/objective` two-part ids** — mirrors CASE's
   framework→item GUID structure without adopting CASE's JSON-LD machinery
   (overkill for one learner). If a framework someday publishes CASE GUIDs,
   the framework-id can map to a CASE URI without a grammar change.
4. Both tags are valid on items, `[!KEY]` blocks, LESSON paragraphs, and TERMS
   entries — one grammar everywhere the auditor needs provenance.

**Lint rules (CONVENTION, cost S, phase 03.2):** unknown source-id = error;
locator label outside registered set = warning; `[OBJ:]` id absent from the
loaded objective framework = error; item with no `[SRC:]` in a bank that has a
`## SOURCES` section = warning (nudges provenance without breaking old banks).

### Q5.2 Objective coverage map — FORMAT + RUNTIME, cost M, phase 03.2 (format) + 11 (auditor)

**Format.** One markdown/JSON pair per course, generated (never hand-edited):
`coverage.md` for humans, `coverage.json` for the auditor. Source of truth is
computed from tags, not stored state:

```
| Objective (framework/id)  | State     | Items | Lessons | Evidence |
| nemses2021/airway.2.3     | covered   | Q4,Q9 | L2      | 2 cited  |
| nemses2021/airway.2.4     | uncovered | -     | -       | -        |
| emt-syllabus-f26/wk3.2    | contested | Q11   | -       | source conflict |
```

**How Phase 11 computes the three states** (matches the citation-first
pattern already in 11-RESEARCH.md and UI-SPEC acceptance scenario 8):
- **covered** — ≥1 lint-clean item AND ≥1 lesson block carry `[OBJ:]` for the
  objective, and each carries at least one `[SRC:]` that resolves to a
  registered source (the "cannot become covered without cited evidence" gate).
- **uncovered** — zero items or zero lessons reference the objective. This is
  the auditor's authoring queue.
- **contested** — the objective is referenced, but its citations conflict
  (two sources disagree per the ingestion conflict flag), a citation dangles
  (source removed/re-fingerprinted since tagging), or the paraphrase lint
  (Q5.3) flags the content. Contested never counts as covered and surfaces as
  a first-class filterable row (UI-SPEC source-ingestion surface rules).

Coverage thresholds (e.g., "covered needs ≥2 items") are a config knob, not
grammar. The map is the artifact that "shrinks Phase 11" per brief §5: 03.2
defines format + computation; Phase 11 only adds the authoring loop on top.

### Q5.3 Paraphrase-not-transcribe: standard + lint — RUNTIME (lint), cost M, phase 03.2

**The workable standard (two-layer, both machine-checkable):**
1. **Hard verbatim rule:** no run of **≥8 consecutive words** copied from a
   registered source (case-folded, punctuation-stripped). Research context:
   academic guidance flags 3+ consecutive source words as paraphrase failure,
   while corpus studies find innocent shared 7-grams across independent
   authors [CITED: arxiv.org/pdf/cs/0702012 — arXiv plagiarism detection uses
   common 7-grams as the analysis unit]. 8 is therefore the shortest run that
   is rarely innocent: **error at ≥8-gram match, warning at 5–7-gram match**
   outside quoted spans. Direct quotes are exempted by an explicit markdown
   quote + `[SRC:]` pair (quoting with citation is legal; silent transcription
   is not).
2. **Structural similarity rule:** per lesson-block/item, estimated Jaccard
   similarity of 5-word shingles against any single source region **>0.25 =
   warning, >0.5 = error** — catches "changed every 7th word" mosaic
   plagiarism that the verbatim rule misses. Thresholds start as config
   defaults and get tuned on synthetic fixtures.

**Fingerprint without storing the source text — FEASIBLE, verified.** This is
the winnowing/MOSS approach [VERIFIED: Schleimer/Wilkerson/Aiken "Winnowing:
Local Algorithms for Document Fingerprinting" + yangdanny97.github.io/blog/2019/05/03/MOSS
via web search 2026-08-09]:
- Normalize source text (case-fold, strip punctuation), slide a k-word window
  (k=8) producing k-gram hashes, then winnow with window w: keep the minimum
  hash per window. Guarantee: any shared substring of length ≥ w+k−1 words
  produces at least one shared fingerprint; density ≈ 2/(w+1).
- **Store only the hash set** (`_sources/<id>.fp.json`: 64-bit hashes +
  coarse locator per hash, e.g. chapter/page bucket). Hashes of 8-word
  shingles are practically non-invertible — the copyrighted text is never
  stored, which is exactly the legal posture we need for AAOS-derivative
  content. Size check: a ~400k-word textbook ≈ 400k 8-gram hashes ≈ 3–4 MB
  un-winnowed, <1 MB winnowed at w=4. Trivial.
- For the hard rule (exact ≥8-gram detection with no probabilistic gap),
  store the **full 8-gram hash set** rather than the winnowed one — still a
  few MB, still text-free. Winnowed set is only needed if size ever matters.
- The similarity rule uses MinHash over 5-word shingles — the expected MinHash
  agreement equals Jaccard similarity [VERIFIED: mccormickml.com/2015/06/12/minhash-tutorial,
  aksakalli.github.io/2016/03/01/jaccard-similarity-with-minhash]. 128 perms
  is plenty at our scale.
- **Pure Python, stdlib only:** `hashlib`/`zlib.crc32` + a 40-line winnower +
  a 30-line MinHash. `datasketch` exists on PyPI if we ever want LSH at scale
  [CITED: medium/codemotion datasketch articles], but we do not need it — one
  learner, a handful of sources. No dependency required.

**Where it runs:** `itembank lint` gains a `--sources` pass; the Phase 11
authoring loop runs the same pass as a quality gate before any draft is shown
(one linter, per the one-parser rule — the fingerprint checker lives beside
`model.lint()`, not in a second tool). Fingerprint generation
(`itembank fingerprint <source.txt> --id aaos12e`) is a private-side, one-time
command run against the learner's own copy of the text; only hashes enter the
data directory, and `itembank guard` should assert no `_sources/*.txt` ever
lands in the repo. CONVENTION + RUNTIME, cost M total.

---

## Q6 — Per-Subject Best Fit (→ Phases 5, 6.1, 9)

### Q6.1 EMT: readings + scenario items — FORMAT + RUNTIME, cost M, phase 9

**What the real exam now looks like.** The NREMT exam (2026) added
Technology-Enhanced Items — drag-and-drop, ordered lists, multiple response,
case studies — and multi-phase **clinical judgment scenarios** structured as
En-Route → Scene → Post-Scene, where each phase reveals new information and
asks one or more questions before the next phase unlocks
[VERIFIED: pocketprep.com TEI post + howtonremt.com clinical-judgment posts +
medictests.com/2026-nremt, web search 2026-08-09]. This derives from NCLEX
NGN's unfolding case studies (6 items walking the Clinical Judgment
Measurement Model: recognize cues → analyze → prioritize hypotheses →
generate solutions → take action → evaluate outcomes), plus NGN standalone
shapes: bowtie, trend, matrix [VERIFIED: ncsbn.org NGN presentation +
examsoft.com/resources/6-new-question-types-nclex].

**Gap analysis against our six types.** The TEI *response widgets* are already
covered: mc, multi (extended multiple response), dnd (drag-and-drop), build
(ordered list), table (matrix/grid). Bowtie is a constrained table (categorize
into cause/condition/intervention columns) — a table-type authoring
convention, not a new type. What we genuinely lack is the **container**:

- **`## SCENARIO` block (FORMAT, additive):** a named scenario with ordered
  `PHASE:` subsections (e.g., `PHASE: en-route`, `PHASE: scene`,
  `PHASE: post-scene`). Each phase carries stem prose (dispatch info, vitals,
  trend tables — trend items are just per-phase data reveals) and references
  1..n existing items by id. Banks without `## SCENARIO` parse unchanged.
- **Runtime staged reveal (RUNTIME):** the session engine serves phase N's
  prose and items only after phase N−1's items are submitted; later-phase text
  never appears in the public payload early. This is the same
  runtime-gates-the-learner muscle as the hint ladder — it is our core claim
  applied to scenario pacing, and exactly what B11 (exam-format fidelity)
  asks for. No new scorer: each item inside a phase scores through
  `runtime.score_response()` as itself.

**Drill patterns from the prep market.** Limmer's EMT PASS (items written by
former NREMT staff) sells *exam-verbiage fidelity*; Pocket Prep sells aligned
banks + weak-area focus [VERIFIED: limmereducation.com/product/emt-pass,
pocketprep.com]. Our version of both is authoring convention, not code: a
`LESSON-STYLE.md` register for NREMT-style stems ("You are dispatched to…"),
and Phase 7/10 already own weak-area selection. **Med-math drills** need one
small runtime addition: a numeric-answer variant that auto-marks with
tolerance/units (today `short` is human-marked). Recommend a `numeric` accept
rule on short items (`ACCEPT: 0.45 ± 0.05 mg` style) scored in the one
scorer — cost S, phase 9, and it is the same mechanism the math checker below
uses, so build it once.

### Q6.2 Math 1400: LaTeX, equivalence, manipulables — RUNTIME + RENDERER, cost M, phase 9 (+6.1)

**Authoring convention (CONVENTION, cost S):** inline `$...$` / display
`$$...$$` LaTeX rendered by the already-planned vendored KaTeX (09-03/09-04),
raw-source disclosure on render failure per UI-SPEC §8.6. Nothing new needed.

**Answer equivalence — the bounded checker is random-point numeric sampling.**
How the incumbents do it:
- **WeBWorK** checks a student formula by evaluating student and key at
  several (optionally author-pinned) sample points and comparing numerically —
  equivalent forms pass, and a non-matching formula almost surely differs at a
  random point [VERIFIED: webwork.maa.org wiki, Answer Checkers (MathObjects)].
- **STACK** (and Möbius with Maple) ship a full CAS (Maxima) and even then
  document that "algebraic equivalence" rides on the CAS's internal
  representation, not a decidable property [VERIFIED: docs.stack-assessment.org
  Answer Tests]. Zero-equivalence is undecidable in general (Richardson's
  theorem); SymPy's own `equals()` falls back to random numeric testing and
  admits True can be unproven [VERIFIED: docs.sympy.org gotchas +
  github.com/sympy/sympy/issues/10279].

**Verdict:** do NOT hand-roll a CAS; do exactly what WeBWorK does. A
`math-expr` accept rule on items: parse a restricted expression grammar
(whitelisted `ast` nodes or a small recursive-descent parser — stdlib), reject
anything outside the whitelist, evaluate learner and key at 5–7 random points
in an author-declarable domain, compare within tolerance. That covers college
algebra/precalc (rational, exponential, log, trig expressions) with ~200 lines
of Python and zero deps. Deterministic-by-seed so the one scorer stays
reproducible. If Weibao later hits calculus-level needs, **sympy is a pure
Python dependency** (now permitted) and slots in *behind the same accept
rule* — the format never changes, only the verifier. Cost M, phase 9. One
caveat the checker must own: "simplify your answer" style items cannot be
graded by equivalence alone (the unsimplified form is also equivalent) —
those need a form check (e.g., string-normal-form or term count) or stay
human-marked; flag this in authoring docs.

**Manipulables — licensing verdict (MEDIUM confidence on pricing, HIGH on
recommendation):**
- **Desmos API** requires an API key and partner terms; production use means
  contacting Desmos, terms/pricing not public [VERIFIED: desmos.com/api,
  desmos.com/api-terms, desmos.com/partners]. A packaged distributed app is
  exactly the case that needs a negotiated license. Risk: external dependency
  with unknown cost.
- **GeoGebra** is free for non-commercial use only; any commercial purpose
  requires a license agreement with GeoGebra GmbH [VERIFIED: geogebra.org/license].
  A personal tool is arguably non-commercial today, but the packaged-app end
  goal makes this a trap.
- **Our Phase 6.1 SVG protocol** is license-clean, already has an approved
  accessibility contract (semantic controls beside the visual, one canonical
  response, no raw pointer telemetry), and its numberline/plot tracer covers
  most of college-algebra manipulation (graph reading, point placement,
  transformation sliders).

**Recommendation:** extend the 6.1 protocol with 2–3 math scene types
(function graph with movable point, slider-parameterized family, interval
selection) rather than embedding Desmos/GeoGebra. RENDERER, cost M, phase 6.1
catalog + phase 9 profiles. Revisit Desmos only if a specific activity proves
out of reach.

### Q6.3 CSCI 1100: bottom-up runnable code — RUNTIME + FORMAT, cost M, phase 5 (+06.2)

**"The Bottom Up" decoded.** Weibao's referent is (with high likelihood) the
pedagogy exemplified by Ian Wienand's free book *Computer Science from the
Bottom Up* — the inversion of the usual top-down course: start at binary,
representation, and the machine, and build upward; "a shop class for computer
science" [VERIFIED: bottomupcs.com, archive.org/details/bottomupcs]. For a
CSCI 1100 intro course the operational meaning is: **every concept appears
first as a small runnable artifact the learner predicts, runs, and modifies**,
before abstraction — which is precisely the Execute Program / Runestone loop
already slated for insert 06.2. CONVENTION: a bottom-up subject profile is a
lesson-ordering + item-mix convention, not new code.

**Exercise shapes worth stealing** [VERIFIED: runestone.academy author guide;
exercism.org/docs building tracks]:
- Runestone: **activecode** (editable/runnable block with optional hidden unit
  tests graded on submit), **Parsons problems** (reorder scrambled code —
  this is literally our `build` type applied to code lines; zero new code,
  one authoring convention), **clickable-area** (click the buggy line — a
  `table`/`mc` convention over numbered lines).
- Exercism: the **concept exercise** discipline — one concept per exercise,
  a stub that shows where code goes, tests visible to the student, TDD
  framing — belongs in `LESSON-STYLE.md` for the CS profile, plus **practice
  exercises** as the open-ended tail.
- Boot.dev-style in-page runs map to our lesson runnable blocks (D7);
  ephemeral unless submitted, per UI-SPEC §5C.

**What the Phase 5 `check` type needs (priority order):**
1. **stdin/stdout cases** — already planned (multiple expected cases, verdict
   via the one scorer). Keep. Add per-case visibility flags (shown cases teach,
   hidden-case *count* is disclosed per UI-SPEC scenario 3).
2. **Function-signature checks** — needed for CSCI 1100 (write `def area(r):`
   without writing an I/O harness). Implementation: the item declares a
   harness mode (`HARNESS: function area`), the runner appends a generated
   `if __name__ == "__main__"` driver that calls the function with each case's
   args and prints the repr; scoring stays stdout comparison — **no second
   scorer, the harness is a runner detail**. Cost S on top of the runner.
3. **Property tests — defer.** Hypothesis-style properties are the wrong tool
   for an intro course and would drag in a dependency plus flaky-failure UX.
   A cheap 80% substitute if ever needed: author-seeded randomized cases
   generated by the harness with a fixed seed (still deterministic). Backlog.

**Pyodide vs daemon-side execution.** Pyodide is a multi-MB WASM runtime
(several MB core, tens of MB with packages; ~1.8 s cold / ~0.4 s warm start
in tuned deployments) that can be fully self-hosted/vendored
[VERIFIED: pyodide.org, devblogs.microsoft.com/python Pyodide feasibility,
github.com/pyodide/pyodide-pack]. Tradeoff:
- Daemon-side (Phase 5 status quo): zero new assets, real CPython, honest
  "no sandbox" wording already contracted — but it is genuinely unsandboxed.
- Pyodide: a real browser sandbox (the one true argument for it), works in a
  static build, but a large vendored asset, slower, and a *second Python
  runtime* whose stdlib/behavior can diverge from the daemon's.
**Recommendation:** stay daemon-side for Phase 5 (one execution path, one
truth), and re-evaluate Pyodide once at Phase 12 packaging — inside a packaged
desktop app the sandbox argument weakens further (the daemon is already local
and the app is the trust boundary), so Pyodide likely never earns its weight.
RUNTIME decision, cost 0 now.

---

## Q7 — Bilingual Reader as a Glossary Field (→ backlog 999.2; grammar reserved in 03.1)

**What real language readers do** (LingQ, Readlang, LWT lineage): per-token
click-to-lookup on arbitrary running text, **lemmatization** on lookup
(running→run), **per-word knowledge status** tracked over time (LingQ's 1–5
known scale), saved terms flowing into SRS review, sentence-level translation,
TTS/karaoke audio sync [VERIFIED: readlang/LingQ feature pages + LWT
github.com/edoreld/learning-with-texts, web search 2026-08-09].

**Answer: yes — the D1 grammar carries a bilingual gloss as one extra optional
field, and that is where it should stop for now.**

**The fork line, precisely.** Everything on the near side operates on the
*authored, curated* term set — the `## TERMS` entries the author chose. Everything
on the far side operates on *arbitrary tokens of running prose*:

| Fits in a glossary field (build via 03.1 grammar, ship whenever) | Needs per-token machinery (do NOT build now — backlog 999.2) |
|---|---|
| Per-term translation gloss shown on the existing `<dfn>` hover/tap | Click ANY word in prose to look it up |
| Gloss included when the term exports to Anki / joins the review queue | Lemmatization / morphological analysis (needs per-language NLP) |
| Multiple language glosses per term | Per-word knowledge-status store (1–5 scale) across all texts |
| Optional pronunciation/romanization string | Whole-sentence machine translation |
| Degrades to visible text with JS off (D1 rule holds) | TTS with word-level audio sync |

The moment any *un-authored* word must be tappable with tracked status, you
need a tokenizer, a lemmatizer, and a word-state database per language — that
is LingQ's whole product and a separate codebase. A curated glossary never
needs any of it.

**Recommended third-field design (FORMAT, cost S — reserve in 03.1, implement
render in 999.2).** Make the TERMS entry's optional trailing fields a
key-value list so the grammar never breaks:

```
## TERMS
term | definition [| meta]
meta := key=value ("; " key=value)*        unknown keys are IGNORED, never errors
```

Reserved keys now (rendering may lag the grammar):
- `zh=气道辅助物` — a gloss field per BCP-47-ish language code; any 2–8 char
  lowercase key that is not otherwise reserved is treated as a language code.
- `pron=qìdào fǔzhùwù` — pronunciation/romanization.
- `audio=…` reserved, undefined.

Example: `airway adjunct | a device that maintains an open airway | zh=气道辅助物; pron=…`

Why this shape: (a) **additive twice over** — old two-field entries parse
unchanged, and any future need (audio path, lemma, image) is a new key, never
a fourth positional field, so the grammar takes zero breaking changes on the
far side of the fork; (b) the renderer change is one line of the existing
`<dfn>` popover (gloss below definition, `lang` attribute set for correct
font/screen-reader voice — an accessibility requirement, not a nicety);
(c) Anki export already carries the field for free as another column.
**Lint:** duplicate keys = warning; malformed pair (no `=`) = warning;
unknown key = silently ignored (that is the compatibility guarantee).

---

## Phase Assignment Summary

| Finding | Kind | Cost | Phase |
|---|---|---|---|
| `[SRC:]`/`[OBJ:]` grammar + `## SOURCES` registry + lint | FORMAT/CONVENTION | S | 03.2 |
| Coverage map format + covered/uncovered/contested computation | FORMAT/RUNTIME | M | 03.2 (format) / 11 (auditor) |
| Paraphrase standard (≥8-gram error, Jaccard>0.25 warn) + winnowing fingerprint lint, stdlib-only | RUNTIME/CONVENTION | M | 03.2, reused by 11 |
| `## SCENARIO` phase container + staged-reveal session serving | FORMAT/RUNTIME | M | 9 (format could seed in 03.1) |
| Numeric-tolerance auto-marked accept rule (med-math + math shared) | RUNTIME | S | 9 |
| Random-point math equivalence checker (WeBWorK method); sympy only if ever needed | RUNTIME | M | 9 |
| Math manipulables: extend 6.1 SVG protocol; no Desmos/GeoGebra (license risk) | RENDERER | M | 6.1 + 9 |
| `check`: function-signature harness mode; Parsons = build-type convention; property tests deferred | RUNTIME/CONVENTION | S | 5 |
| Execution stays daemon-side; Pyodide re-evaluated only at packaging | RUNTIME (decision) | 0 | 5 / 12 |
| TERMS third-field `key=value` meta grammar (bilingual gloss) | FORMAT | S | reserve in 03.1, render in 999.2 |

## Assumptions needing confirmation
- A1: exact NEMSES-2021 / syllabus objective id spelling — pull from the real
  PDF/syllabus during 03.2 planning (grammar is agnostic to it).
- A2: AAOS-12e publisher LO code format — confirm against the private copy.
- A3: paraphrase thresholds (8-gram error / 0.25 Jaccard warn) — defaults to
  tune on synthetic fixtures, not product facts.
- A4: "The Bottom Up" = Wienand-style bottom-up pedagogy — confirm with Weibao;
  if he meant something else, only the CS `LESSON-STYLE.md` register changes.
