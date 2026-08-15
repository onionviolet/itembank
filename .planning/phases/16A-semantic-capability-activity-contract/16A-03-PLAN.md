---
phase: 16A-semantic-capability-activity-contract
plan: 03
type: execute
wave: 3
depends_on: ["16A-02"]
files_modified:
  - surfaces/lesson.py
  - model.py
  - capabilities.py
  - fixtures/lesson_capability_corpus.py
  - tests/capability_stress_corpus_tracer.py
autonomous: true
requirements: [CAP-01, PORT-01]
estimate:
  tokens: 88000
  raw_tokens: 88000
  tasks: 3
  confidence: low
must_haves:
  truths:
    - "All fourteen semantic teaching roles CAP-01 names have a live rendering path, and the catalog that says so is machine readable rather than prose: capabilities.SEMANTIC_ROLE_CATALOG has exactly fourteen entries, every entry names its mechanism, and the tracer asserts every one of the fourteen resolves to something that actually renders (CAP-01 completeness probe, the row the edge probe returned as unclassified)."
    - "Seven of the fourteen roles were already shipped and are catalogued rather than rebuilt: the key idea, warning, and worked example callouts, the TERMS glossary, the inline check reserved slot, the authored hint ladder, and the visual item type keep their existing code paths and no task in this plan edits runtime.py, evidence.py, or surfaces/quiz.py."
    - "surfaces.lesson._CALLOUT_KINDS has exactly eleven members after this plan: the four shipped kinds unchanged plus the seven new roles, each a one-line registration through the shipped container whose degradation contract does not change."
    - "A semantic may be declared required by a trailing exclamation mark inside the callout marker, and the shipped _CALLOUT_MARK_RE is not modified to make that work, proven by the regex source being byte identical before and after this plan (D-16A-3)."
    - "An unknown optional semantic renders exactly the paragraph output it rendered before Phase 16A existed and adds the lint warning lesson.unknown_semantic; an unknown required semantic renders one visible refusal container carrying its own body text unchanged and adds the lint error lesson.unknown_required_semantic. Nothing is dropped, nothing is silently swallowed, and neither path raises."
    - "The worked-example-first default is enforced as the lint warning lesson.definition_before_example and is overridable only by an authored directive carrying a reason, where a directive with no reason text is the lint error lesson.example_order_no_reason (D-16A-6, CAP-01's recorded-override clause)."
    - "Additivity holds through this plan: the two golden SHA-256 values recorded in 16A-PRECONDITION.md are unchanged, python tests/lesson_roundtrip.py exits 0, and a bank using none of the seven new kinds renders byte identically."
  prohibitions:
    - statement: "An unknown required semantic must not silently disappear; a block the renderer cannot honor is shown as an explicit, named refusal carrying the author's own text, because a reader that quietly drops a block the author marked essential is lying about what the lesson said."
      status: kept
      verification: flagged-unverified
    - statement: "No style rule, capability profile, or rendering flow may require a decorative block or compel learner highlighting; semantic emphasis stays author-provided orientation, per CAP-02's no-decorative-block clause and CAP-01's no-compelled-highlighting bake-in."
      status: kept
      verification: flagged-unverified
    - statement: "A semantic role must not acquire its own top-level Markdown construct or its own parse branch; CAP-01 says roles are composed from shared primitives, not separate content types, and a per-role branch is the widget-specific lesson grammar CAP-01 supersedes."
      status: kept
      verification: flagged-unverified
  artifacts:
    - "surfaces/lesson.py: six new _CALLOUT_KINDS entries, _callout_required_of, _unsupported_callout_html, UNSUPPORTED_SEMANTIC_COPY"
    - "capabilities.SEMANTIC_ROLE_CATALOG with exactly fourteen entries"
    - "model.LINT_CODES gains lesson.unknown_semantic, lesson.unknown_required_semantic, lesson.definition_before_example, lesson.example_order_no_reason"
    - "fixtures/lesson_capability_corpus.py gains build_all_roles and build_unknown_semantics"
    - "tests/capability_stress_corpus_tracer.py gains scenario_fourteen_roles, scenario_unknown_semantics, and scenario_example_order"
  key_links:
    - "The required marker rides inside _CALLOUT_MARK_RE's existing group 1 capture, which already accepts any non-bracket characters after the leading letter. That is why the trailing exclamation mark needs no regex change and why a bank that uses none of them parses byte identically. If a later executor edits the regex to make required semantics work, the additivity proof would still pass while the shipped four kinds silently changed capture behavior, so the acceptance criteria pin the regex source itself."
    - "_callout_required_of must be consulted before _callout_spec returns None, not after. An unknown kind currently returns None and falls through to the paragraph path; if required detection ran only on kinds the registry knows, an unknown required semantic would take the optional path and disappear, which is exactly the prohibition this plan carries."
    - "SEMANTIC_ROLE_CATALOG names seven mechanisms that live outside surfaces/lesson.py: the TERMS glossary, the inline check slot, the hint ladder, and the visual item type. The tracer must resolve each by calling into its real shipped path, not by asserting the catalog string is non-empty, or the catalog becomes documentation that cannot go stale visibly."
    - "lesson.definition_before_example fires per heading body, not per lesson. A per-lesson check would fire on any lesson whose first heading is an overview, which is the false positive that gets a warning ignored, and an ignored warning is worse than no warning because it trains the author to skim lint output."
---

<objective>
Fill in the six semantic teaching roles the tracer left, give the vocabulary its
required-versus-optional distinction and its unknown-semantic contract, and
prove that all fourteen roles CAP-01 names actually render.

`16A-RESEARCH.md`'s Pitfall 1 is this plan's central instruction: CAP-01's
fourteen roles are not fourteen greenfield designs. Seven already have a
shipped, working home, confirmed against real executed code:

