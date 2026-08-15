# Phase 16A: Semantic Capability & Activity Contract - Research

**Researched:** 2026-08-15
**Domain:** Lesson semantic teaching roles rendered through one parser in two
modes, capability support profiles, media metadata, registered output modes,
purpose-first activity declarations, runtime-only assessment authority proven
adversarially, localization fixtures, and the portable canonical UTF-8
Markdown lesson. Built on top of Phase 14B (planned, not executed) and the
shipped assessment runtime.
**Confidence:** MEDIUM. Everything cited from the shipped `model.py`,
`runtime.py`, `evidence.py`, and `surfaces/lesson.py` is `[VERIFIED: <file>:<lines>]`
against real, executed source code read this session. Everything cited from
14A, 14B, or 15A is `[VERIFIED: <plan file>:<lines>]` against plan text only,
because none of those three phases has executed (confirmed below).
Architectural composition recommendations for 16A's own new surface
(capability registry shape, new callout kinds, activity declaration fields)
are this research's own synthesis and are flagged `[ASSUMED]`.

## Critical caveat: Phase 16A's declared dependency (14B) has not executed, and neither has anything upstream of it

Confirmed by direct filesystem check this session:

```
identity.py MISSING       journal.py MISSING       discovery.py MISSING
graph.py MISSING          course.py MISSING        course_package.py MISSING
director.py MISSING       blueprint.py MISSING
```

No `14A-FREEZE.md` exists under `.planning/phases/14A-identity-lifecycle-operation/`.
No `14B-FREEZE.md` exists under `.planning/phases/14B-graph-course-package-prototype/`
(only `14B-RESEARCH.md`, `14B-PATTERNS.md`, `14B-01` through `14B-06` PLAN
files, and `14B-VALIDATION.md`; no `*-SUMMARY.md` for any of the six plans).
No `15A-FREEZE.md` exists. `.planning/phases/13.9-walking-skeleton/` contains
only `13.9-01-PLAN.md` through `13.9-03-PLAN.md`; no `13.9-*-SUMMARY.md` and
no `13.9-DECISIONS.md` exist, so the walking skeleton itself has not been
walked yet.

This matters more for 16A than it did for 15B, because of a chained gate:
`ROADMAP.md`'s own Phase 14B entry states the freeze may not close "before
Phase 13.9 has been walked" `[VERIFIED: ROADMAP.md and 14B-06-PLAN.md Task 4
step 2]`, and `ROADMAP.md`'s Phase 16A entry states **"Depends on: Phase 14B
... Phases 14A and 14B are planned but not yet executed, so every signature
this phase imports is read from plan text at planning time; the first 16A
plan opens with a recorded precondition check that halts by name on any
divergence, the same pattern plans 14B-01, 15A-01, and 15B-01 set, extended to
check for a `14B-FREEZE.md` record."** `[VERIFIED: ROADMAP.md:1824-1830]`.

Every function signature, constant, and refusal code cited below as "from
14A", "from 14B", or "planned" is `[VERIFIED: <plan file>:<lines>]`, never
`[VERIFIED: <module>.py]`, for the same reason 15B-RESEARCH.md gives: those
modules do not exist on disk to read. The first 16A plan must open with the
identical precondition-check pattern 14B-01/15A-01/15B-01 already established,
extended to check for `14B-FREEZE.md`'s literal `## Frozen at 14B` heading
(not merely the file's existence, since `14B-06-PLAN.md` can also write a
`## Freeze withheld` section instead).