| CAP-01 role | Shipped mechanism | Where |
|---|---|---|
| key idea | the `[!KEY]` index card | `surfaces/lesson.py` `_key_card_html`, Phase 3.1 |
| warning | the `[!WARNING]` callout | `surfaces/lesson.py` `_CALLOUT_KINDS`, Phase 3.1 |
| worked example | the `[!EXAMPLE]` callout | `surfaces/lesson.py` `_CALLOUT_KINDS`, Phase 3.1 |
| term and definition | the `## TERMS` registry and `[[term]]` refs | `model.parse_terms` plus the hover, focus, and touch gloss, Phase 3.1 |
| inline check | the `[!CHECK: <id>]` reserved slot and gate band | `surfaces/lesson.py` `_callout_spec` and `_gate_band_html`, Phases 3.1 and 6.2 |
| hint | the six-tier authored hint ladder | `runtime` and `surfaces/quiz.py`, Phases 6 and 8 |
| accessible visual interaction | the `visual` item type | `runtime._visual_interaction_contract`, Phase 06.1 |

This plan catalogs those seven and rebuilds none of them. No task here edits
`runtime.py`, `evidence.py`, or `surfaces/quiz.py`, and a task that reaches for
one of those files has misread the pitfall.

The remaining seven are the ones with no shipped home. `PREREQUISITE` landed in
the tracer. This plan registers `MISCONCEPTION`, `TIP`, `COUNTEREXAMPLE`,
`EXCERPT`, `UNCERTAINTY`, and `SUMMARY`, each as one dict entry through the
container whose own comment promises that "adding a kind is a one-line
registration here, the container and its degradation contract do not change".

It then adds the two things the vocabulary needs that the shipped four never
did: a way for an author to say a block is required for comprehension, and a
documented, visible behavior when a reader meets a semantic it does not know.
CAP-01's Degraded clause is the whole specification, quoted: "an unknown
optional semantic renders its fallback with a warning; an unknown required
semantic fails safely."

Decisions already made, cited, and never re-derived here:

- **`16A-DECISIONS.md` `## D-16A-1`**: the seven role tokens and their
  `(slug, label)` pairs, and whether `_CALLOUT_KINDS` remains the source of
  truth. Read it before Task 1. Under `option-a` the six this plan adds are
  `MISCONCEPTION`, `TIP`, `COUNTEREXAMPLE`, `EXCERPT`, `UNCERTAINTY`, `SUMMARY`.
- **`16A-DECISIONS.md` `## D-16A-3`**: the trailing exclamation mark marks a
  semantic required; the unknown-optional and unknown-required behaviors; and
  the exact refusal copy.
- **`16A-DECISIONS.md` `## D-16A-6`**: the shipped `[!EXAMPLE]` callout is
  CAP-01's worked-example bar for 16A, the worked-example-first default is a
  lint warning, and the override directive requires a reason.
- **`16A-PRECONDITION.md`, the Additivity baseline section**: the two golden
  SHA-256 values Task 3 asserts unchanged.
- **CAP-02's no-decorative-block clause and CAP-01's no-compelled-highlighting
  bake-in**, both quoted in `REQUIREMENTS.md`: no style rule may require a
  decorative block, and no flow may compel learner highlighting.
- **The phase-shape constraint on visual scope**: no color, spacing,
  typography, motion, or token decision is made anywhere in Phase 16A.

Purpose: complete the semantic vocabulary and make its failure modes visible.
Output: eleven callout kinds, a fourteen-entry role catalog, and two named
degradation paths.
</objective>

<context>
@.planning/phases/16A-semantic-capability-activity-contract/16A-DECISIONS.md
@.planning/phases/16A-semantic-capability-activity-contract/16A-PRECONDITION.md
@.planning/phases/16A-semantic-capability-activity-contract/16A-RESEARCH.md
@.planning/phases/16A-semantic-capability-activity-contract/16A-PATTERNS.md
@.planning/phases/16A-semantic-capability-activity-contract/16A-VALIDATION.md
@.planning/REQUIREMENTS.md
@.planning/PLANNING-DIRECTIVES.md
@surfaces/lesson.py
@model.py
@capabilities.py
@fixtures/lesson_capability_corpus.py
@tests/capability_stress_corpus_tracer.py
</context>

## Artifacts this phase produces (plan 16A-03 share)

New symbols introduced by this plan, and by nothing earlier:

- `surfaces/lesson.py`: six new `_CALLOUT_KINDS` entries (`MISCONCEPTION`,
  `TIP`, `COUNTEREXAMPLE`, `EXCERPT`, `UNCERTAINTY`, `SUMMARY`);
  `_callout_required_of`; `_unsupported_callout_html`;
  `UNSUPPORTED_SEMANTIC_COPY`
- `capabilities.SEMANTIC_ROLE_CATALOG` (a fourteen-entry tuple) and
  `capabilities.role_mechanism`
- Four new `model.LINT_CODES` members: `lesson.unknown_semantic`,
  `lesson.unknown_required_semantic`, `lesson.definition_before_example`,
  `lesson.example_order_no_reason`
- `model.parse_lesson`'s two new keys: `example_order` and
  `example_order_reason`
- `fixtures/lesson_capability_corpus.py`: `build_all_roles`,
  `build_unknown_semantics`, `build_definition_first`
- `tests/capability_stress_corpus_tracer.py`: `scenario_fourteen_roles`,
  `scenario_unknown_semantics`, `scenario_example_order`

No CLI command, no daemon route, and no schema file is produced by this plan.

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: the six remaining roles and the fourteen-role catalog</name>
  <files>surfaces/lesson.py, capabilities.py, fixtures/lesson_capability_corpus.py</files>
  <read_first>
- `.planning/phases/16A-semantic-capability-activity-contract/16A-DECISIONS.md`
  `## D-16A-1` in full, for the six token spellings and their `(slug, label)`
  pairs. If it recorded `option-b`, follow the consequence list recorded there
  instead of this task's step 1 and do not decide by judgment.
- `surfaces/lesson.py` lines 643 to 653, the locked-kinds comment and
  `_CALLOUT_KINDS`, as extended by plan 16A-02 to five entries.
- `surfaces/lesson.py` lines 852 to 887, `_callout_spec` and
  `_callout_kind_of`, so the dispatch is understood before it is left alone.
- `surfaces/lesson.py` lines 1121 to 1160, `_callout_html`, the one container.
- `surfaces/lesson.py` lines 926 to 1000, `_key_card_html`, and the
  `_gate_band_html` function, so the catalog's entries for the key idea and the
  inline check name their real functions rather than a guess.
- `model.py` lines 625 to 711, `parse_terms`, so the catalog's term and
  definition entry names its real function.
- `runtime.py` lines 44 to 99, `public_item`, specifically the `visual` branch,
  so the catalog's visual interaction entry names its real contract builder.
- `capabilities.py` in full as created by plan 16A-02.
- `.planning/REQUIREMENTS.md` `CAP-01` in full, for the fourteen role names in
  the order the requirement lists them.
  </read_first>
  <behavior>
- `surfaces.lesson._CALLOUT_KINDS` has exactly eleven members after this task:
  `KEY`, `EXAMPLE`, `NOTE`, `WARNING`, `PREREQUISITE`, `MISCONCEPTION`, `TIP`,
  `COUNTEREXAMPLE`, `EXCERPT`, `UNCERTAINTY`, `SUMMARY`.
- Each of the six new kinds renders through `_callout_html` into a
  `<section class="callout callout-<slug>">` carrying its locked label, with the
  same structure the four shipped kinds produce.
- `capabilities.SEMANTIC_ROLE_CATALOG` is a tuple of exactly fourteen entries,
  each a dict with the keys `role`, `mechanism`, `module`, `shipped_in`, and
  `reachable_by`, where `shipped_in` is the phase identifier that shipped the
  mechanism and is the string `"16A"` for the seven this phase adds.
- `capabilities.role_mechanism(role)` returns the entry for a catalogued role
  name and `None` for anything else.
- `build_all_roles(dest_dir)` writes one bank exercising all eleven callout
  kinds plus a `## TERMS` registry with one `[[term]]` reference, one
  `[!CHECK: <id>]` slot, and one item carrying the authored hint ladder, and
  returns its absolute path. It lints clean.
  </behavior>
  <action>
1. Add six entries to `surfaces/lesson.py`'s `_CALLOUT_KINDS` dict, one line
   each, immediately after the `PREREQUISITE` entry plan 16A-02 added. Under
   `D-16A-1` option-a the pairs are exactly:
   - `"MISCONCEPTION"` mapping to `("misconception", "Common mistake")`
   - `"TIP"` mapping to `("tip", "Expert tip")`
   - `"COUNTEREXAMPLE"` mapping to `("counterexample", "Counterexample")`
   - `"EXCERPT"` mapping to `("excerpt", "From the source")`
   - `"UNCERTAINTY"` mapping to `("uncertainty", "Not settled")`
   - `"SUMMARY"` mapping to `("summary", "In short")`

   Change nothing else in `surfaces/lesson.py` in this task. Do not touch
   `_callout_spec`, `_callout_kind_of`, `_callout_html`, `_CALLOUT_MARK_RE`, or
   the block classifier. If a new kind needs a parse branch, the design is wrong
   and the plan should be stopped rather than the branch added: CAP-01's own
   text says roles are "composed from shared primitives, not separate content
   types".

2. Add `SEMANTIC_ROLE_CATALOG` to `capabilities.py`, a module-level tuple of
   exactly fourteen dicts, in the order `REQUIREMENTS.md` CAP-01 lists the roles:
   key idea, warning, prerequisite, misconception, expert tip, worked example,
   counterexample, source excerpt, term and definition, uncertainty, summary,
   inline check, hint, accessible visual interaction.

   Each dict carries exactly these keys:
   - `role`, the role name as CAP-01 spells it, lowercase, spaces preserved.
   - `mechanism`, a short prose phrase naming the concrete mechanism, for
     example `the [!KEY] index card` or `the ## TERMS registry and [[term]]
     references`.
   - `module`, the dotted module path holding the mechanism, for example
     `surfaces.lesson` or `model` or `runtime`.
   - `shipped_in`, the phase identifier, one of `"3.1"`, `"6"`, `"6.2"`,
     `"06.1"`, `"8"`, or `"16A"`. The seven new roles carry `"16A"`.
   - `reachable_by`, the exact authored syntax or the exact function name a
     caller uses, for example `> [!KEY]` or `runtime.public_item`.

   Add `role_mechanism(role)` returning a shallow copy of the matching entry or
   `None`.

   Add one sentence to `capabilities.py`'s module docstring stating that
   `SEMANTIC_ROLE_CATALOG` is a catalog and not a source of truth under
   `D-16A-1` option-a: `_CALLOUT_KINDS` and the shipped mechanisms remain
   authoritative, and the catalog exists so CAP-01's completeness claim is
   machine checkable rather than prose. If `D-16A-1` recorded `option-b`, this
   sentence is replaced by the consequence list recorded in `16A-DECISIONS.md`.