By contrast, **`model.py`, `runtime.py`, `evidence.py`, and
`surfaces/lesson.py` are shipped and executed**, confirmed by reading them
directly this session. They already carry a substantial fraction of what
CAP-01's fourteen semantic teaching roles need (see the role-mapping table in
Architecture Patterns below), and 16A's job for those roles is registration
and extension of an existing additive pattern, not invention from nothing.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| CAP-01 | One parsed canonical lesson supports both continuous reader and guided modes and renders fourteen semantic teaching roles (key idea, warning, prerequisite, misconception, expert tip, worked example, counterexample, source excerpt, term and definition, uncertainty, summary, inline check, hint, accessible visual interaction) composed from shared primitives, not separate content types. Default block order places a worked example or concrete case before the formal definition; an override is recorded with a reason. Semantic emphasis is author-provided orientation; no flow may compel learner highlighting. `[VERIFIED: REQUIREMENTS.md:546-567]` | Seven of the fourteen roles already have a shipped home (`_CALLOUT_KINDS` in `surfaces/lesson.py`, the `## TERMS` grammar, the hint ladder, the `visual` item type) and must be reused, not rebuilt; seven are genuinely new and need a registration in the same additive pattern. Guided mode does not exist yet in any form; 16A must define its data contract (stage sequencing, disclosure state) without producing Phase 17A's visual tokens. |
| CAP-02 | Each semantic capability declares an accessible-behavior, offline-fallback, renderer-availability, version, validation, and known-limits profile; each media asset carries rights, credit, accessible-alternative, derivation, availability, and integrity metadata; no decorative block is required by style alone. `[VERIFIED: REQUIREMENTS.md:569-579]` | No capability-profile registry or media-metadata grammar exists anywhere in the shipped codebase (confirmed by grep: no `figure`, `credit`, `rights`, or `derivation` handling in `model.py` or `surfaces/lesson.py`). This is genuinely new surface, composed from the shared-primitive shapes synthesis section 4.1 names ("Capability support profile" and "Source/media record" rows) and RIGHTS-01's operation-specific rights vocabulary once 14A lands. |
| CAP-03 | Registered output modes (notebook page, outline, Cornell notes, concept map, glossary, formula sheet, timeline, comparison table, study guide, source-extracted notes) compose from shared note and activity schemas plus provenance; a new canonical type is minted only when validation or behavior genuinely differs. `[VERIFIED: REQUIREMENTS.md:581-592]` | Synthesis section 12.2's disposition row for these ten modes is "Registered output modes after prototype ... They share stable relations and provenance but retain distinct intent, structures, learner actions, and validators" `[VERIFIED: research/phase-16/14-synthesis.md:655]`. 16A's freeze gate composes exactly two of the ten (outline, glossary) from one stress-corpus lesson's shared schemas, and records the other eight (minus the two already partly shipped: `outline_projection` per 14B-02 and the glossary per Phase 3.1) as backburner catalog entries. |
| ACTIVITY-01 | Every activity declares purpose, cognitive demand, objective, stimulus/source, response schema, retry behavior, feedback/disclosure policy, evidence status, accessibility equivalence, and static fallback; existing response forms serve many purposes and a new item type is warranted only when scoring semantics or response structure cannot be expressed safely. `[VERIFIED: REQUIREMENTS.md:596-606]` | Research stream 03's purpose-first matrix (ten purposes: prediction, noticing, retrieval, explanation, comparison, diagnosis, practice, transfer, reflection, formal assessment) is the authoring vocabulary this requirement adopts. The shipped eight item types (`mc`, `multi`, `table`, `dnd`, `build`, `short`, `check`, `visual`) are the closed set of response forms; ACTIVITY-01 is metadata composed alongside those forms, not a ninth form. |
| ACTIVITY-03 | The runtime alone scores, grants keyed disclosure, selects authoritative assessment behavior, and writes assessment evidence; prose remains pending until approved marking; no surface, agent, note, import, or visual leaks a key, invents a score, auto-grades prose, or changes a frozen sitting. `[VERIFIED: REQUIREMENTS.md:620-629]` | The shipped runtime already enforces most of this structurally: `runtime.public_item()` withholds the key before response, `evidence.mark_event()` rejects any marker other than the literal string `"human"` `[VERIFIED: STATE.md:355, evidence.py]`, and `runtime.glossable()` is "the same class of decision as `public_item()` withholding a key ... the runtime, not the author and not a model, decides what reaches the learner" `[VERIFIED: runtime.py:1509-1520]`. The Fixture's adversarial fixture is new test-writing against these existing gates, not new runtime machinery. |
| A11Y-02 | Canonical records carry language and direction; localization fixtures cover RTL, mixed code/math direction, CJK, combining marks, long strings, localized numbers/units, and culturally dependent examples. `[VERIFIED: REQUIREMENTS.md:732-741]` | No document-level language or direction field exists anywhere in the shipped format (the only `[LANG:]` marker in `model.py` is a per-`check`-item programming-language tag, unrelated `[VERIFIED: model.py:25,151-155]`). This is net-new metadata plus a fixture set; synthesis's cross-cutting rule 3 states the requirement in one sentence: "canonical records carry language and direction. Tests cover RTL, mixed code/math direction, CJK, combining marks, long strings, localized numbers/units, and culturally dependent examples" `[VERIFIED: research/phase-16/14-synthesis.md:582-584]`. |
| PORT-01 | The canonical lesson is UTF-8 Markdown with shallow metadata and an additive, versioned semantic profile; complete core meaning, captions, citations, definitions, static activity instructions, and media alternatives remain readable outside the app; derived HTML/index/cache is never the sole understandable copy; a proprietary or open-package canonical format stays rejected unless every criterion in research report 04 section 8 passes. `[VERIFIED: REQUIREMENTS.md:745-758]` | The shipped format already satisfies this for everything it currently carries (`model.py`'s module docstring: "Everything here reads markdown and returns plain dicts" `[VERIFIED: model.py:1-6]`); PORT-01's job is proving the NEW semantic grammar this phase adds keeps the same property, via the stress-corpus-opened-outside-the-app fixture. Report 04 section 8's eight-criterion proprietary-format gate is quoted in full below; none of the eight is met by any candidate in this research, so the recommendation is unchanged: reject a proprietary format. |
</phase_requirements>

## Summary

Phase 16A is a **logical contract phase, not a visual-design phase**: it
freezes what a lesson semantically means and how an activity is declared,
using the one existing parser and the one existing runtime, so that Phase 17A
can style the result without renegotiating its meaning. The single most
important discovery this research makes is that **half of CAP-01's fourteen
semantic teaching roles already have a shipped, working home** in
`surfaces/lesson.py`'s `_CALLOUT_KINDS` registry (`KEY`, `EXAMPLE`, `NOTE`,
`WARNING`), the `## TERMS` glossary grammar (Phase 3.1), the six-tier hint
ladder (Phase 6/8), and the `visual` item type (Phase 06.1). 16A's job for
those seven roles is retroactive capability-profile documentation (CAP-02
explicitly names the shipped hover/focus/touch glossary as "the first
catalogued capability" `[VERIFIED: ROADMAP.md:1821-1823]`) and NOT
re-implementation. The remaining seven roles (prerequisite, misconception,
expert tip, counterexample, source excerpt, uncertainty, summary) need one new
callout-kind registration each, following the exact one-line-registration
pattern the shipped code's own comment documents: "Adding a kind is a
one-line registration here -- the container and its degradation contract do
not change" `[VERIFIED: surfaces/lesson.py:643-647]`.

The second major discovery is the **dependency-chain caveat above**: 16A
depends on Phase 14B, which itself cannot freeze until Phase 13.9 (walking
skeleton) has been walked, and none of 14A, 14B, 15A, or 13.9 has produced a
summary or freeze record yet. Every 14B signature this research cites (the
course sidecar's rights fields, `graph.add_source`, `TREATMENT_RIGHTS`) is
read from `14B-01-PLAN.md` through `14B-05-PLAN.md`'s text, not from source,
and the planner must re-verify every one of them against the real
`14B-FREEZE.md` before or during 16A planning if it has landed by then.

The third discovery is that **CAP-02's media-metadata and capability-profile
grammar is genuinely new territory with no in-repo precedent**: grep confirms
no `figure`, `credit`, `rights`, or `derivation` handling exists anywhere in
the shipped parser or renderer today. This is real work, not composition,
though its shape should follow the closed-vocabulary, additive-registration
pattern every other new grammar addition in this project already uses
(`GATE_VALUES`, `_CALLOUT_KINDS`, `LOSS_CATEGORIES` in the planned
`course_package.py`).

**Primary recommendation:** treat CAP-01's fourteen roles as a gap-closing
exercise against the shipped renderer, not a from-scratch design; register
the seven new callout kinds using the exact `_CALLOUT_KINDS` one-line pattern
plus a new capability-profile registry (`capabilities.py`, a `checkpoint:decision`
candidate name, model-tier, pure, following `graph.py`'s established
no-file-I/O pattern); build ACTIVITY-03's adversarial fixture as a test suite
that attacks the ALREADY-SHIPPED gates (`public_item()`, `mark_event()`,
`glossable()`) rather than inventing new enforcement machinery; and keep
guided mode's 16A deliverable strictly a data/sequencing contract, with any
visual rendering built only to the minimum needed to prove the stress-corpus
fixture renders in "both continuous reader and guided modes," deferring all
token, color, and layout decisions to Phase 17A by name.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Semantic teaching-role blocks (callouts) | Model tier (`model.py`, parsing) | Presentation tier (`surfaces/lesson.py`, rendering both modes) | Every existing semantic role (`[!KEY]`, `[!WARNING]`, `[!EXAMPLE]`, `[!CHECK:]`) parses in `model.py`'s preamble/body scan and renders through `surfaces/lesson.py`'s `_CALLOUT_KINDS` dispatch; the new roles follow the identical split. |
| Continuous reader mode | Presentation tier (`surfaces/lesson.py`, shipped) | N/A | Already fully shipped for the existing roles; extending it to the seven new roles is additive rendering, no new tier. |
| Guided mode | Presentation tier (new) | Model tier (stage/disclosure metadata, new) | Does not exist yet. 16A defines the data contract (which blocks compose a "stage," what persists across a stage transition); Phase 17A owns the visual staging. Misassigning this to the model tier alone would make guided-mode behavior unobservable without a renderer; misassigning it entirely to Phase 17A would leave 16A's freeze gate unable to prove the corpus "renders in both modes" as its own Fixture sentence requires. |
| Capability support profile | Model tier (new registry, pure, no file I/O) | N/A | A capability's accessible-behavior/offline-fallback/renderer-availability/version/validation/known-limits tuple is static declared data, the same shape as `graph.EDGE_FIELD_DEFAULTS` or `course_package.LOSS_CATEGORIES`, a pure lookup, never I/O. |
| Media asset metadata | Model tier (parsing/validation) | Runtime tier (rights enforcement, once 14A/14B land) | Media metadata parses the same way any other block does; but "which right gates use of this asset" is exactly the rights-state question `identity.rights_state`/`identity.rights_granted` (14A) and `TREATMENT_RIGHTS` (14B) already answer for source bindings. 16A must not invent a second rights vocabulary for media; it reuses the planned one, flagged `[ASSUMED]` pending 14A landing. |
| Registered output modes (outline, glossary, etc.) | Presentation tier (rendering) | Model tier (shared note/activity schema) | `graph.outline_projection` (14B, planned) already IS the outline mode's model-tier data source; the glossary mode already IS `parse_terms`'s shipped output. CAP-03's job is proving two modes compose from ONE underlying schema rather than each mode owning a private one. |
| Purpose-first activity declaration | Model tier (parsing the declaration) | Runtime tier (scoring authority, unchanged) | An activity's purpose/demand/feedback-policy metadata is authored data read by `model.py`; the actual scoring stays entirely inside `runtime.score_response()`, untouched. Declaring a purpose never grants a new scoring path. |
| Runtime-only assessment authority | Runtime tier (`runtime.py`, `evidence.py`) | N/A | Already the sole authority per the project's core invariant; 16A adds no new code path here, only an adversarial test suite proving the existing gates hold against a scripted attacker. |
| Localization metadata and fixtures | Model tier (language/direction fields) | Presentation tier (rendering RTL/CJK/combining-mark content) | The `lang`/`dir` field is parsed data; correct bidi/CJK/combining-mark rendering is standard browser behavior once the field and the raw UTF-8 text are present, requiring no new normalization logic in Python (see Don't Hand-Roll). |
| Portable canonical file | Model tier (the one parser, additive grammar only) | N/A | PORT-01 is a property of `model.py`'s parse/serialize round trip, proven by opening the corpus outside the app; no new tier is needed, only a fixture. |

## Standard Stack

### Core (already shipped and executed)

| Module | Status | Purpose | Why reused, not rebuilt |
|--------|--------|---------|--------------------------|
| `model.py` | Shipped, executed `[VERIFIED: model.py:1-70]` | `parse_bank`, `parse_lesson`, `parse_terms`, `_preamble_section` (the ONE boundary-rule function every preamble section reader shares) `[VERIFIED: model.py:574-602]` | "Section order in the preamble is therefore free ... `_preamble_section` -- all read through this one definition, so the file carries one boundary rule rather than four that can drift" `[VERIFIED: model.py:578-586]`. Any new preamble-level grammar (media registry, activity declarations) should read through this same function, not a second boundary scanner. |
| `surfaces/lesson.py` | Shipped, executed `[VERIFIED: surfaces/lesson.py:640-680]` | `_CALLOUT_KINDS` dict (`KEY`, `EXAMPLE`, `NOTE`, `WARNING`), `_callout_kind_of`, the vendored gloss-enhancement hook | The closed, additive registration pattern this phase's seven new roles must follow exactly: "Adding a kind is a one-line registration here" `[VERIFIED: surfaces/lesson.py:646]`. |
| `runtime.py` | Shipped, executed `[VERIFIED: runtime.py:1509-1540]` | `public_item()`, `explain_payload()`, `glossable()`, `canonical_response()`, `score_response()` | ACTIVITY-03's runtime-only authority is these functions, unmodified. `glossable()`'s own docstring states the exact ACTIVITY-03 principle: "the runtime, not the author and not a model, decides what reaches the learner" `[VERIFIED: runtime.py:1514-1516]`. |
| `evidence.py` | Shipped, executed `[VERIFIED: STATE.md:355]` | `mark_event()` (rejects any marker other than the literal string `"human"`), `append_event()` | The adversarial fixture's "auto-grade prose" attack must be proven refused by this EXISTING gate, not a new one. `mark_event()` rejects any marker other than 'human' (T-1-24); a model verdict is not accepted evidence until Phase 8/TEACH-09" `[VERIFIED: STATE.md:355]`. |
| `model.GATE_VALUES` | Shipped `[VERIFIED: model.py:2052]` | `GATE_VALUES = ("required", "recommended", "off")` | The exact closed-tuple-constant shape every new CAP-01/CAP-02 vocabulary (renderer-availability states, known-limits categories) should follow. |

### Core (planned, not yet executed - 14A/14B)

| Module | Status | Purpose | Why reused, not rebuilt |
|--------|--------|---------|--------------------------|
| `identity.py` | Planned `[VERIFIED: 14A-01-PLAN.md, cited in 14B-01-PLAN.md:196-198]` | `RIGHTS_OPERATIONS = ("read", "quote", "transform", "remote_process", "package", "export", "share")`, `RIGHTS_STATES = ("granted", "denied", "unknown")`, `rights_state`, `rights_granted` | If media rights gate anything before 14A lands, this is the ONE rights vocabulary; 16A must not invent a second one for media assets. Flagged `[ASSUMED]` pending real landing. |
| `graph.py` | Planned `[VERIFIED: 14B-01-PLAN.md:112-118, 14B-02-PLAN.md:107-119, 14B-03-PLAN.md:101-114]` | `outline_projection(doc)`, `EDGE_TYPES`, `TREATMENT_KINDS` (eleven, closed), `TREATMENT_RIGHTS` (an eleven-key map from treatment kind to required right) | `outline_projection` is the literal model-tier source CAP-03's "outline" registered output mode composes from; a second, independent outline generator inside 16A's own code would violate the "compose from shared schemas" clause of CAP-03 directly. |
| `course.py` | Planned `[VERIFIED: 14B-01-PLAN.md:119-127, 14B-03-PLAN.md:116-121]` | `bind_source`, `bind_treatment`, `rights_for_binding` (all rights-gated at the moment of the operation, never cached) | The exact pattern ("no stale snapshot ever authorizes") 16A's media-rights enforcement should follow once 14A/14B land, per `14B-03-PLAN.md`'s own Pitfall 5 discipline. |

### New in this phase

| Component | Purpose | Why it is new |
|-----------|---------|----------------|
| Seven new `_CALLOUT_KINDS` registrations (`PREREQUISITE`, `MISCONCEPTION`, `TIP`, `COUNTEREXAMPLE`, `EXCERPT`, `UNCERTAINTY`, `SUMMARY` -- exact string tokens are this research's proposal, a `[ASSUMED]` naming choice) | The seven CAP-01 roles with no shipped home | No existing block, callout kind, or item field carries these meanings today (confirmed by full-text grep across `model.py` and `surfaces/lesson.py`). |
| `capabilities.py` (name is this research's proposal, a `checkpoint:decision` candidate) | Pure model-tier module: the capability support profile registry (accessible-behavior, offline-fallback, renderer-availability, version, validation, known-limits per capability) | No existing module owns "does this capability's renderer exist, and what does an unavailable renderer show instead"; CAP-02 names this a shared primitive with no shipped implementation. Follows `graph.py`'s established pure, no-file-I/O pattern. |
| A media-asset metadata grammar (block-level, additive; exact syntax is `[ASSUMED]`, a `checkpoint:decision` candidate between a fenced-attribute block and a pipe-table registry section following `## TERMS`'s and `## SOURCES`'s precedent) | Rights, credit, accessible-alternative, derivation, availability, integrity per asset | Confirmed by grep: zero existing handling of `figure`, `credit`, `rights`, or `derivation` in `model.py`. |
| A purpose-first activity declaration grammar (fields: purpose, cognitive demand, objective, stimulus/source, response schema, retry behavior, feedback/disclosure policy, evidence status, accessibility equivalence, static fallback) | ACTIVITY-01's ten declared fields, attached to existing item types | Research stream 03's ten-purpose taxonomy (`4.1 Summary matrix`) is the vocabulary; no parser field carries "purpose" or "cognitive demand" today. |
| Localization fixture set (RTL, mixed code/math direction, CJK, combining marks, long strings, localized numbers/units) plus a `lang`/`dir` metadata field on the canonical lesson header | A11Y-02's fixtures and the field they validate | No document-level language/direction field exists; the only `[LANG:]` marker is per-`check`-item and unrelated (`model.py:25,151-155`). |
| An adversarial runtime-authority test suite (new test file, e.g. `tests/assessment_authority_adversarial.py`) | ACTIVITY-03's Fixture: a scripted agent, a note, and an import each attempt to leak a key, invent a score, auto-grade prose, or edit a frozen sitting | This is new TEST code proving EXISTING gates hold; it adds no new runtime machinery. |
| The portable rich-lesson stress corpus (`fixtures/lesson_capability_corpus.py` or similar; exact name is a `checkpoint:decision` candidate) | One synthetic lesson exercising every semantic teaching role plus one unknown optional and one unknown required semantic; the medical evolving-case fixture; the disputed-timeline fixture; the localization fixture set | The freeze gate's named deliverable, following `fixtures/corpus_14b.py`'s fictional-content-only, fixed-seed convention. |

### Alternatives Considered

| Instead of | Could use | Tradeoff |
|------------|-----------|----------|
| Seven new callout kinds registered in the existing `_CALLOUT_KINDS` dict | Seven new top-level Markdown block types (e.g. `## PREREQUISITE`) | Rejected as the default: CAP-01's own text says roles are "composed from shared primitives, not separate content types" `[VERIFIED: REQUIREMENTS.md:546-547]`, and the shipped `[!KIND]` callout container is exactly that shared primitive already proven for four roles. A new top-level block per role would be the "widget-specific lesson grammar" CAP-01 explicitly supersedes. |
| A new pure `capabilities.py` registry module | Extending `graph.py` (14B, planned) to also hold capability profiles | Rejected: `graph.py`'s scope is explicitly the course objective graph (containers, objectives, edges, bindings); capability profiles describe LESSON RENDERING semantics, an orthogonal concern with no graph relationship. Growing `graph.py` past its 14B-frozen scope (once frozen) would violate the same module-boundary discipline `15B-RESEARCH.md`'s Alternatives Considered already flagged for `blueprint.py` versus `director.py`. |
| Reusing `identity.RIGHTS_OPERATIONS`/`rights_state`/`rights_granted` for media rights once 14A lands | A second, media-specific rights vocabulary (e.g. `MEDIA_RIGHTS_STATES`) | Rejected: RIGHTS-01 is explicit that rights are operation-specific and closed; a second vocabulary for the same seven operations, applied to media instead of sources, would be exactly the "second rights vocabulary" 14B-03's Pitfall names as a Directive-4.2-adjacent risk. |
| A minimal functional guided-mode renderer sufficient only to prove the stress-corpus fixture "renders in both modes" | A visually polished guided-mode renderer | The visually polished version is explicitly Phase 17A's job per the phase description's landmine note: "Visual system and tokens are Phase 17A's job. 16A is the logical contract: do not research or propose visual design, only semantic behavior, fallbacks, and fixtures." A polished renderer here would duplicate work Phase 17A must redo against real tokens. |

## Package Legitimacy Audit

Not applicable. This phase installs no new external package. It composes
existing, shipped, and planned in-repo Python-stdlib modules and adds new
Markdown grammar plus Python data structures, consistent with the project's
stated preference (still a preference, not a rule, per the 2026-08-09
constraint relaxation) and the fact that no research question in this phase's
scope names a new library. Localization fixtures (RTL, CJK, combining marks)
are exercised as raw UTF-8 text and standard HTML/CSS `dir`/`lang` attributes;
they do not require an ICU, Unicode-segmentation, or bidi-algorithm library,
because rendering direction is a browser responsibility once the `dir`
attribute is emitted (see Don't Hand-Roll).

## Architecture Patterns

### System Architecture Diagram

```text
 Authored lesson Markdown (canonical, UTF-8, additive grammar)
   |
   v
 model.py: parse_bank / parse_lesson / parse_terms / _preamble_section
   |  (ONE parser; new grammar reads through the SAME boundary function)
   |
   +--> existing roles: [!KEY] [!WARNING] [!EXAMPLE] [!CHECK:] ## TERMS
   |      (shipped, Phase 3/3.1/6/06.1 -- reused unmodified)
   |
   +--> NEW roles (16A): [!PREREQUISITE] [!MISCONCEPTION] [!TIP]
   |      [!COUNTEREXAMPLE] [!EXCERPT] [!UNCERTAINTY] [!SUMMARY]
   |      (one-line _CALLOUT_KINDS registration each, same container)
   |
   +--> NEW media metadata block (rights, credit, alt, derivation,
   |      availability, integrity) -- gated at render/package time by
   |      identity.rights_granted once 14A/14B land
   |
   +--> NEW capability profile lookup (capabilities.py, pure, no I/O)
   |      accessible-behavior / offline-fallback / renderer-availability /
   |      version / validation / known-limits, keyed by capability name
   |
   v
 Two presentation paths over the SAME parsed document (surfaces/lesson.py):
   |
   +--> Continuous reader mode (shipped for existing roles; extended here)
   |      renders authored order verbatim, all roles inline
   |
   +--> Guided mode (NEW, 16A data contract only)
   |      stages blocks, persists position separately, degrades an
   |      unavailable renderer to the static instructional path
   |      (capabilities.py's renderer-availability field decides this)
   |
   v
 Activity blocks inside either mode declare purpose/demand/objective/
 stimulus/response-schema/retry/feedback-policy/evidence-status/
 accessibility-equivalence/static-fallback (ACTIVITY-01), but the
 RESPONSE ITSELF still flows through the unchanged eight item types
   |
   v
 runtime.score_response() / public_item() / explain_payload() / glossable()
   (UNCHANGED; ACTIVITY-03's adversarial fixture proves these refuse every
    scripted leak/invent-score/auto-grade/edit-frozen-sitting attempt)
   |
   v
 evidence.append_event() / evidence.mark_event()
   (UNCHANGED; mark_event() still rejects any marker but the literal
    string "human")
```

A reader can trace the primary use case (an authored lesson becomes a
rendered, scored, evidence-producing experience) from the top (Markdown text)
to the bottom (an evidence event) by following the arrows: no new parser, no
new scorer, and the two new presentation-mode branches both read the SAME
parsed document rather than forking it.

### Recommended Project Structure

```text
<repo root>/
├── model.py                    # existing; gains seven callout-kind entries
│                                   in surfaces/lesson.py's _CALLOUT_KINDS
│                                   dict (parsing itself is unchanged --
│                                   [!KIND] is already a generic container)
├── surfaces/
│   └── lesson.py                # existing; _CALLOUT_KINDS gains seven
│                                   entries; gains a guided-mode render path
│                                   (data-contract level only, no tokens)
├── capabilities.py               # NEW -- pure model-tier capability
│                                   profile registry, no file I/O, follows
│                                   graph.py's established pattern
├── schemas/
│   └── capability_profile.schema.json   # NEW, if the profile is exposed
│                                   as a published contract (checkpoint:decision)
├── fixtures/
│   └── lesson_capability_corpus.py      # NEW -- the portable rich-lesson
│                                   stress corpus generator, fictional
│                                   content, fixed seed
└── tests/
    ├── capability_stress_corpus_tracer.py   # NEW, follows
    │                                   tests/three_domain_tracer.py's and
    │                                   tests/file_fault_tracer.py's
    │                                   structure (fail(msg), named
    │                                   scenario_*() functions, main(),
    │                                   final "TRACER: N passed, M
    │                                   skipped, 0 failed" line)
    └── assessment_authority_adversarial.py  # NEW -- ACTIVITY-03's
                                        adversarial fixture
```

### Pattern 1: One-line additive callout-kind registration

**What:** A new semantic teaching role that fits the existing `[!KIND]`
callout container is added as one dict entry, never a new parser branch.
**When to use:** Every one of the seven CAP-01 roles with no shipped home.
**Example (the exact shipped pattern this phase's new roles must copy):**

```python
# Source: surfaces/lesson.py:648-653, quoted verbatim
_CALLOUT_KINDS = {
    "KEY": ("key", "Key point"),
    "EXAMPLE": ("example", "Example"),
    "NOTE": ("note", "Note"),
    "WARNING": ("warning", "Warning"),
}
```

The comment directly above this dict states the property that makes this
pattern safe to reuse: "Adding a kind is a one-line registration here -- the
container and its degradation contract do not change"
`[VERIFIED: surfaces/lesson.py:646-647]`.

### Pattern 2: One boundary-rule function for every preamble section

**What:** Any new preamble-level grammar (media registry, capability
declarations) reads through `model.py`'s single `_preamble_section` function
rather than writing a second section-boundary scanner.
**When to use:** Parsing any new `## SECTION` this phase adds to the lesson
preamble.
**Example:**

```python
# Source: model.py:578-586, quoted verbatim (docstring)
"""THE boundary rule, defined once for every preamble registry: a preamble
section runs until the next level-two heading or the first question,
whichever comes first. `head` arrives already truncated at the first
question by the caller's chunk walk; this function applies the other
half. `parse_terms`, `parse_sources` and `parse_cases` -- plus the
lesson-body `[[term]]` refs scan -- all read through this one
definition, so the file carries one boundary rule rather than four that
can drift."""
```

### Pattern 3: The runtime, not the author or a model, decides disclosure

**What:** A gate function that is deliberately conservative -- on any
ambiguity it withholds rather than discloses -- and is a pure function with
no I/O and no side effects.
**When to use:** ACTIVITY-03's adversarial fixture must prove this property
holds for every new attack surface 16A's own new grammar introduces (for
example, could a source-excerpt block accidentally quote a keyed rationale?).
**Example (the exact shipped precedent):**

```python
# Source: runtime.py:1509-1531, quoted verbatim (abridged)
def glossable(qs, term):
    """The one gate between a term's definition and the learner: False when
    the definition text could disclose keyed answer material from any
    question in `qs`, True otherwise.

    This is the same class of decision as `public_item()` withholding a key
    -- the runtime, not the author and not a model, decides what reaches the
    learner (Directive Section 4.1, D-20). It is deliberately conservative --
    on any ambiguity it returns False."""
```

### Pattern 4: Compare-and-swap rights re-check at the moment of the operation, never a cached snapshot

**What:** A binding, package, or media-inclusion decision reads the CURRENT
rights registry at the moment of the operation; a value copied into a record
earlier is history only and is never re-read to authorize a later action.
**When to use:** Once 14A/14B land, any media-asset rights gate 16A's own
grammar introduces.
**Example:**

```text
# Source: 14B-03-PLAN.md:200-215 (Pitfall 5), quoted (abridged) -- the
# exact discipline this phase's media-rights enforcement must follow once
# 14A/14B land
"No stale snapshot ever authorizes ... Change the source's rights record
so the same operation now reads denied, then call the same binding again
for a second objective. It refuses ... even though the earlier binding
row still shows granted. The current registry decides; the snapshot
never does."
```

### Anti-Patterns to Avoid

- **A widget per semantic role.** CAP-01's own text explicitly supersedes
  "widget-specific lesson grammar" `[VERIFIED: REQUIREMENTS.md section header
  note preceding CAP-01]`. Every new role is a callout-kind registration, not
  a new top-level Markdown construct, unless a role genuinely cannot fit the
  existing `[!KIND]` container's shape (none of the seven new roles need
  more structure than a labeled block of prose plus optional citation).
- **Inventing a second boundary-rule scanner.** Any new preamble section
  parsed with its own regex instead of `_preamble_section` reintroduces the
  exact "four boundary rules that can drift" risk the shipped function's own
  docstring names as the reason it exists.
- **A new item type for an activity purpose.** ACTIVITY-01 is explicit:
  existing response forms serve many purposes; a ninth item type is
  warranted "only when scoring semantics or response structure cannot be
  expressed safely." None of the ten purposes in research stream 03's matrix
  require a new response form on their own.
- **A media-rights vocabulary independent of `identity.RIGHTS_OPERATIONS`.**
  See Alternatives Considered above.
- **Guided mode acquiring Phase 17A's visual tokens.** The phase description's
  own landmine note forbids this; 16A's guided-mode deliverable is a data
  contract (which blocks compose a stage, what state persists across a stage
  transition) proven functionally by the freeze-gate fixture, not a styled
  experience.
- **A capability whose "unavailable renderer" path is undefined.** CAP-02's
  Degraded clause requires "an unavailable renderer shows the static
  instructional path" `[VERIFIED: REQUIREMENTS.md:576]`. Every new capability
  profile entry must name its fallback; a capability with no fallback field
  filled in fails the CAP-02 fixture by construction.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| A new semantic-role container | A new top-level Markdown block per role | The existing `[!KIND]` callout container, extending `_CALLOUT_KINDS` | Shipped, tested, one-line-additive by the container's own design comment. |
| A new preamble-section boundary scanner | A regex-based section finder per new grammar block | `model.py`'s `_preamble_section(head, name)` | The shipped, single boundary rule every existing preamble reader (`parse_terms`, `parse_sources`, `parse_cases`) already shares; a second scanner is the exact drift risk its docstring names. |
| RTL/CJK/combining-mark rendering | A Python-side bidi algorithm, ICU binding, or Unicode normalization pass | Standard HTML `dir="rtl"`/`dir="auto"` and `lang` attributes plus raw UTF-8 text, rendered by the browser | Bidi reordering, CJK line-breaking, and combining-mark glyph composition are browser/font-stack responsibilities once the correct attributes and untouched UTF-8 bytes are emitted; a Python-side reimplementation would duplicate a solved, standards-governed problem and risks getting it wrong. `graph.py`'s own precedent (14B) is instructive by contrast: it explicitly imports NO `unicodedata` and applies no normalization to identity strings, because identity there is opaque-id-based, not content-based -- lesson RENDERING is a different problem needing the browser's bidi engine, not none at all. |
| A media rights vocabulary | A second `MEDIA_RIGHTS_STATES` tuple | `identity.RIGHTS_OPERATIONS`/`RIGHTS_STATES` (14A, planned) | See Architecture Patterns Pattern 4 and Alternatives Considered. |
| An "auto-grade prose" scoring path to test against | A stub scorer for the adversarial fixture | The real `runtime.score_response()` plus `evidence.mark_event()`'s existing `"human"`-only marker check | ACTIVITY-03's fixture must prove the REAL gate refuses, not a test double standing in for it; a stub would prove nothing about the actual runtime. |
| A key-leak detector for the new source-excerpt/counterexample roles | A new leak-scanning regex | `runtime.glossable()`'s existing pattern (check against `canonical_key()`, correct option labels, collapsed key/answer text) `[VERIFIED: runtime.py:1521-1524]` | The same class of decision already has a working, deliberately-conservative implementation; a second leak detector risks disagreeing with the first about what counts as keyed content. |
| A course-graph-adjacent outline generator for CAP-03's "outline" mode | A new outline-building function inside `capabilities.py` or a fixture module | `graph.outline_projection(doc)` (14B, planned) | CAP-03 requires composition from "shared note and activity schemas"; a second outline generator would be exactly the duplicated-truth anti-pattern the requirement rejects. |

**Key insight:** CAP-01's fourteen roles are not fourteen new problems. Seven
are shipped, working, and only need retroactive capability-profile
documentation. Of the remaining seven, all fit the existing one-line callout
registration pattern. The genuinely new surface area is narrow: the
capability-profile registry itself (CAP-02), the media-metadata grammar
(CAP-02), the ten-field activity declaration (ACTIVITY-01), the localization
field and fixture set (A11Y-02), and the guided-mode data contract (CAP-01's
second half). Everything else is either reuse or a fixture proving reuse
worked.

## Common Pitfalls

### Pitfall 1: Treating CAP-01's fourteen roles as fourteen greenfield designs

**What goes wrong:** A planner reads CAP-01's role list and drafts fourteen
new grammar elements, rebuilding the glossary, the hint ladder, and the
`visual` item type as lesson-embedded blocks instead of recognizing them as
already-shipped capabilities this phase must merely catalog.
**Why it happens:** The requirement text lists all fourteen roles in one flat
sentence with no annotation of which already exist.
**How to avoid:** Confirmed this session by reading `surfaces/lesson.py:648-653`
(`_CALLOUT_KINDS`), `model.py:625-690` (`parse_terms`), `STATE.md:355`
(the hint ladder's six tiers), and the shipped `visual` item type
(`REQUIREMENTS.md` VIS-01 through VIS-09, Phase 06.1, complete): seven roles
map to shipped mechanisms (key idea, warning, worked example, term and
definition, inline check, hint, accessible visual interaction); seven do not
(prerequisite, misconception, expert tip, counterexample, source excerpt,
uncertainty, summary). The plan must state this mapping explicitly so the
executor does not rebuild any of the seven shipped ones.
**Warning signs:** A plan task that touches `surfaces/quiz.py` or `runtime.py`
to "add hint support to lessons," when the hint ladder is already
lesson-reachable per shipped Phase 6/8/13.5 work.

### Pitfall 2: Building 16A's freeze gate against 14B plan text that has since diverged

**What goes wrong:** The plan cites `graph.TREATMENT_RIGHTS`,
`graph.add_source`, or `course.bind_source`'s exact signature from
`14B-01-PLAN.md`/`14B-03-PLAN.md`, and by the time 16A executes, 14B has
landed with a genuinely different signature (the plan explicitly anticipates
this: "a deviation here is not a failure ... it is the signal that plans 02
through 06 must be re-read against `14A-FREEZE.md`" `[VERIFIED: 14B-01-PLAN.md:229-233]`).
**Why it happens:** 16A is planned before 14B executes, so every citation is
necessarily against a plan, not against ground truth.
**How to avoid:** The first 16A plan's precondition task (Pattern already
established by 14B-01/15A-01/15B-01) must check for `14B-FREEZE.md`'s literal
`## Frozen at 14B` heading (not `## Freeze withheld`) and re-verify the
specific constants this research cites (`graph.EDGE_TYPES`,
`graph.TREATMENT_KINDS`, `graph.TREATMENT_RIGHTS`, `course.bind_source`'s
signature) before any 16A code imports them.
**Warning signs:** A 16A task that imports `graph` or `course` without first
running the precondition check, or that assumes `14B-FREEZE.md` exists at
all (it may not; see the Critical Caveat).

### Pitfall 3: Confusing guided mode's data contract with Phase 17A's visual system

**What goes wrong:** 16A's plan produces styled HTML, CSS tokens, or a
staged-reveal animation for guided mode, duplicating work Phase 17A must
redo against its own token set, or worse, locking in visual decisions before
Phase 17A's "same logical flows in three visual directions" prototype
(`PLANNING-DIRECTIVES.md` section 3a) has run.
**Why it happens:** The freeze gate's own Fixture sentence requires the
stress corpus be "rendered in both continuous reader and guided modes"
`[VERIFIED: ROADMAP.md:1831-1834]`, which reads as an invitation to build a
real renderer.
**How to avoid:** Build the minimum functional distinction needed to prove
the DATA contract (which blocks group into which stage; what state, if any,
persists across a stage boundary; how an unavailable renderer's static
fallback is shown) without committing to color, spacing, typography, or
motion. The phase description's own landmine note is explicit: "do not
research or propose visual design, only semantic behavior, fallbacks, and
fixtures."
**Warning signs:** A 16A task file listing `theme.py`, `SHARED_CSS`, or any
token constant from `presentation.py` in its `files_modified`.

### Pitfall 4: Minting a media rights vocabulary before 14A lands, then having two

**What goes wrong:** 16A's media-metadata grammar defines its own
`rights`/`credit` states independently (because 14A/14B have not landed and
`identity.py` does not exist to import), and once 14A lands, two rights
vocabularies coexist: the media one and `identity.RIGHTS_OPERATIONS`.
**Why it happens:** 16A's freeze gate does not itself depend on 14A directly
(only on 14B, and even that transitively through 14A), so a plan might
reasonably try to avoid the whole precondition-check machinery by building
media rights independently.
**How to avoid:** If 14A/14B have not landed by 16A's planning or execution
time, media rights enforcement stays a DECLARED but UNENFORCED field (the
metadata is present in the corpus, but no code path gates on it yet), with an
explicit note in the plan naming this as deferred to whichever later
subphase's execution finds 14A/14B landed. Do not invent a working
enforcement mechanism against a vocabulary this phase does not own.
**Warning signs:** A `MEDIA_RIGHTS_STATES` or `ASSET_RIGHTS` constant
anywhere in 16A's new code that is not a direct re-export of
`identity.RIGHTS_STATES`.

### Pitfall 5: The adversarial fixture testing a stub instead of the real gates

**What goes wrong:** ACTIVITY-03's adversarial fixture is implemented against
a simplified mock of `runtime.score_response()` or `evidence.mark_event()`
"to keep the test isolated," which proves nothing about whether the ACTUAL
shipped gates hold.
**Why it happens:** Writing against the real functions requires constructing
real sessions, real evidence logs, and real bank fixtures, which is more
setup than a mock.
**How to avoid:** The fixture must call the real, imported `runtime.py` and
`evidence.py` functions, following the exact "verified against real, executed
source code" discipline this research itself follows. A scripted "agent"
attempting to leak a key should literally call `runtime.public_item()` before
a response exists and assert the key is absent from the returned dict; a
scripted "import" attempting to invent a score should literally call
`evidence.append_event()` with a manufactured event and assert it is either
rejected or recorded as `pending`, never as an accepted score.
**Warning signs:** Any `class Mock*` or `def fake_*` helper inside the
adversarial test file standing in for `runtime.py` or `evidence.py`.

## Code Examples

### The one-line callout-kind registration pattern this phase's seven new roles must follow

```python
# Source: surfaces/lesson.py:648-653, quoted verbatim
_CALLOUT_KINDS = {
    "KEY": ("key", "Key point"),
    "EXAMPLE": ("example", "Example"),
    "NOTE": ("note", "Note"),
    "WARNING": ("warning", "Warning"),
}
```

### The shipped preamble boundary-rule function every new grammar section must read through

```python
# Source: model.py:574-602, quoted verbatim (abridged, function body)
def _preamble_section(head, name):
    text = _STYLE_FENCE_RE.sub("", head or "")
    m = re.search(r"(?m)^##\s+%s\s*$" % re.escape(name), text)
    if m is None:
        return None
    body = text[m.end():]
    nxt = _PREAMBLE_HEADING_RE.search(body)
    return body[:nxt.start()] if nxt else body
```

### The shipped disclosure gate ACTIVITY-03's adversarial fixture must attack directly

```python
# Source: runtime.py:1509-1531, quoted verbatim (abridged)
def glossable(qs, term):
    """The one gate between a term's definition and the learner: False when
    the definition text could disclose keyed answer material from any
    question in `qs`, True otherwise. ... It is deliberately conservative --
    on any ambiguity it returns False."""
```

### The shipped human-only marking gate

```text
# Source: STATE.md:355, quoted verbatim (decision log entry, describing
# evidence.py's mark_event())
"mark_event() rejects any marker other than 'human' (T-1-24); a model
verdict is not accepted evidence until Phase 8/TEACH-09 teaches the
runtime to hold one as pending review"
```

### The closed-vocabulary constant shape every new CAP-01/CAP-02 field should follow

```python
# Source: model.py:2052, quoted verbatim
GATE_VALUES = ("required", "recommended", "off")
```

### The rights re-check-at-operation-time discipline media rights must follow once 14A/14B land

```text
# Source: 14B-03-PLAN.md (Pitfall 5), quoted (abridged)
"No stale snapshot ever authorizes ... The current registry decides; the
snapshot never does."
```

### Proprietary format decision criteria (PORT-01's citation target, quoted in full)

```text
# Source: research/phase-16/04-portable-contract-agents.md:433-455, quoted
# verbatim -- the eight criteria a proprietary canonical format must ALL
# pass, per PORT-01's own text ("stays rejected unless every criterion in
# research report 04 section 8 passes")
1. A required learning capability cannot be represented as Markdown
   semantics, validated data, external assets, and trusted derived
   behavior without losing essential meaning.
2. The limitation affects common accepted lessons, not an unusual
   optional edge case.
3. An open package or existing standard such as EPUB, HTML, IIIF, or a
   directory bundle cannot satisfy the need.
4. The benefit is material to learning quality, accessibility, integrity,
   or authoring reliability and exceeds migration, lock-in, tooling, and
   security costs.
5. Agents and humans can still inspect, diff, validate, migrate, and
   recover the content with documented open tooling.
6. A lossless export preserves essential text, structure, citations,
   media credits, and static interaction fallbacks.
7. One authoritative parser and document model remains possible.
8. Version negotiation, forward-compatible unknown content, migration,
   and rollback are specified and tested before adoption.

"No evidence reviewed in this stream meets these criteria."
```

None of the eight criteria is met by any candidate examined in research
stream 04; this research's own recommendation is unchanged: **reject a
proprietary canonical format** for 16A's semantic profile. The canonical
lesson stays UTF-8 Markdown with additive grammar.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|---------------|--------|
| Superseded `LEARNUI-02`/`LEARNUI-03` (a single "comprehensive learner UI" requirement covering both semantic capability AND visual presentation) | Split into `CAP-01`/`CAP-02` (semantic contract, owned by 16A) plus `VISUAL-01`/`VISUAL-02` (visual system, owned by 17A) | 2026-08-13 family expansion `[VERIFIED: REQUIREMENTS.md:295-297]` | 16A does not own token, palette, density, or motion decisions; it owns which semantic roles exist and how they degrade. A 16A plan proposing a color or spacing value is out of scope by this split. |
| Flat Phase 16 ("Learning Flow & Lesson Capability Contract", one phase covering flow, capabilities, questions, portability, interactions, accessibility, media, and agent guidance) | Split into 16A (semantic capability/activity), 16B (IA/modes/recovery), 16C (strategies/notes/convergence) | 2026-08-13, `[VERIFIED: ROADMAP.md:109-113]` | 16A's freeze gate is narrower than the old flat-Phase-16 tracer (which required "storyboard and prototype one representative course unit across desktop, narrow screen, keyboard, touch, screen reader, offline, and plain-file contexts"); 16A's actual freeze gate is specifically the portable rich-lesson stress corpus, and the storyboard/interruption work moves to 16B. |
| `[!EXAMPLE]` as a generic "example" callout | Research stream 02's richer "worked example" capability (ordered, per-step annotated steps, not just a labeled paragraph) | Research date 2026-08-13 `[VERIFIED: research/phase-16/02-lesson-flow-capabilities.md:190]` | The shipped `[!EXAMPLE]` callout is necessarily REUSED for the "worked example" role's label, but CAP-01's fuller worked-example capability (annotated ordered steps) may need the callout PLUS a lightweight ordered-list convention inside it, not a wholly separate mechanism; this is flagged as an open question below, not resolved by this research. |

**Deprecated/outdated:** none specific to this phase's own history; this is
the first research pass for 16A.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The seven new callout-kind names (`PREREQUISITE`, `MISCONCEPTION`, `TIP`, `COUNTEREXAMPLE`, `EXCERPT`, `UNCERTAINTY`, `SUMMARY`) are this research's proposed tokens, not verified against any prior decision record. | Standard Stack "New in this phase", Architecture Patterns Pattern 1 | Low risk of contract breakage (the callout-kind dict is additive and any string token works structurally), but the exact spelling becomes an authored-content contract the moment a real lesson uses it; should be a plan-level `checkpoint:decision` naming the final seven tokens rather than silently adopted. |
| A2 | `capabilities.py` is the right name and the right module boundary for the capability support profile registry, rather than folding it into `model.py` directly or into the planned `graph.py`. | Standard Stack "New in this phase", Alternatives Considered | If wrong, either `model.py` grows a registry concern beyond "parse markdown into dicts" (its own stated scope), or a later phase must migrate the registry out of wherever it landed. This is a `checkpoint:decision` candidate, following the exact pattern `15B-RESEARCH.md`'s A1 (`blueprint.py` versus `director.py`) already used for an identical class of module-boundary question. |
| A3 | Media-asset metadata is parsed as a new preamble-level block/section (following `## SOURCES`'s and `## TERMS`'s precedent) rather than as an inline per-image attribute syntax. | Standard Stack "New in this phase" | If wrong, the exact grammar shape changes but the underlying data (rights, credit, accessible-alternative, derivation, availability, integrity) stays the same; a `checkpoint:decision` should present both shapes with this research's recommendation (registry section, for consistency with `## SOURCES`) named as the default. |
| A4 | Guided mode's 16A-scoped deliverable is a data contract only (which blocks group into a stage, what persists across a stage transition, how an unavailable-renderer fallback is shown), with no visual rendering beyond the minimum needed to prove the freeze-gate fixture renders in "both modes." | Architecture Patterns Pattern (Diagram), Common Pitfalls 3 | If wrong (if the freeze gate genuinely requires a styled, complete guided-mode UI), the phase boundary with 17A collapses and 17A's "same flow in three visual directions" prototype work would have nothing left to compare against; this is a high-stakes reading and should be confirmed as a plan-level `checkpoint:decision` before any rendering code is written, quoting the phase-description landmine note verbatim in the checkpoint. |
| A5 | Media rights enforcement is DECLARED but UNENFORCED in this phase's fixtures if 14A/14B have not landed by 16A's execution time, deferred to whichever later subphase finds them landed. | Common Pitfalls 4 | If wrong (if CAP-02's media metadata must actually gate something at 16A execution time regardless of 14A/14B's status), the phase would need its own minimal, deliberately temporary rights-gate mechanism, which risks becoming the "second rights vocabulary" this research explicitly warns against; recommend re-verifying 14A/14B landing status at 16A plan time before deciding this. |

**If this table is empty:** N/A, five assumptions are recorded above. A2 and
A4 touch one-way module-boundary and phase-boundary decisions and should
surface to the user as `checkpoint:decision` tasks per
`PLANNING-DIRECTIVES.md` section 2 rule 1 (hard-to-reverse format decisions
other phases will build against). A1, A3, and A5 are lower-risk and may be
resolved by the planner with the recommendation stated here, named as an
assumption in the plan's decision table.

## Open Questions

1. **Does the shipped `[!EXAMPLE]` callout alone satisfy CAP-01's "worked
   example" role, or does it need an additional ordered/annotated-steps
   convention inside it?**
   - What we know: the shipped `[!EXAMPLE]` callout is a generic labeled
     block `[VERIFIED: surfaces/lesson.py:650]`; research stream 02's
     capability table describes a richer worked-example contract with
     per-step annotations and a "Plain and rich behavior" column calling for
     "Ordered steps with result and per-step annotation" `[VERIFIED:
     research/phase-16/02-lesson-flow-capabilities.md:190]`.
   - What's unclear: whether the existing `[!EXAMPLE]` block's freeform prose
     is sufficient, or whether the stress corpus's worked-example fixture
     needs a lightweight numbered-list convention the linter can check
     structurally (matching the "worked-example-first default" bake-in
     already locked in CAP-01's own text).
   - Recommendation: treat the plain `[!EXAMPLE]` callout as the CAP-01
     minimum bar (it already satisfies "renders a worked example role"
     structurally), and record annotated per-step structure as a
     Registered-tier enhancement for a later capability-profile version bump
     rather than blocking 16A's freeze on it, since CAP-02 explicitly allows
     versioned capability profiles.

2. **What is the exact closed-vocabulary shape for a capability's
   `renderer-availability` field?**
   - What we know: CAP-02 names it as one of six required profile fields;
     `GATE_VALUES = ("required", "recommended", "off")` is the shipped
     precedent for a similarly-sized closed tuple `[VERIFIED: model.py:2052]`.
   - What's unclear: whether renderer-availability is boolean
     (`available`/`unavailable`) or needs a third state for "partially
     available" (for example, a visual interaction whose keyboard path works
     but whose pointer path is broken).
   - Recommendation: default to a three-state closed tuple
     (`("available", "degraded", "unavailable")`) following the "unavailable
     renderer shows the static instructional path" Degraded clause's own
     binary framing plus one explicit middle state for partial breakage,
     and record this as a plan-level decision rather than leaving the
     executor to invent the tuple's arity.

3. **How does the medical evolving-case fixture's "dated jurisdiction
   warning" compose with the existing `[!WARNING]` callout, or does it need
   its own field?**
   - What we know: CAP-01's Fixture names "a medical evolving-case fixture
     with a dated jurisdiction warning and no premature reveal"
     `[VERIFIED: REQUIREMENTS.md:563-567]`; the shipped `[!WARNING]` callout
     has no date/jurisdiction field, only free prose.
   - What's unclear: whether "dated" means the warning's prose states a date
     in free text (satisfied by the shipped callout as-is) or whether a
     structured `effective_date`/`jurisdiction` field is required for
     staleness checking by a later phase (RELIABILITY-03, 15B).
   - Recommendation: default to free-prose-with-a-stated-date for 16A (the
     shipped callout already supports this), and record a structured date
     field as a backburner enhancement contingent on 15B's staleness
     machinery landing, since 16A's own scope is semantic capability, not
     staleness detection.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.11+ | Everything in this phase | Present (confirmed via project CI floor; this session's interpreter not independently re-checked, consistent with every prior phase's own confirmed floor) | 3.11+ per project floor | N/A |
| Phase 14A/14B landing on disk with `14B-FREEZE.md`'s `## Frozen at 14B` heading | The precondition check every 16A code import of `graph`/`course` must pass first | Not yet; confirmed `MISSING` this session for `identity.py`, `journal.py`, `discovery.py`, `graph.py`, `course.py`, `course_package.py`; no `14A-FREEZE.md` or `14B-FREEZE.md` exists | N/A | The precondition task halts by name (Pattern established by 14B-01/15A-01/15B-01); 16A's own new grammar (callout kinds, capability profiles, activity declarations, localization fields) does NOT itself require `graph`/`course`/`identity` to exist and can be built and fixture-tested independently. Only media-rights enforcement (CAP-02's rights field) is blocked pending 14A/14B, per Pitfall 4/Assumption A5. |
| Phase 13.9 (walking skeleton) walked | 14B's freeze gate, transitively 16A's stated dependency | Not yet; confirmed only `13.9-01-PLAN.md` through `13.9-03-PLAN.md` exist, no `*-SUMMARY.md`, no `13.9-DECISIONS.md` | N/A | 16A cannot itself walk 13.9; this is upstream sequencing the orchestrator must resolve before 16A execution, though 16A PLANNING may proceed against plan text per the established precedent. |

**Missing dependencies with no fallback:**
- Media-rights enforcement against a real `identity.py`/14A registry cannot
  be built until 14A lands; this is a genuine blocking gap for the
  ENFORCEMENT half of CAP-02's media metadata (the DECLARATION half is not
  blocked).

**Missing dependencies with fallback:**
- `graph.outline_projection` for CAP-03's "outline" registered mode: if
  14B has not landed by 16A execution time, the outline mode's fixture may
  need a temporary stand-in projection function inside 16A's own fixture
  code, explicitly marked as superseded once 14B's real `graph.py` lands, per
  the precondition-check pattern's own "re-read against the freeze record"
  discipline.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Direct-execution Python scripts (`tests/*.py`), no pytest/unittest framework dependency, per the project's shipped convention `[VERIFIED: CLAUDE.md "Test runner" section]` |
| Config file | None; every test file defines its own local `fail(msg)` helper (confirmed convention across every `tests/*_roundtrip.py` and `tests/*_tracer.py` file this session and in the 14B/15B research) |
| Quick run command | `python tests/<new_test_file>.py` for whichever single new test a task adds |
| Full suite command | `for t in tests/*.py; do python "$t" || exit 1; done`, the exact command `14A-04-PLAN.md`, `14B-06-PLAN.md`, and `15B-RESEARCH.md` already establish as this project's full-suite check |

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|---------------------|-------------|
| CAP-01 | Every semantic teaching role parses and renders in both continuous reader and guided modes; an unknown optional semantic renders its fallback with a warning; an unknown required semantic fails safely | Tracer scenario over the stress corpus | `python tests/capability_stress_corpus_tracer.py` (new) | Wave 0 gap |
| CAP-02 | A declared capability's full support profile is inspectable; a capability with its renderer marked unavailable shows the static instructional path | Unit assertions over `capabilities.py`'s registry, plus one tracer scenario | `python tests/capability_stress_corpus_tracer.py` (new) | Wave 0 gap |
| CAP-03 | Two registered output modes (outline, glossary) compose from one stress-corpus lesson's shared schemas; one unregistered mode stays a named backburner catalog entry | Tracer scenario | `python tests/capability_stress_corpus_tracer.py` (new) | Wave 0 gap |
| ACTIVITY-01 | Every declared activity in the stress corpus carries all ten fields; one unsupported response form falls back to its declared static equivalent | Tracer scenario | `python tests/capability_stress_corpus_tracer.py` (new) | Wave 0 gap |
| ACTIVITY-03 | A scripted agent, a note, and an import each attempt to leak a key, invent a score, auto-grade prose, or edit a frozen sitting; every attempt is refused | Adversarial fixture, calling real `runtime.py`/`evidence.py` functions | `python tests/assessment_authority_adversarial.py` (new) | Wave 0 gap |
| A11Y-02 | The localization fixture set (RTL, mixed code/math direction, CJK, combining marks, long strings, localized numbers/units) renders inside the stress corpus without corruption | Tracer scenario, byte-level assertions on preserved UTF-8 | `python tests/capability_stress_corpus_tracer.py` (new) | Wave 0 gap |
| PORT-01 | The stress corpus, opened outside the app in a plain Markdown viewer with every derived HTML/index/cache deleted, stays readable; core meaning, captions, citations, and fallbacks survive; derived views rebuild | Tracer scenario, byte-identical-fixture discipline following `model.py`'s golden-parse-snapshot precedent | `python tests/capability_stress_corpus_tracer.py` (new) | Wave 0 gap |

### Sampling Rate

- **Per task commit:** the single new/extended test file for that task's
  scope, plus `python itembank.py guard .` on any task touching `fixtures/`.
- **Per wave merge:** `for t in tests/*.py; do python "$t" || exit 1; done`.
- **Phase gate:** the portable rich-lesson stress corpus tracer green, plus
  the shipped-suite check (confirms 16A introduced no regression in
  `model.py`/`runtime.py`/`evidence.py`/`surfaces/lesson.py` byte
  compatibility, following the `shipped_suite_check()` precedent
  `14B-06-PLAN.md` and `15B-RESEARCH.md` both establish).

### Wave 0 Gaps

- [ ] `tests/capability_stress_corpus_tracer.py` -- the freeze-gate tracer;
  covers CAP-01, CAP-02, CAP-03, ACTIVITY-01, A11Y-02, and PORT-01 in one
  run, following `tests/three_domain_tracer.py`'s (14B) and
  `tests/file_fault_tracer.py`'s (14A) structure.
- [ ] `tests/assessment_authority_adversarial.py` -- ACTIVITY-03's dedicated
  adversarial suite, calling real `runtime.py`/`evidence.py` functions per
  Pitfall 5.
- [ ] `fixtures/lesson_capability_corpus.py` -- the synthetic stress-corpus
  generator (fictional content, fixed seed, following `fixtures/corpus_14b.py`'s
  convention), including the medical evolving-case fixture and the
  disputed-timeline fixture the freeze gate names by name.
- [ ] A golden-parse snapshot for the byte-identical additivity fixture,
  following `fixtures/lesson_golden_phase3_parse.json`'s shipped precedent,
  proving a bank/lesson using none of the seven new callout kinds parses
  unchanged.
- [ ] `capabilities.py` and its unit assertions (no pre-existing module
  covers a capability-profile registry).

*(No pre-existing test infrastructure covers this phase's six requirements
directly; all listed gaps are new. The infrastructure the new tests CALL --
`runtime.py`, `evidence.py`, `model.py`'s parsing -- is entirely shipped and
unchanged.)*

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-------------------|
| V2 Authentication | No | Single-learner local product; no accounts, no auth surface (`.claude/CLAUDE.md` Users constraint, unchanged by this phase). |
| V3 Session Management | No | No new session concept; `runtime.py`'s session model is untouched by this phase. |
| V4 Access Control | Yes | ACTIVITY-03's entire fixture IS an access-control test: the runtime alone may grant keyed disclosure, and the adversarial fixture proves `public_item()`/`explain_payload()`/`mark_event()` refuse every scripted bypass. |
| V5 Input Validation | Yes | Every new grammar element (seven callout kinds, media metadata, activity declarations, localization fields) is parsed by `model.py`'s existing regex-based, fail-safe parsing discipline (a malformed block returns `None` or a structured error dict, never a crash, matching `parse_lesson`'s and `parse_terms`' existing shape). |
| V6 Cryptography | No | No new secret material; nothing in this phase touches key material, tokens, or `model_adapter.py`'s `secret_env` resolution. |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|------------------------|
| A scripted agent calling `runtime.public_item()` and inspecting the returned dict for a leaked key before any response is recorded | Information Disclosure | `public_item()`'s existing contract (unchanged by this phase) never includes the key/rationale/why-best fields; ACTIVITY-03's adversarial fixture asserts this directly against the real function per Pitfall 5. |
| A scripted "note" or "import" writing a manufactured event directly into the evidence log to simulate a score without going through `runtime.score_response()` | Tampering / Elevation of Privilege | `evidence.append_event()` and `mark_event()`'s existing `"human"`-only marker discipline (unchanged) are the gate; the fixture calls the real function and asserts the manufactured event is either refused or recorded as non-authoritative (pending), never accepted as a settled score. |
| A right-to-left override character (U+202E) or other bidi-control character embedded in authored lesson text used to visually spoof a warning's meaning or hide malicious-looking text from a casual reader | Spoofing | This is a genuine new risk surface A11Y-02's fixture set introduces (mixed-direction text is now a first-class, tested case). The localization fixture set should include a deliberate bidi-override character as one of its "mixed code and math direction" cases and assert the raw text is preserved byte-for-byte (never stripped, which would corrupt legitimate RTL content) while noting the display-spoofing risk as a documented, accepted characteristic of any RTL-capable renderer, not a itembank-specific defect -- the same posture every text editor and browser takes. |
| Real course, learner, or bank content entering the repository through the new stress-corpus fixture | Information Disclosure | The fixture generator follows the fictional-content-only, fixed-seed convention every prior 14A/14B fixture already established; `python itembank.py guard .` is a required acceptance check on every task touching `fixtures/`. |
| A media asset's `derivation`/`integrity` field trusted without recomputation, allowing a substituted asset to pass as authentic | Tampering | Once media assets are actually stored (a later phase's concern per CAP-02's declaration-only scope in 16A per Assumption A5), integrity verification should follow `identity.object_fingerprint`'s recompute-don't-trust pattern already established in 14A/14B; 16A itself declares the field but does not yet enforce it, and this deferral is recorded explicitly rather than silently. |
| Supply chain: a bidi, Unicode-segmentation, or media-processing dependency introduced for the localization or media work | Tampering | None is needed; see Don't Hand-Roll for why RTL/CJK/combining-mark rendering is a browser responsibility requiring no new Python dependency. Per `PLANNING-DIRECTIVES.md` section 4a, any dependency ever added here later is vendored at a pinned version with a recorded checksum and a named license review, following the KaTeX precedent. |

## Sources

### Primary (HIGH confidence -- shipped, executed code and requirements read this session)

- `model.py` (module docstring, `parse_bank`, `parse_lesson`, `parse_terms`,
  `_preamble_section`, `GATE_VALUES`, `MARKERS` including `[LANG:]`) -- the
  one shipped parser, its boundary-rule discipline, and its closed-vocabulary
  constant shape.
- `surfaces/lesson.py` (`_CALLOUT_KINDS`, `_callout_kind_of`, the vendored
  gloss-enhancement hook) -- the shipped, additive callout-kind registration
  pattern.
- `runtime.py` (`glossable()` in full, `public_item`, `explain_payload`,
  `canonical_response`, `score_response` by reference) -- the shipped
  runtime-only disclosure and scoring authority.
- `.planning/STATE.md` (lines 1-470, in particular the `01-09` and `03.1-*`
  decision-log entries) -- confirms `mark_event()`'s human-only marker gate,
  the shipped `[!KEY]`/`[!EXAMPLE]`/`[!CHECK:]` callout history, and the
  glossary/hover mechanism's shipped status.
- `.planning/REQUIREMENTS.md` (full CAP/ACTIVITY/A11Y/PORT family sections,
  the traceability table, the family-alias note, RTS-05 through RTS-12 and
  their 2026-08-13 reframe destination note) -- the seven owned requirements
  verbatim with Fixture sentences.
- `.planning/ROADMAP.md` (Phase 16A detail section, the nine-subphase table,
  the roadmap governance clauses, the Phase 14B and Phase 13.9 entries) --
  phase goal, dependencies, freeze gate, and the explicit precondition-check
  instruction this phase's first plan must follow.
- `.planning/PLANNING-DIRECTIVES.md` (full read) -- the autonomy rule, build-
  both rule, five non-negotiables, executor bar, and the disposition/breadth
  discipline in section 3a.
- `.planning/SOURCE-TO-COURSE.md` (full read) -- the north star, the learning-
  experience-and-capability-research charter, and the scope-boundary list.
- `.planning/PLAN-TEMPLATE.md` (full read) -- the executor-bar structure
  every 16A plan must satisfy.
- `.planning/phases/15B-quality-blueprint-acceptance/15B-RESEARCH.md` (full
  read) -- the reference exemplar for this document's shape, depth, and
  citation discipline, and the direct precedent for the precondition-check
  pattern, the checkpoint-candidate framing for module-boundary decisions,
  and the Validation Architecture / Security Domain section shapes.
- `.planning/phases/14B-graph-course-package-prototype/14B-01-PLAN.md`
  through `14B-06-PLAN.md` (objective, decisions-locked table, and "Artifacts
  this phase produces" sections read in full for each) -- the planned
  `graph.py`/`course.py`/`course_package.py` API surface this research cites
  as `[VERIFIED: <plan file>:<lines>]` throughout.
- `.planning/research/phase-16/14-synthesis.md` (sections 1 through 8, 11,
  12.1 through 12.5, 15, 16 read in full) -- the product model, semantic
  primitive set, cross-cutting rules, disposition ledger, subphase table, and
  exit gates.
- `.planning/research/phase-16/02-lesson-flow-capabilities.md` (full read) --
  the lesson-capability catalog candidates, their portability/accessibility/
  authorability/evidence requirements, and the accept/reject/defer/prototype
  disposition table.
- `.planning/research/phase-16/03-question-activity-matrix.md` (full read) --
  the ten-purpose activity taxonomy, response-form design space, and the
  "ideas that should not become new item types" table.
- `.planning/research/phase-16/04-portable-contract-agents.md` (sections 7
  through 9 read in full) -- the portable-contract layered model, the
  decision table, and the eight-criterion proprietary-format gate quoted in
  full in Code Examples.
- `.planning/UI-SPEC.md` section 8 (the nine numbered accessibility gates) --
  confirmed as exactly nine items, matching `PLANNING-DIRECTIVES.md` section
  4a's "exactly nine gates" citation.
- `.planning/config.json` (`workflow.nyquist_validation: true`,
  `workflow.security_enforcement: true`) -- confirms both the Validation
  Architecture and Security Domain sections are required for this document.
- Live filesystem check this session confirming `identity.py`, `journal.py`,
  `discovery.py`, `graph.py`, `course.py`, `course_package.py`, `director.py`,
  and `blueprint.py` are all `MISSING`, and no `*-FREEZE.md`/`*-DECISIONS.md`
  exists for 14A, 14B, or 15A; `.planning/phases/13.9-walking-skeleton/`
  contains only its three PLAN files with no SUMMARY or DECISIONS record.

### Secondary (MEDIUM confidence)

- `.planning/STATE.md` (lines beyond 470, not fully read this session due to
  length; the read portion covers the project history through the 13.9
  planning entry, which is sufficient for this phase's scope).
- `.planning/phases/13.9-walking-skeleton/13.9-01-PLAN.md` (referenced via
  `14B-01-PLAN.md`'s citation, not independently re-read in full this
  session) -- the `course.md` stub shape 14B's `migrate_stub` reads, relevant
  context for understanding why 14B's freeze is gated on 13.9.

### Tertiary (LOW confidence)

- None used; no web search was performed. This phase's research scope is
  entirely in-repo architecture composition and reuse of a shipped runtime,
  with no new external library or API to verify against an authoritative
  external source, matching `15B-RESEARCH.md`'s identical posture.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH for shipped modules (`model.py`, `runtime.py`,
  `evidence.py`, `surfaces/lesson.py`), MEDIUM for planned-but-unexecuted
  modules (`identity.py`, `graph.py`, `course.py`) because their real
  implementation may deviate from plan text during 14A/14B execution, and
  LOW-to-MEDIUM for this phase's own genuinely new surface (capability
  registry shape, media-metadata grammar, callout-kind naming) because no
  prior decision record fixes any of it -- flagged throughout as `[ASSUMED]`
  and surfaced in the Assumptions Log.
- Architecture: MEDIUM-HIGH -- the reuse pattern (seven roles already
  shipped, one-line callout registration, the shared `_preamble_section`
  boundary rule, the runtime-only disclosure gates) is directly grounded in
  real, executed code read this session with exact line citations; the
  module-boundary decisions for genuinely new surface (A2, A3, A4) are
  recommendations, not locked facts, and are flagged as checkpoint
  candidates.
- Pitfalls: HIGH -- Pitfall 1 (the shipped-versus-new role mapping) and
  Pitfall 5 (testing real gates, not stubs) are directly verified against
  real, executed code and requirements text read this session with exact
  line citations; Pitfalls 2 and 4 are directly grounded in explicit
  precedent 14B-01/14B-03 already established and tested for structurally
  identical problems; Pitfall 3 is grounded directly in the phase
  description's own landmine note, quoted verbatim.

**Research date:** 2026-08-15
**Valid until:** Re-check immediately if `14A-FREEZE.md`, `14B-FREEZE.md`, or
`13.9-DECISIONS.md`/`13.9-03-SUMMARY.md` appears in the repository before 16A
is planned or executed (their real, frozen constants and walked-skeleton
evidence supersede the plan-text citations and "not yet walked" caveat in
this document). Otherwise, valid for approximately 14 days (fast-moving: this
phase sits downstream of two unexecuted phases and one unwalked skeleton
whose real landing may shift plan-text details cited throughout).