3. Add `build_all_roles(dest_dir)` to `fixtures/lesson_capability_corpus.py`.
   It writes one file, `capability_all_roles_bank.md`, from a module-level
   literal string constant, following `build_thin_slice`'s established shape:
   fictional content, no `random`, no timestamp, deterministic bytes.

   The bank exercises every one of the fourteen roles in one document:
   - The three lesson directives from plan 16A-02.
   - A `## TERMS` registry with at least two rows, and at least one `[[term]]`
     reference in the lesson body, which covers the term and definition role.
   - One `## LESSON` section with two `### ` headings.
   - All eleven callout kinds present at least once across the two headings,
     each with a one-line or two-line body of fictional prose.
   - One `> [!CHECK: <id>]` block whose id matches a real item in the bank,
     which covers the inline check role.
   - At least two `Qn.` items. One of them carries the authored hint ladder
     fields the shipped grammar already accepts, which covers the hint role;
     read `model.SPEC` for their exact names rather than guessing them.
   - One `visual` item carrying a valid interaction contract, which covers the
     accessible visual interaction role. Read
     `fixtures/advanced_visual_bank.md` for a shipped, lint-clean example to
     copy the shape from, and change its content to fictional strings.

   No em dash characters anywhere in the file. Run
   `python itembank.py lint` against the generated bank and fix the fixture
   until it exits 0 with no errors.
  </action>
  <verify>
  <automated>python -c "import sys; sys.path.insert(0,'.'); sys.path.insert(0,'fixtures'); import capabilities, model, tempfile, subprocess; from surfaces import lesson; import lesson_capability_corpus as c; assert len(lesson._CALLOUT_KINDS)==11, sorted(lesson._CALLOUT_KINDS); assert len(capabilities.SEMANTIC_ROLE_CATALOG)==14; assert all(set(e)=={'role','mechanism','module','shipped_in','reachable_by'} for e in capabilities.SEMANTIC_ROLE_CATALOG); assert sum(1 for e in capabilities.SEMANTIC_ROLE_CATALOG if e['shipped_in']=='16A')==7; d=tempfile.mkdtemp(); p=c.build_all_roles(d); assert subprocess.call([sys.executable,'itembank.py','lint',p])==0; pg=lesson.lesson_page(p, model.load(p), model.parse_lesson(p)); [pg.index('callout-'+s) for s in ('prerequisite','misconception','tip','counterexample','excerpt','uncertainty','summary')]; print('fourteen roles ok')"</automated>
Expected: prints `fourteen roles ok` and exits 0. The degraded state this task
must also prove is that the shipped four are untouched: run
`python tests/lesson_roundtrip.py` and `python tests/gate_roundtrip.py`,
expecting exit code 0 from both, and confirm the two golden SHA-256 values in
`16A-PRECONDITION.md` still match.
  </verify>
  <acceptance_criteria>
- `len(surfaces.lesson._CALLOUT_KINDS)` is exactly `11` and its sorted key list
  is exactly
  `['COUNTEREXAMPLE', 'EXAMPLE', 'EXCERPT', 'KEY', 'MISCONCEPTION', 'NOTE', 'PREREQUISITE', 'SUMMARY', 'TIP', 'UNCERTAINTY', 'WARNING']`.
- `len(capabilities.SEMANTIC_ROLE_CATALOG)` is exactly `14`, every entry's key
  set is exactly the five named keys, and exactly seven entries carry
  `shipped_in` equal to `"16A"`.
- Every `module` value in the catalog names a module that imports successfully,
  and every `reachable_by` value that names a function is callable on that
  module. Assert this in the tracer rather than by eye.
- A render of the all-roles bank contains all seven of `callout-prerequisite`,
  `callout-misconception`, `callout-tip`, `callout-counterexample`,
  `callout-excerpt`, `callout-uncertainty`, `callout-summary`.
- `python itembank.py lint` on the generated all-roles bank exits 0 with no
  errors.
- `python tests/lesson_roundtrip.py`, `python tests/gate_roundtrip.py`, and
  `python tests/visual_roundtrip.py` each exit 0.
- The two golden SHA-256 values in `16A-PRECONDITION.md` are unchanged.
- `python itembank.py guard .` reports `0 offending files`.
- `git diff` on `surfaces/lesson.py` for this task shows changed lines only
  inside the `_CALLOUT_KINDS` dict literal.
- No em dash character appears in any line this task added to any file.
  </acceptance_criteria>
  <reversibility rating="costly">The six token spellings become an authored
  content contract the moment a corpus or a real lesson uses one. The
  representation question was settled at the `D-16A-1` checkpoint; this task
  implements the chosen answer.</reversibility>
  <done>All fourteen CAP-01 roles have a live rendering path, seven of them
  unchanged from what already shipped, and a machine-readable catalog says which
  is which.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: required semantics and the unknown-semantic contract</name>
  <files>surfaces/lesson.py, model.py</files>
  <read_first>
- `.planning/phases/16A-semantic-capability-activity-contract/16A-DECISIONS.md`
  `## D-16A-3` in full. It carries the trailing-marker rule, both degradation
  behaviors, and the exact refusal copy.
- `surfaces/lesson.py` line 641, `_CALLOUT_MARK_RE`, character by character. Its
  group 1 is `([A-Za-z][^\]]*)`, which already accepts a trailing exclamation
  mark, which is why this task changes no regex.
- `surfaces/lesson.py` lines 852 to 887, `_callout_spec` and
  `_callout_kind_of`, both in full. This task changes `_callout_spec`'s
  unknown-kind branch and adds `_callout_required_of` beside them. Note that
  `_callout_spec` currently returns `None` for an unknown kind and that
  `_callout_kind_of` returns that `None` straight through, and note the
  docstring sentence "an unknown kind never raises and never invents a
  container", which this task must keep true for the optional case.
- `surfaces/lesson.py` lines 1493 to 1535, the callout branch of the block
  classifier, in full. The `cm and _callout_kind_of(line) is not None` guard at
  1494 is the exact condition an unknown required semantic must now also pass.
- `surfaces/lesson.py` lines 1121 to 1160, `_callout_html`, so
  `_unsupported_callout_html` matches its container shape without reusing its
  label mechanism.
- `model.py` lines 2176 to 2215, `LINT_CODES`.
- `model.py` `lint`'s lesson branch, where `lesson.invalid_gate` and the three
  codes plan 16A-02 added already fire.
- `.planning/REQUIREMENTS.md` `CAP-01`'s Degraded clause, verbatim.
  </read_first>
  <behavior>
- `_callout_required_of("MISCONCEPTION!")` returns the tuple
  `("MISCONCEPTION", True)`. `_callout_required_of("MISCONCEPTION")` returns
  `("MISCONCEPTION", False)`. `_callout_required_of("WHATEVER!")` returns
  `("WHATEVER", True)` even though `WHATEVER` is not a registered kind.
- A `> [!MISCONCEPTION!]` block renders the identical container a
  `> [!MISCONCEPTION]` block renders, plus the attribute
  `data-required="1"` on the section element and nothing else. A required
  registered semantic is not a different block; it is the same block that says
  it matters.
- A `> [!WHATEVER]` block, with no trailing marker and no registration, renders
  exactly the paragraph output it rendered before Phase 16A existed, byte for
  byte.
- A `> [!WHATEVER!]` block renders one
  `<section class="callout callout-unsupported" data-required="1">` containing
  the exact locked copy `This block needs a lesson feature this reader does not
  have. Its text is below, unchanged.` followed by the block's own body text,
  escape-first through the same `_inline()` pass every other text run uses.
- Neither unknown path raises, on any input, including an empty body, a body
  that is only whitespace, and a marker that is a single letter followed by an
  exclamation mark.
- `model.lint` emits `lesson.unknown_semantic` as a warning naming the kind, one
  finding per distinct unknown optional kind, and `lesson.unknown_required_
  semantic` as an error naming the kind, one finding per distinct unknown
  required kind.
- A lesson using only registered kinds emits neither code, and its lint output
  is unchanged from before this task.
  </behavior>
  <action>
1. Add `_callout_required_of(raw)` to `surfaces/lesson.py`, beside
   `_callout_spec`. It takes the raw text `_CALLOUT_MARK_RE` group 1 captured,
   strips surrounding whitespace, and returns a `(kind, required)` tuple where
   `required` is `True` when the stripped text ends with a single `!` and the
   kind is the text with that `!` removed. It must run before any registry
   lookup, so an unknown kind still reports its required flag. Do not modify
   `_CALLOUT_MARK_RE`: the acceptance criteria pin its source text.

   The `CHECK:` prefix is handled by `_callout_spec` before this function is
   consulted, exactly as it is today. A `[!CHECK: id!]` marker is not a
   supported form and is treated as an unknown kind; state that in the
   function's docstring so a later reader does not add a branch for it.

2. Add `UNSUPPORTED_SEMANTIC_COPY` as a module-level constant in
   `surfaces/lesson.py` holding exactly this string and nothing else:
   `This block needs a lesson feature this reader does not have. Its text is
   below, unchanged.`
   Write it as one line with a single space between sentences. This is
   user-visible copy and it is locked here; do not rephrase it, do not add a
   period variant, and do not localize it in this phase.

3. Add `_unsupported_callout_html(kind, body)` to `surfaces/lesson.py`, beside
   `_callout_html`. It returns one
   `<section class="callout callout-unsupported" data-required="1">` containing:
   a `<p class="callout-label">` carrying the decorative `_CALLOUT_ICON` and the
   HTML-escaped literal label `Unsupported block`; a `<p>` carrying the escaped
   `UNSUPPORTED_SEMANTIC_COPY`; and a `<div class="callout-body">` carrying the
   body run through the same `_inline()` escape-first pass `_callout_html` uses.
   It introduces no color, no spacing value, no token, and no script.

4. Change the block classifier's callout branch in `surfaces/lesson.py` so an
   unknown required semantic reaches `_unsupported_callout_html` while an
   unknown optional semantic keeps its current fall-through. Concretely, the
   guard at line 1494 becomes: enter the callout branch when the marker matches
   and either `_callout_kind_of(line)` is not `None` or
   `_callout_required_of(<group 1>)` reports `required` is `True`. Inside the
   branch, when the spec lookup returns `None` and `required` is `True`, consume
   the `>`-prefixed run exactly as the known-kind path does and emit
   `_unsupported_callout_html`. When the spec lookup returns `None` and
   `required` is `False`, the branch is not entered at all and the existing
   paragraph path handles it untouched.

   Also add the `data-required="1"` attribute to `_callout_html`'s output when
   the caller passes a new `required` argument that is `True`, defaulting to
   `False` so every existing call site is byte identical.

   The paragraph-continuation guard at line 1601, which breaks a paragraph run
   when it meets `_callout_kind_of(nxt) is not None`, must break on an unknown
   required semantic too, or a required block immediately after a paragraph
   would be swallowed into it. Extend that condition the same way the branch
   guard was extended.

5. Add four members to `model.LINT_CODES`: `"lesson.unknown_semantic"`,
   `"lesson.unknown_required_semantic"`, `"lesson.definition_before_example"`,
   and `"lesson.example_order_no_reason"`. The last two are consumed by Task 3;
   they are added here so the sorted-set literal is edited once.

6. Add two checks to `model.lint`'s lesson branch, beside the codes plan 16A-02
   added. Both scan the effective lesson body for callout markers using the same
   marker shape `surfaces/lesson.py` uses, imported through a function-local
   import of `surfaces.lesson` so no top-level import cycle is created, which is
   the exact pattern `model.parse_terms` already uses to reuse
   `surfaces.lesson`'s cell splitter. The exact message strings are:
   - `BANK: lesson.unknown_semantic: [!%s] is not a known semantic role; it renders as a plain paragraph`
   - `BANK: lesson.unknown_required_semantic: [!%s!] is marked required and is not a known semantic role; it renders the unsupported-block fallback`

   Each emits one finding per distinct kind, in first-appearance order, so a
   lesson using the same unknown kind six times reports it once.
  </action>
  <verify>
  <automated>python -c "import sys; sys.path.insert(0,'.'); sys.path.insert(0,'fixtures'); import model, tempfile, os; from surfaces import lesson; import lesson_capability_corpus as c; assert lesson._callout_required_of('MISCONCEPTION!')==('MISCONCEPTION',True); assert lesson._callout_required_of('MISCONCEPTION')==('MISCONCEPTION',False); assert lesson._callout_required_of('WHATEVER!')==('WHATEVER',True); d=tempfile.mkdtemp(); p=c.build_unknown_semantics(d); pg=lesson.lesson_page(p, model.load(p), model.parse_lesson(p)); assert 'callout-unsupported' in pg; assert lesson.UNSUPPORTED_SEMANTIC_COPY in pg or lesson.UNSUPPORTED_SEMANTIC_COPY.replace('\"','&quot;') in pg; e,w=model.lint(model.load(p), lesson=model.parse_lesson(p)); assert any('lesson.unknown_required_semantic' in x for x in e), e; assert any('lesson.unknown_semantic' in x for x in w), w; print('unknown-semantic contract ok')"</automated>
Expected: prints `unknown-semantic contract ok` and exits 0. The degraded state
this task must also prove is that nothing is dropped: assert that the unknown
required block's own body text appears in the rendered page, and that the
unknown optional block's body text also appears, so neither degradation path
loses the author's words. Also confirm a bank using only registered kinds
renders byte identically by re-running `python tests/lesson_roundtrip.py` and
re-checking the two golden hashes.
  </verify>
  <acceptance_criteria>
- `_callout_required_of` returns the three documented tuples for
  `"MISCONCEPTION!"`, `"MISCONCEPTION"`, and `"WHATEVER!"`.
- `surfaces.lesson.UNSUPPORTED_SEMANTIC_COPY` equals exactly
  `This block needs a lesson feature this reader does not have. Its text is below, unchanged.`
- The source line defining `_CALLOUT_MARK_RE` is byte identical to its
  pre-16A text; verify with
  `grep -n '_CALLOUT_MARK_RE = re.compile' surfaces/lesson.py` and compare
  against the value recorded in the summary.
- A render of `build_unknown_semantics`'s bank contains
  `class="callout callout-unsupported"` exactly once, contains the unknown
  required block's own body text, and contains the unknown optional block's body
  text inside a `<p>` element with no callout container around it.
- `model.lint` on that bank reports `lesson.unknown_required_semantic` as an
  error and `lesson.unknown_semantic` as a warning, one finding each.
- All four new codes are members of `model.LINT_CODES`, and
  `python tests/protocol_roundtrip.py` exits 0.
- `python tests/lesson_roundtrip.py` and `python tests/gate_roundtrip.py` each
  exit 0.
- The two golden SHA-256 values in `16A-PRECONDITION.md` are unchanged.
- `grep -nE "#[0-9a-fA-F]{3,6}|font-size|margin|padding|transition" surfaces/lesson.py`
  produces no line inside the ranges this task added; record the ranges in the
  summary.
- No em dash character appears in any line this task added.
  </acceptance_criteria>
  <reversibility rating="costly">The trailing exclamation mark becomes an
  authored syntax that real lessons carry, and the unsupported-block copy is
  user-visible text a learner reads. Rated costly rather than one-way because
  the behavior was not chosen here: CAP-01's Degraded clause dictates both
  degradation paths verbatim, and `D-16A-3` records only the marker spelling,
  which is additive and which no content outside this phase's own corpus uses
  yet. Changing it after real lessons carry it would be a content
  migration.</reversibility>
  <done>An author can mark a block required, an unknown optional semantic
  degrades exactly as it did before this phase, and an unknown required semantic
  is refused out loud with the author's own text intact.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 3: the worked-example-first default, its recorded override, and the three tracer scenarios</name>
  <files>model.py, fixtures/lesson_capability_corpus.py, tests/capability_stress_corpus_tracer.py</files>
  <read_first>
- `.planning/phases/16A-semantic-capability-activity-contract/16A-DECISIONS.md`
  `## D-16A-6` in full.
- `.planning/REQUIREMENTS.md` `CAP-01`, the two sentences beginning "The default
  block order for a new conceptual lesson places a worked example or concrete
  case before the formal definition" and ending "override per lesson with a
  recorded reason", verbatim.
- `model.py` lines 469 to 566, `parse_lesson`, specifically the `headings` list
  each entry of which carries `text`, `slug`, and `body`. The per-heading check
  runs over `body`.
- `model.py` lines 530 to 535, the `[GATE:]` grab, the shape the
  `[EXAMPLE-ORDER:]` directive copies.
- `model.py` `lint`'s lesson branch as extended by Task 2.
- `tests/capability_stress_corpus_tracer.py` in full as created by plan 16A-02,
  for the scenario naming convention and the `main()` counter.
- `.planning/phases/16A-semantic-capability-activity-contract/16A-VALIDATION.md`,
  the Per-Task Verification Map.
  </read_first>
  <behavior>
- `parse_lesson` returns two new keys: `example_order`, defaulting to the string
  `"example-first"`, and `example_order_reason`, defaulting to the empty string.
  A bank carrying `[EXAMPLE-ORDER: definition-first because the formal
  definition is the course's own wording]` returns `example_order` equal to
  `"definition-first"` and `example_order_reason` equal to `the formal
  definition is the course's own wording`.
- A bank carrying `[EXAMPLE-ORDER: definition-first]` with no `because` clause
  returns `example_order` equal to `"definition-first"` and
  `example_order_reason` equal to the empty string.
- `model.lint` emits `lesson.definition_before_example` as a warning, once per
  offending heading, naming the heading text, when that heading's body contains
  at least one `> [!EXAMPLE]` marker and the character offset of its first
  `> [!KEY]` marker or its first `[[term]]` reference is lower than the offset of
  that first `> [!EXAMPLE]` marker.
- A heading containing no `> [!EXAMPLE]` marker emits no finding. A heading whose
  first example precedes its first key or term reference emits no finding.
- When `example_order` is `"definition-first"` and `example_order_reason` is
  non-empty, `lesson.definition_before_example` is suppressed for every heading
  in the lesson.
- When `example_order` is `"definition-first"` and `example_order_reason` is
  empty, `lesson.example_order_no_reason` is emitted as an error and
  `lesson.definition_before_example` is NOT suppressed. An override with no
  reason is not an override; CAP-01 requires the reason.
  </behavior>
  <action>
1. Add the `[EXAMPLE-ORDER: <value>]` grab to `parse_lesson`, immediately after
   the three directives plan 16A-02 added, following the same shape. Parse its
   text as: the first whitespace-delimited token is the order value, and
   everything after the literal word `because` (case sensitive, with surrounding
   whitespace stripped) is the reason. A value other than `"example-first"` or
   `"definition-first"` falls back to `"example-first"` and is not itself an
   error code in this phase; record that decision in the docstring so a later
   reader does not add a fourth lint code without deciding to.

   Add `example_order` and `example_order_reason` to the returned dict and to
   both `[LESSON-SRC:]` early-return dicts, exactly as plan 16A-02's six keys
   were added, so every path out of the function returns the same key set.

2. Add the two lint checks to `model.lint`'s lesson branch. The exact message
   strings are:
   - `BANK: lesson.definition_before_example: heading %r places a definition before its first worked example; CAP-01's default is example first, or record a reason with [EXAMPLE-ORDER: definition-first because ...]`
   - `BANK: lesson.example_order_no_reason: [EXAMPLE-ORDER: definition-first] carries no because clause; CAP-01 requires a recorded reason for the override`

   The first is a warning, the second an error. Implement the offset comparison
   over the heading's raw `body` string using `str.find` on the three literal
   markers, not a regex scan, so the rule is readable and its false-positive
   surface is small. A `-1` result from `find` means absent and is handled
   before any comparison.

3. Add three fixture builders to `fixtures/lesson_capability_corpus.py`,
   following `build_thin_slice`'s shape: literal string constants, fictional
   content, deterministic bytes, no `random`.
   - `build_unknown_semantics(dest_dir)`, writing a bank containing exactly one
     `> [!WHATEVER]` block and exactly one `> [!ALSOUNKNOWN!]` block, each with
     two lines of fictional body text, plus one registered callout so the file
     is a realistic lesson rather than a pathology.
   - `build_definition_first(dest_dir)`, writing a bank with two `### `
     headings: the first places a `> [!KEY]` block before its `> [!EXAMPLE]`
     block and carries no override directive, and the second places its
     `> [!EXAMPLE]` first.
   - Extend `build_definition_first` with a keyword argument
     `override` taking the values `None`, `"with_reason"`, and `"no_reason"`,
     writing the corresponding `[EXAMPLE-ORDER:]` directive or none. Default
     `None`.

   Each generated bank must lint clean apart from the specific findings it
   exists to produce. Run `python itembank.py lint` on each and record the
   findings in the summary.

4. Add three scenarios to `tests/capability_stress_corpus_tracer.py`, following
   the file's existing convention and counted by its existing `main()`:
   - `scenario_fourteen_roles()`: asserts `SEMANTIC_ROLE_CATALOG` has fourteen
     entries; for every entry, imports the named `module` and, when
     `reachable_by` names a dotted function, asserts it is callable on that
     module; builds the all-roles bank; renders it in both continuous and guided
     mode; and asserts every one of the eleven callout slugs appears in both
     renders. A catalog entry that names a module or function that does not
     resolve fails the scenario by name.
   - `scenario_unknown_semantics()`: builds the unknown-semantics bank; renders
     it; asserts the unsupported container appears exactly once; asserts both
     unknown blocks' body text survives into the page; and asserts `model.lint`
     reports exactly one `lesson.unknown_semantic` warning and exactly one
     `lesson.unknown_required_semantic` error.
   - `scenario_example_order()`: builds the definition-first bank three times
     with `override=None`, `override="with_reason"`, and
     `override="no_reason"`, and asserts the warning fires, is suppressed, and
     fires alongside `lesson.example_order_no_reason` respectively.

5. Update `16A-VALIDATION.md`'s Per-Task Verification Map with three rows for
   plan 16A-03's tasks, naming the three scenario functions and a Status of
   `passing`.
  </action>
  <verify>
  <automated>python tests/capability_stress_corpus_tracer.py</automated>
Expected final line: `TRACER: 5 passed, 0 skipped, 0 failed`, exit code 0. The
degraded state this task must also prove is that the override is not a bypass:
the `override="no_reason"` case must produce both codes, showing that an
override with no recorded reason neither suppresses the warning nor passes
silently.
  </verify>
  <acceptance_criteria>
- `model.parse_lesson` returns `example_order` and `example_order_reason` on
  every path, with defaults `"example-first"` and `""`.
- `python tests/capability_stress_corpus_tracer.py` exits 0 with the final line
  `TRACER: 5 passed, 0 skipped, 0 failed`.
- `model.lint` on the `override=None` definition-first bank reports exactly one
  `lesson.definition_before_example` warning naming the first heading.
- `model.lint` on the `override="with_reason"` bank reports zero
  `lesson.definition_before_example` findings and zero
  `lesson.example_order_no_reason` findings.
- `model.lint` on the `override="no_reason"` bank reports one
  `lesson.example_order_no_reason` error and one
  `lesson.definition_before_example` warning.
- `for t in tests/*.py; do python "$t" || exit 1; done` exits 0.
- `python itembank.py guard .` reports `0 offending files`.
- The two golden SHA-256 values in `16A-PRECONDITION.md` are unchanged.
- `16A-VALIDATION.md` has three new filled rows naming plan `16A-03`.
- No em dash character appears in any line this task added.
  </acceptance_criteria>
  <reversibility rating="costly">The `[EXAMPLE-ORDER:]` directive becomes an
  authored syntax and the two lint messages are read by authoring agents and by
  CI greps. Changing the directive after lessons carry it is a content
  migration; changing a message string breaks a grep.</reversibility>
  <done>The worked-example-first default is enforced by a check rather than by
  hope, its override requires the reason CAP-01 asks for, and the tracer proves
  all three states.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| authored callout marker to renderer | An author writes an arbitrary kind string inside brackets; the renderer must handle any of them without raising and without dropping the author's text. |
| unknown semantic to learner | A block the reader cannot honor is where a lesson silently loses meaning, and where a learner would never know it happened. |
| catalog claim to real mechanism | `SEMANTIC_ROLE_CATALOG` asserts fourteen roles render; a catalog that is only prose can claim a mechanism that no longer exists. |
| new lint messages to CI greps | Authoring agents and CI both read the exact message strings, so a rephrasing breaks consumers outside this file. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-16A-03-01 | Repudiation | an unknown required semantic silently dropped, so the rendered lesson misrepresents what the author wrote | high | mitigate | Task 2 routes the unknown required case to `_unsupported_callout_html`, which carries the author's own body text through the same escape-first `_inline()` pass, and the acceptance criteria assert that body text appears in the rendered page. `model.lint` emits an error naming the kind. |
| T-16A-03-02 | Tampering | a regex change to `_CALLOUT_MARK_RE` that silently alters how the four shipped kinds capture | high | mitigate | The required marker rides inside the existing group 1 capture and no regex edit is needed; the acceptance criteria pin the regex source line and require it recorded in the summary for comparison. |
| T-16A-03-03 | Spoofing | a role catalog claiming a mechanism that no longer resolves | medium | mitigate | `scenario_fourteen_roles` imports every catalogued `module` and asserts every function-shaped `reachable_by` is callable, so a stale entry fails the tracer rather than reading plausibly. |
| T-16A-03-04 | Tampering | a format change that is not additive | high | mitigate | Every task's acceptance criteria re-assert the two golden SHA-256 values from `16A-PRECONDITION.md` and require `tests/lesson_roundtrip.py` green. |
| T-16A-03-05 | Elevation of Privilege | a required semantic read as an authorization rather than as authored orientation | high | mitigate | `data-required="1"` is an attribute on a presentation container and reaches no runtime call; the plan's prohibition states that semantic emphasis stays author-provided orientation and compels nothing, and plan 16A-09's adversarial suite asserts no lesson attribute changes what `runtime.public_item` returns. |
| T-16A-03-06 | Denial of Service | a pathological callout marker raising during render | medium | mitigate | `_callout_required_of` operates on an already-captured string with `str.strip` and `str.endswith` only, and the behavior block names an empty body, a whitespace-only body, and a single-letter marker as cases that must not raise. |
| T-16A-03-07 | Information Disclosure | real course content entering the repository through three new fixture builders | high | mitigate | Every builder writes from a module-level literal fictional constant with no `random` and no external read; `python itembank.py guard .` reporting `0 offending files` is an acceptance criterion on all three tasks. |
| T-16A-03-08 | Tampering | supply chain: a third-party dependency introduced by this plan | high | mitigate | None is added; every change is standard library only. Per `PLANNING-DIRECTIVES.md` section 4a the absence of dependencies is explicitly not the mitigation: the mitigation is that any dependency ever added here is vendored at a pinned version with a recorded checksum and a named license review, following the KaTeX precedent in `09-03-PLAN.md`. |
</threat_model>

<out_of_scope>
Refused by this plan, by name, so no adjacent temptation is decided by executor
judgment:

- Any edit to `runtime.py`, `evidence.py`, or `surfaces/quiz.py`. The hint
  ladder, the visual item type, and the scorer are shipped and are catalogued
  here, not touched. `16A-RESEARCH.md`'s Pitfall 1 names a task that touches
  those files to "add hint support to lessons" as the warning sign this plan
  refuses.
- A richer worked-example structure. `D-16A-6` settles that the shipped
  `[!EXAMPLE]` callout is 16A's bar, and annotated per-step structure is a
  Registered-tier enhancement for a later capability-profile version.
- A structured `effective_date` or `jurisdiction` field on `[!WARNING]`.
  `D-16A-7` defers it; the medical evolving-case fixture in plan 16A-10 uses
  free prose with a stated date.
- The capability profile for each new role. Plan 16A-04 registers profiles for
  the roles this plan adds; this plan adds only the catalog entry.
- `## MEDIA`, `## ACTIVITIES`, and the localization fixture set. Plans 16A-05,
  16A-06, and 16A-08 own them.
- Every visual decision. No color, spacing, typography, motion, or token
  constant is introduced anywhere in this plan.
- A fourth lint code for an unrecognized `[EXAMPLE-ORDER:]` value. Task 3 step 1
  states the fallback and records the decision not to add one.
</out_of_scope>

<flagged_assumptions>
- **CAP-01's probe row, returned by the edge-coverage probe as `unclassified`,
  is classified by this plan as a completeness question** and resolved
  explicitly: does every one of the fourteen named roles have a live rendering
  path, and what happens to a role named in the requirement but absent from the
  registry. The acceptance criterion is carried in `must_haves.truths` as the
  fourteen-entry catalog whose every entry resolves to a real module and a real
  callable, and the "absent from the registry" half is exactly the
  unknown-semantic contract Task 2 builds. The classification and its reason are
  recorded in `16A-DECISIONS.md`'s Probe classification note by plan 16A-01.
- **The `data-required="1"` attribute is a presentation marker only in this
  phase.** Nothing reads it. It exists so a guided-mode stager, a later
  accessibility review, and Phase 17A's visual system have a hook that already
  carries the author's intent, rather than each inventing one. That it is
  currently unread is recorded here rather than discovered later as dead code.
</flagged_assumptions>

<summary_obligations>
`16A-03-SUMMARY.md` records: the six `(slug, label)` pairs as registered; the
`_CALLOUT_MARK_RE` source line verbatim, so the pin in the acceptance criteria
is checkable by a later reader; the line ranges added to `surfaces/lesson.py`
and `model.py`, so the no-visual-token grep is checkable; the fourteen catalog
entries with their `module` and `reachable_by` values as written; the lint
findings each of the three new fixture banks produced; the tracer's final
summary line verbatim; the two golden SHA-256 values as re-verified; which truth
was verified by which command with the command's actual stdout; and any
deviation from this plan with its reason.
</summary_obligations>

<output>
Create
`.planning/phases/16A-semantic-capability-activity-contract/16A-03-SUMMARY.md`
when done.
</output>
