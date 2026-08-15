---
phase: 16A-semantic-capability-activity-contract
plan: 02
type: execute
wave: 2
depends_on: ["16A-01"]
files_modified:
  - model.py
  - capabilities.py
  - surfaces/lesson.py
  - fixtures/lesson_capability_corpus.py
  - tests/capability_stress_corpus_tracer.py
autonomous: true
requirements: [CAP-01, CAP-02, A11Y-02, PORT-01]
estimate:
  tokens: 82000
  raw_tokens: 82000
  tasks: 3
  confidence: low
must_haves:
  truths:
    - "One authored synthetic lesson block travels the whole phase in one committed slice: a [!PREREQUISITE] callout authored in UTF-8 Markdown parses through the one shipped parser, resolves a capability profile in the new registry, and renders in both continuous and guided mode, proven by one end to end tracer scenario rather than by three per-layer unit tests."
    - "parse_lesson returns three new keys, semantic_profile, lang, and dir, on every call including calls on banks that carry none of the three directives, where the values are the integer 1, the string en, and the string auto (D-16A-4)."
    - "A lesson with no [LESSON-LANG:] directive parses to lang equal to en and dir equal to auto; an empty directive value parses to those same defaults and is the lint error lesson.lang_empty rather than an emitted empty attribute (A11Y-02 empty probe)."
    - "lesson_page gains a mode keyword defaulting to continuous, so every shipped caller renders the same document it rendered before this plan, and guided mode is reached only by an explicit argument (D-16A-9)."
    - "capabilities.py exists as a pure module: it contains no open( call, imports neither evidence nor runtime, and every public function returns a value computed from its arguments and module constants alone."
    - "The additivity claim is proven, not promised: fixtures/lesson_golden_phase3_parse.json and fixtures/lesson_golden_phase3_content.txt still carry the two SHA-256 values recorded in 16A-PRECONDITION.md after every change in this plan, and python tests/lesson_roundtrip.py exits 0 (PORT-01 empty probe)."
    - "The tracer file tests/capability_stress_corpus_tracer.py exists and ends its run with the literal line TRACER: N passed, M skipped, 0 failed, so every later plan grows one tracer rather than starting a second one."
    - "The stress corpus generator contains no real course, exam, syllabus, learner, or bank content: every string in fixtures/lesson_capability_corpus.py is fictional and deterministic, and python itembank.py guard . reports zero offending files."
  prohibitions:
    - statement: "A capability profile must not decide keyed disclosure or settle a score; renderer availability describes whether a renderer exists, never whether a learner may see an answer, and the runtime remains the only authority for disclosure."
      status: kept
      verification: flagged-unverified
    - statement: "Real course, learner, exam, or bank content must not enter the repository through the stress corpus; the corpus is fictional and its only relationship to real material is its shape."
      status: kept
      verification: flagged-unverified
    - statement: "Guided mode must not acquire a color, spacing, typography, motion, or token decision; a second rendering mode that renegotiates visual meaning would take Phase 17A's decisions before Phase 17A has compared three directions."
      status: kept
      verification: flagged-unverified
  artifacts:
    - "model.SEMANTIC_PROFILE_VERSION, model.LESSON_DIRECTIONS, and parse_lesson's three new keys semantic_profile, lang, dir"
    - "capabilities.py with CAPABILITY_PROFILE_KEYS, RENDERER_AVAILABILITY, CapabilityError, profile, profiles, register, static_path, and exactly one seeded profile"
    - "surfaces/lesson.py with one new _CALLOUT_KINDS entry, lesson_page's mode keyword, guided_stages, and _stage_html"
    - "fixtures/lesson_capability_corpus.py with build_thin_slice"
    - "tests/capability_stress_corpus_tracer.py with scenario_thin_slice and scenario_additivity_golden_parse"
  key_links:
    - "The tracer's verify is one end to end assertion over one authored block, not three per-layer assertions stitched together. A per-layer suite would pass with a parser that emits a field no renderer reads, which is the architectural dead end the tracer exists to catch on this phase's first commit rather than on its ninth."
    - "lesson_page's mode keyword defaults to continuous. If it defaulted to guided or had no default, every shipped caller in surfaces/daemon.py, surfaces/cli.py, and six test files would change behavior in a plan that has no defect to fix in any of them, and the additivity proof in Task 3 would go red for a reason unrelated to grammar."
    - "capabilities.py is seeded with exactly one profile in this plan. Seeding the full registry here would make the tracer a horizontal layer wearing a tracer's name: the point of the slice is that one profile travels all the way, not that a registry is complete before anything reads it."
    - "The <html> tag in LESSON_TEMPLATE gains lang and dir attributes. The shipped golden content fixture is body-only (it begins at <section id=...>), and no test asserts on the <html> tag, confirmed by grep across tests/. That is why this change can be additive at the parse level and still emit the attributes A11Y-02 requires."
---

<objective>
Build the phase's tracer: the thinnest end to end path that touches every layer
Phase 16A will modify, wired together, verified by a real runnable check, and
committed before any horizontal expansion begins.

The path is one authored `[!PREREQUISITE]` callout in one synthetic lesson. It
starts as UTF-8 Markdown, passes through the one shipped parser (`model.py`),
resolves one capability profile in the new registry (`capabilities.py`), and
renders in both continuous and guided mode through the one shipped renderer
(`surfaces/lesson.py`), and one tracer scenario asserts the whole trip rather
than each hop.

Every layer this phase will grow is present in that slice and none of them is
complete: one of seven new roles, one of the capability registry's eventual
profiles, one of the localization fields' fixture cases. That is the point.
`16A-RESEARCH.md`'s Pitfall 3 names the architectural risk this catches: a
guided mode that turns out to need a second parsed document, or a capability
profile that turns out to have no renderer that reads it, is a dead end worth
discovering after one commit rather than after nine.

This plan is production quality, not a prototype. The `[!PREREQUISITE]`
registration, the three lesson directives, `capabilities.py`'s module shape,
and `lesson_page`'s `mode` keyword are the shipped versions. What is thin is
coverage, not quality: the six remaining roles, the full profile registry, and
the full localization fixture set are later plans filling in behind a proven
path, and each of them is a functionality gap rather than an architectural one.

Decisions already made, cited, and never re-derived here:

- **`16A-DECISIONS.md` `## D-16A-1`**: the seven role tokens and whether the
  semantic-role registry is primary. Read that file before Task 2. Under
  `option-a` the token for this plan's one role is `PREREQUISITE` and its pair
  is `("prerequisite", "Before this")`.
- **`16A-DECISIONS.md` `## D-16A-2`**: where the capability registry lives.
  Under `option-a` this plan creates a new root-level `capabilities.py`.
- **`16A-DECISIONS.md` `## D-16A-4`**: the `[SEMANTIC-PROFILE: <n>]` directive,
  default `1`, read with the same `grab()` shape `[GATE:]` uses.
- **`16A-DECISIONS.md` `## D-16A-5`**:
  `RENDERER_AVAILABILITY = ("available", "degraded", "unavailable")`.
- **`16A-DECISIONS.md` `## D-16A-9`**: guided mode's data contract, in full,
  including the sentence that reading position and resume are Phase 16B's.
- **`16A-PRECONDITION.md`, the Additivity baseline section**: the two golden
  SHA-256 values Task 3 asserts unchanged.
- **PLANNING-DIRECTIVES section 4 number 4**: format changes are additive,
  proven by a byte-identical fixture, not by promise.
- **PLANNING-DIRECTIVES section 4a**, quoted: section 4.2 "forbids a **second**
  parser, scorer, or evidence store. It does not freeze the one parser's
  grammar. Additive growth is section 4.4's subject and is permitted."

Purpose: prove the architecture end to end on this phase's first commit.
Output: one authored block that travels every layer, and one tracer that says so.
</objective>

<context>
@.planning/phases/16A-semantic-capability-activity-contract/16A-DECISIONS.md
@.planning/phases/16A-semantic-capability-activity-contract/16A-PRECONDITION.md
@.planning/phases/16A-semantic-capability-activity-contract/16A-RESEARCH.md
@.planning/phases/16A-semantic-capability-activity-contract/16A-PATTERNS.md
@.planning/phases/16A-semantic-capability-activity-contract/16A-VALIDATION.md
@.planning/PLANNING-DIRECTIVES.md
@.planning/PLAN-TEMPLATE.md
@.planning/REQUIREMENTS.md
@model.py
@surfaces/lesson.py
@fixtures/lesson_bank.md
@tests/lesson_roundtrip.py
</context>

## Artifacts this phase produces (plan 16A-02 share)

New symbols introduced by this plan, and by nothing earlier:

- `model.SEMANTIC_PROFILE_VERSION` (integer constant, value `1`)
- `model.LESSON_DIRECTIONS` (tuple constant `("ltr", "rtl", "auto")`)
- Three new keys on `model.parse_lesson`'s return dict: `semantic_profile`,
  `lang`, `dir`
- Two new `model.LINT_CODES` members: `lesson.invalid_semantic_profile`,
  `lesson.lang_empty`; and one more, `lesson.invalid_direction`
- `capabilities.py` and on it: `CAPABILITY_PROFILE_KEYS`,
  `RENDERER_AVAILABILITY`, `CapabilityError`, `profile`, `profiles`, `register`,
  `static_path`, `_CAPABILITY_PROFILES`
- `surfaces/lesson.py`: one new `_CALLOUT_KINDS` entry; `lesson_page`'s `mode`
  keyword argument; `guided_stages`; `_stage_html`; the `__LANG__` and
  `__DIR__` template placeholders
- `fixtures/lesson_capability_corpus.py` and on it: `build_thin_slice`
- `tests/capability_stress_corpus_tracer.py` and on it: `fail`,
  `shipped_suite_check`, `scenario_thin_slice`,
  `scenario_additivity_golden_parse`, `main`

No CLI command and no daemon route is produced by this plan. No schema file is
produced by this plan.

<tasks>

<task type="tracer" tdd="true">
  <name>Task 1: the parse layer of the slice, plus the corpus file it parses</name>
  <files>model.py, fixtures/lesson_capability_corpus.py</files>
  <read_first>
- `.planning/phases/16A-semantic-capability-activity-contract/16A-DECISIONS.md`
  in full, in particular `## D-16A-4` (the semantic profile directive) and
  `## D-16A-1` (the seven role tokens). Do not proceed if either heading is
  absent; that means plan 16A-01's checkpoints were not answered.
- `model.py` lines 469 to 566, `parse_lesson` in full. Note in particular the
  `[GATE:]` grab at lines 530 to 535 and its comment, which is the exact shape
  the three new directives copy, and the returned dict at lines 560 to 566,
  which is where the three new keys are added.
- `model.py` lines 569 to 602, `_TERM_REF_RE` through `_preamble_section`, the
  one boundary rule every preamble registry reads through. This task adds no
  new preamble section, so it adds no second scanner; read this so the
  constraint is understood before plan 16A-05 does add one.
- `model.py` lines 2176 to 2215, `LINT_CODES`, the sorted set literal the three
  new codes are added to.
- `model.py` line 2052, `GATE_VALUES`, the closed-tuple constant shape
  `LESSON_DIRECTIONS` copies.
- `model.py` lines 2864 to the end of `lint`'s lesson section, to find where the
  existing `lesson.invalid_gate` check fires; the three new lesson-level checks
  fire beside it, in the same branch, so lesson findings stay together in the
  emitted order the shipped tests already assert.
- `fixtures/lesson_bank.md` in full. It is the shape template for the corpus
  file: a `# ` title, a synthetic-content disclaimer paragraph, a `## LESSON`
  section with `### ` headings, then `Qn.` items carrying `[LESSON-REF:]`,
  `[OBJECTIVE:]`, lettered options, `CORRECT:`, `WHY BEST:`,
  `KEY DISCRIMINATOR:`, `SECOND-BEST:`, `DISTRACTOR ANALYSIS:`, `TRAP:`, and
  `CONFIDENCE:`.
- `fixtures/grandchild_spawner.py` in full, the closest shipped Python fixture
  generator, for the module shape `lesson_capability_corpus.py` follows.
  </read_first>
  <behavior>
- `parse_lesson` on a bank carrying none of the three new directives returns a
  dict whose `semantic_profile` is the integer `1`, whose `lang` is the string
  `"en"`, and whose `dir` is the string `"auto"`, and whose every other key and
  value is byte identical to what it returned before this plan.
- `parse_lesson` on a bank carrying `[SEMANTIC-PROFILE: 2]` returns
  `semantic_profile` equal to the integer `2`.
- `parse_lesson` on a bank carrying `[SEMANTIC-PROFILE: two]` or
  `[SEMANTIC-PROFILE: 0]` or `[SEMANTIC-PROFILE: -1]` returns
  `semantic_profile` equal to `1` and does not raise. The value is refused at
  lint time, never at parse time, exactly as `[GATE:]` is.
- `parse_lesson` on a bank carrying `[LESSON-LANG: ar]` and `[LESSON-DIR: rtl]`
  returns `lang` equal to `"ar"` and `dir` equal to `"rtl"`.
- `parse_lesson` on a bank carrying `[LESSON-LANG: ]` with an empty value
  returns `lang` equal to `"en"` and does not raise.
- `parse_lesson` on a bank carrying `[LESSON-DIR: sideways]` returns `dir` equal
  to `"auto"` and does not raise.
- `model.lint` on a lesson whose `semantic_profile` directive was unparseable
  emits `lesson.invalid_semantic_profile` as an error; on an empty
  `[LESSON-LANG: ]` emits `lesson.lang_empty` as an error; on a direction
  outside `LESSON_DIRECTIONS` emits `lesson.invalid_direction` as an error.
- `model.lint` on a bank carrying none of the three directives emits none of the
  three codes and its findings list is unchanged from before this plan.
- `build_thin_slice(dest_dir)` writes exactly one file,
  `<dest_dir>/capability_thin_slice_bank.md`, returns its absolute path, and
  writing it twice into the same directory produces byte identical content.
  </behavior>
  <action>
1. Add three module-level names to `model.py`, beside `GATE_VALUES` at line
   2052 so the closed vocabularies stay together:
   - `SEMANTIC_PROFILE_VERSION`, the integer `1`, with a one-line comment citing
     `D-16A-4` and PORT-01's "additive, versioned semantic profile".
   - `LESSON_DIRECTIONS`, the tuple `("ltr", "rtl", "auto")`, in
     `GATE_VALUES`'s exact shape.
   - Nothing else. Do not add a language tag vocabulary: BCP 47 tags are an open
     set and validating them would need a table this project has no reason to
     carry. `lang` is validated as non-empty only, which is what
     `lesson.lang_empty` says.

2. Extend `parse_lesson` in `model.py`. Add three `grab()` reads immediately
   after the existing `[GATE:]` grab at line 535, each following that line's
   exact pattern of a multiline anchored directive regex with a default applied
   by an `or` expression:
   - `[SEMANTIC-PROFILE: <value>]`, defaulting to `SEMANTIC_PROFILE_VERSION`.
     Coerce the grabbed text with a guarded integer conversion: a value that is
     not a decimal string of a positive integer falls back to
     `SEMANTIC_PROFILE_VERSION` and sets a new local flag the returned dict
     carries as `semantic_profile_raw` holding the offending text, so `lint` can
     name what the author wrote. When the directive is absent,
     `semantic_profile_raw` is the empty string.
   - `[LESSON-LANG: <tag>]`, defaulting to `"en"`. An empty or whitespace-only
     value falls back to `"en"` and sets `lang_raw` to the empty-after-strip
     text so `lint` can distinguish "absent" from "present and empty": absent
     leaves `lang_raw` unset as the empty string and present-and-empty sets it
     to the sentinel string `"<empty>"`.
   - `[LESSON-DIR: <value>]`, defaulting to `"auto"`. A value outside
     `LESSON_DIRECTIONS` falls back to `"auto"` and sets `dir_raw` to the
     offending text.

   Add exactly six keys to the returned dict at lines 560 to 566:
   `semantic_profile`, `semantic_profile_raw`, `lang`, `lang_raw`, `dir`,
   `dir_raw`. Add them after the existing `gate` key and before `body`, so the
   dict's existing key order is not disturbed for any reader that iterates it.

   Also add all six keys to the two early-return dicts inside `parse_lesson`
   that handle an unreadable `[LESSON-SRC:]` (lines 520 to 522 and 526 to 527),
   with the same defaults, so every path out of the function returns the same
   key set. This is the same discipline the existing `error` and `detail` keys
   already follow.

   The parse must not raise on any input. `parse_lesson`'s own docstring already
   states that contract for `[LESSON-SRC:]`; extend the docstring with one
   sentence naming the three new directives, their defaults, and the fact that
   their values are validated at lint time and never here.

3. Add three members to `model.LINT_CODES`'s sorted set literal:
   `"lesson.invalid_semantic_profile"`, `"lesson.lang_empty"`,
   `"lesson.invalid_direction"`. The literal is wrapped in
   `tuple(sorted({...}))`, so ordering is structural and no manual placement is
   needed.

4. Add three checks to `model.lint`'s lesson branch, beside the existing
   `lesson.invalid_gate` check, each emitting a `BANK`-tagged error in the same
   shape that check uses. The exact message strings, which authoring agents and
   CI greps both read, are:
   - `BANK: lesson.invalid_semantic_profile: [SEMANTIC-PROFILE: %s] is not a positive integer; the reader falls back to profile 1`
   - `BANK: lesson.lang_empty: [LESSON-LANG:] carries no language tag; the reader falls back to en`
   - `BANK: lesson.invalid_direction: [LESSON-DIR: %s] is not one of ltr, rtl, auto; the reader falls back to auto`

   Each fires only when the corresponding `*_raw` key is non-empty, so a bank
   carrying none of the three directives emits none of the three findings and
   the shipped lint output is unchanged.

5. Create `fixtures/lesson_capability_corpus.py` with a module docstring
   stating, in prose: that every string in the file is fictional; that no real
   course, exam, syllabus, learner note, or bank content is present or derived
   from; that the module is the Phase 16A stress-corpus generator; and that it
   is standard library only and directly importable. Follow
   `fixtures/grandchild_spawner.py`'s module shape: module-level functions, no
   class, no `__main__` block needed.

   Add `build_thin_slice(dest_dir)`. It writes exactly one file,
   `capability_thin_slice_bank.md`, under `dest_dir`, from a module-level
   literal string constant named `THIN_SLICE_BANK`. Use no `random` and no
   timestamp: determinism here is a literal, which is stronger than a seed. It
   returns the absolute path of the written file.

   `THIN_SLICE_BANK`'s content, structurally, following
   `fixtures/lesson_bank.md`:
   - A `# ` title line reading `# Reading a tide table (synthetic)`.
   - A disclaimer paragraph stating the content is fully invented and derived
     from no real course, exam, or textbook.
   - The three new directives on their own lines, in this order:
     `[SEMANTIC-PROFILE: 1]`, `[LESSON-LANG: en]`, `[LESSON-DIR: ltr]`.
   - A `## LESSON` heading.
   - One `### ` heading reading `### Reading A Tide Table`.
   - Under it, in this order: one `> [!PREREQUISITE]` callout whose body is one
     `>` line reading
     `> You can read a two column table and add whole numbers.`; one paragraph
     of fictional prose about tide tables; one `> [!EXAMPLE]` callout whose body
     names a fictional station called Kestrel Point with two times; and one more
     paragraph.
   - One `Q1.` multiple-choice item with four lettered options, a
     `[LESSON-REF: Reading A Tide Table]` tag, an `[OBJECTIVE: nav:tides]` tag,
     and every field `fixtures/lesson_bank.md`'s `Q1` carries: `CORRECT:`,
     `WHY BEST:`, `KEY DISCRIMINATOR:`, `SECOND-BEST:`,
     `DISTRACTOR ANALYSIS:` with one bullet per option each containing the
     phrase `would be correct if`, `TRAP:`, and `CONFIDENCE: high`.

   No em dash characters anywhere in the file, including inside the fixture
   content string. Run `python itembank.py lint <written path>` against the
   generated file and fix the fixture until it exits 0 with no errors. A fixture
   that does not lint clean is not a fixture this phase can build on.
  </action>
  <verify>
  <automated>python -c "import model, tempfile, os, sys; sys.path.insert(0,'.'); sys.path.insert(0,'fixtures'); import lesson_capability_corpus as c; d=tempfile.mkdtemp(); p=c.build_thin_slice(d); L=model.parse_lesson(p); assert L['semantic_profile']==1 and L['lang']=='en' and L['dir']=='ltr', L; B=model.parse_lesson('fixtures/lesson_bank.md'); assert B['semantic_profile']==1 and B['lang']=='en' and B['dir']=='auto', B; e,w=model.lint(model.load('fixtures/lesson_bank.md'), lesson=B); assert not [x for x in e if 'lesson.invalid_semantic_profile' in x or 'lesson.lang_empty' in x or 'lesson.invalid_direction' in x], e; print('parse layer ok')"</automated>
Expected: prints `parse layer ok` and exits 0. The degraded state this task must
also prove is that a malformed directive never raises: run
`python -c "import model; print(model.SEMANTIC_PROFILE_VERSION, model.LESSON_DIRECTIONS)"`
expecting `1 ('ltr', 'rtl', 'auto')`, then build a temporary copy of the thin
slice bank with `[SEMANTIC-PROFILE: two]` and `[LESSON-DIR: sideways]`
substituted and confirm `parse_lesson` returns `1` and `auto` with no exception
while `model.lint` reports both codes.
  </verify>
  <acceptance_criteria>
- `python -c "import model; print(model.SEMANTIC_PROFILE_VERSION, model.LESSON_DIRECTIONS)"`
  prints exactly `1 ('ltr', 'rtl', 'auto')`.
- `model.parse_lesson('fixtures/lesson_bank.md')` returns a dict containing all
  six of `semantic_profile`, `semantic_profile_raw`, `lang`, `lang_raw`, `dir`,
  `dir_raw`, with values `1`, `""`, `"en"`, `""`, `"auto"`, `""`.
- All three of `lesson.invalid_semantic_profile`, `lesson.lang_empty`, and
  `lesson.invalid_direction` are members of `model.LINT_CODES`.
- `python tests/protocol_roundtrip.py` exits 0, confirming the three new codes
  satisfy the shipped lint-namespace coupling assertions.
- `python tests/lesson_roundtrip.py` exits 0.
- `python itembank.py lint` on the generated thin-slice bank exits 0 with no
  errors reported.
- `build_thin_slice` called twice into two different temporary directories
  produces two files with the same SHA-256.
- `python itembank.py guard .` reports `0 offending files`.
- `fixtures/lesson_capability_corpus.py` contains no em dash character and no
  `import random`.
  </acceptance_criteria>
  <precondition>`16A-DECISIONS.md` exists and carries the headings `## D-16A-1`, `## D-16A-2`, `## D-16A-4`, and `## D-16A-9`, meaning plan 16A-01's two blocking checkpoints were answered.</precondition>
  <reversibility rating="costly">The three lesson directives become an authored
  content contract the moment a corpus file uses one, and later plans and later
  phases author against them. Renaming a directive after the freeze is a content
  migration across every file that carries it, though the parse is additive so
  no existing bank breaks.</reversibility>
  <done>An authored lesson carrying all three new directives parses to the
  documented values, a bank carrying none of them parses exactly as before, and
  the corpus generator produces a bank that lints clean.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: the registry and render layers of the slice</name>
  <files>capabilities.py, surfaces/lesson.py</files>
  <read_first>
- `.planning/phases/16A-semantic-capability-activity-contract/16A-DECISIONS.md`,
  `## D-16A-1` (the token and its `(slug, label)` pair), `## D-16A-2` (which
  module this registry lives in), `## D-16A-5` (the renderer-availability
  tuple), and `## D-16A-9` (guided mode's data contract), all in full.
- `surfaces/lesson.py` lines 639 to 665: `_TOKEN_RE`, `_FENCE_RE`,
  `_CALLOUT_MARK_RE`, the locked-kinds comment, `_CALLOUT_KINDS`, and
  `_CALLOUT_ICON`. The one-line registration goes in the dict at 648 to 653.
- `surfaces/lesson.py` lines 852 to 887, `_callout_spec` and
  `_callout_kind_of`. Read both; this task changes neither under `D-16A-1`
  option-a.
- `surfaces/lesson.py` lines 1121 to 1160, `_callout_html`, the one container
  every generic kind renders through. This task changes nothing in it.
- `surfaces/lesson.py` lines 1480 to 1535, the callout branch of the block
  classifier, so the new kind's dispatch path is understood without changing it.
- `surfaces/lesson.py` lines 332 to 346, `LESSON_TEMPLATE`'s opening, and lines
  1974 to 1993, the chain of `.replace()` calls that fills it. Both the
  `<html>` tag and the replace chain change in this task.
- `surfaces/lesson.py` lines 1734 to 1810, `lesson_page`'s signature and
  docstring, where the `mode` keyword is added.
- `model.py` line 2052, `GATE_VALUES`, the closed-tuple shape
  `RENDERER_AVAILABILITY` copies.
- `16A-PATTERNS.md`, the `capabilities.py` Pattern Assignment section in full,
  including the "Do not fold into" note.
  </read_first>
  <behavior>
- `capabilities.profile("callout_prerequisite")` returns a dict whose keys are
  exactly `CAPABILITY_PROFILE_KEYS`, with `renderer_availability` equal to
  `"available"`.
- `capabilities.profile("no_such_capability")` returns `None`. It does not raise
  and does not return a partial dict.
- `capabilities.register(entry, registry=None)` returns a NEW dict carrying the
  existing entries plus the new one and mutates nothing, so a caller that
  registers a capability cannot leak it into another caller's view. Called with
  a name already present it raises `CapabilityError`. Called with a
  `renderer_availability` outside `RENDERER_AVAILABILITY` it raises
  `CapabilityError`. Called with a key set that is not exactly
  `CAPABILITY_PROFILE_KEYS` it raises `CapabilityError`.
- `capabilities.profile(name, registry=None)` and
  `capabilities.profiles(registry=None)` read the module's built-in registry
  when `registry` is `None` and the caller's dict otherwise.
- `capabilities.static_path(name)` returns the profile's `offline_fallback`
  string for a registered name and the empty string for an unregistered one.
- `lesson_page(bank, qs, lesson)` with no `mode` argument returns the identical
  string it returned before this plan for every bank that carries no
  `[!PREREQUISITE]` callout and no `[LESSON-LANG:]` or `[LESSON-DIR:]`
  directive, except for the two new attributes on the `<html>` tag.
- `lesson_page(bank, qs, lesson, mode="guided")` returns a document whose body
  contains at least one `<section class="stage" data-stage="0"` and in which
  exactly one stage carries `data-stage-open="1"`.
- `lesson_page(..., mode="guided")` and `lesson_page(..., mode="continuous")`
  called on the same bank produce documents whose rendered callout containers
  are identical strings: guided mode groups blocks, it does not re-render them.
- `guided_stages(heading_body)` returns a list of dicts each carrying exactly
  the keys `index`, `slug`, `blocks`, `requires`, and returns a one-element list
  for a heading body with no callout in it.
- `lesson_page` called with `mode="sideways"` raises `ValueError` naming the two
  accepted values. An unknown mode is a programming error at a call site, not
  authored content, so it fails loudly rather than falling back.
  </behavior>
  <action>
1. Create `capabilities.py` at the repository root, under `D-16A-2` option-a. If
   `D-16A-2` recorded option-b or option-c, follow the consequence list recorded
   in `16A-DECISIONS.md` instead of this step, and do not decide by judgment.

   Module docstring states, in prose: that this is the capability support
   profile registry for CAP-02; that it is pure, meaning no file read, no file
   write, no session state, and no import of `evidence` or `runtime`; that a
   capability profile describes whether a renderer exists and what a learner
   sees when it does not, and never whether a learner may see an answer, which
   is `runtime.public_item`'s and `runtime.glossable`'s decision and no other
   module's; and that adding a capability is a one-entry registration in the
   module-level dict, following `model.GATE_VALUES`'s and
   `surfaces/lesson.py`'s `_CALLOUT_KINDS`'s established pattern.

   The module carries:
   - `CAPABILITY_PROFILE_KEYS`, the tuple
     `("name", "accessible_behavior", "offline_fallback",
     "renderer_availability", "version", "validation", "known_limits")`.
   - `RENDERER_AVAILABILITY`, the tuple
     `("available", "degraded", "unavailable")`, per `D-16A-5`.
   - `class CapabilityError(Exception)` with a one-line docstring.
   - `_CAPABILITY_PROFILES`, a module-level dict seeded with exactly one entry,
     `"callout_prerequisite"`, whose values are: `accessible_behavior` reading
     `Renders as a labelled section with a visible text label; reachable in
     document order by keyboard and by screen reader with no interaction
     required.`; `offline_fallback` reading `The block renders as a labelled
     paragraph with no script and no network.`; `renderer_availability` equal to
     `"available"`; `version` equal to the integer `1`; `validation` reading
     `model.lint reports an unknown callout kind as lesson.unknown_semantic.`;
     and `known_limits` reading `The label is not translated; the block carries
     the lesson's document language.`
   - `profile(name, registry=None)`, returning a shallow copy of the entry or
     `None`. Return a copy so a caller cannot mutate the registry by editing a
     returned dict. `registry` defaults to `_CAPABILITY_PROFILES`.
   - `profiles(registry=None)`, returning a tuple of shallow copies in the
     dict's insertion order, which is the module's literal source order.
   - `register(entry, registry=None)`, validating the key set against
     `CAPABILITY_PROFILE_KEYS`, the `renderer_availability` value against
     `RENDERER_AVAILABILITY`, and the name against the existing keys, raising
     `CapabilityError` with a message naming the offending value on each
     failure, then returning a NEW dict carrying the existing entries plus the
     new one. It mutates nothing, so a test or a fixture that registers a
     synthetic capability cannot leak it into another caller's view.
   - `static_path(name, registry=None)`, returning the profile's
     `offline_fallback` or the empty string.

   Do not add an output-mode vocabulary, a media vocabulary, a schema file, or
   a second seeded profile in this task. Plan 16A-04 owns all four, and adding
   them here would turn the tracer into a horizontal layer.

2. Register the one new callout kind in `surfaces/lesson.py`'s `_CALLOUT_KINDS`
   dict at lines 648 to 653: the key `"PREREQUISITE"` mapping to
   `("prerequisite", "Before this")` under `D-16A-1` option-a, or to whatever
   pair `16A-DECISIONS.md` recorded. Add it as one line. Do not change
   `_callout_spec`, `_callout_kind_of`, `_callout_html`, `_CALLOUT_MARK_RE`, or
   the block classifier: the container and its degradation contract do not
   change, which is what the comment above the dict already promises.

   Add exactly one line of CSS class support only if `LESSON_CSS` already
   carries a per-slug rule for the four shipped kinds. Check first. If it uses
   one shared `.callout` rule with no per-slug branch, add nothing, and state
   that in the summary. Do not introduce a color, a spacing value, or any token:
   Phase 17A owns those, and this plan may not name one.

3. Emit the document language and direction. Change `LESSON_TEMPLATE`'s opening
   from `<html lang="en">` to `<html lang="__LANG__" dir="__DIR__">`, and add
   two `.replace()` calls to the chain at lines 1974 to 1993, substituting the
   HTML-escaped `lang` and `dir` values from the `lesson` dict the caller
   passed, defaulting to `"en"` and `"auto"` when `lesson` is `None` or carries
   neither key. `lang` and `dir` are escaped with `html.escape` exactly as every
   other interpolated value in that chain is.

   This is the only byte change to the shipped rendered page in this task. The
   shipped golden content fixture is body-only, beginning at
   `<section id=...>`, and no test asserts on the `<html>` tag, so
   `tests/lesson_roundtrip.py` stays green. Confirm that rather than assume it,
   in Task 3.

4. Add guided mode. Give `lesson_page` a keyword argument `mode` defaulting to
   the string `"continuous"`, placed last in the signature so no positional
   caller changes. Add one sentence to its docstring naming the two values,
   citing `D-16A-9`, and stating that reading position and resume are Phase
   16B's and are deliberately absent here.

   Add `guided_stages(heading_body)` as a module-level function: it splits one
   `###` heading's body into stages at each callout boundary, where a stage is
   the run of blocks up to and including the next callout, and returns a list of
   dicts carrying `index` (integer, zero based), `slug` (the heading slug plus
   a `-stage-<index>` suffix, built through `model.lesson_slug` and never by
   raw string manipulation), `blocks` (the raw text of the stage), and
   `requires` (a list of the required-semantic kind strings found in the stage,
   which is empty in this plan because required semantics are plan 16A-03's).
   A body with no callout returns a one-element list. A body that is empty
   returns an empty list.

   Add `_stage_html(stage, rendered_blocks)`: it wraps one stage's already
   rendered block HTML in
   `<section class="stage" data-stage="N">` plus, for index `0` only,
   ` data-stage-open="1"`, and closes it. It adds no other attribute, no class
   beyond `stage`, and no inline style.

   In `lesson_page`, when `mode` is `"guided"`, render each heading's body
   through the existing `render_markdown` exactly as continuous mode does, then
   group the resulting block HTML into stages and wrap each with `_stage_html`.
   The rendered callout containers must be identical strings in both modes:
   guided mode groups, it does not re-render. When `mode` is neither
   `"continuous"` nor `"guided"`, raise `ValueError` with the message
   `lesson_page: mode must be "continuous" or "guided" (got %r)`.

   Introduce no JavaScript, no CSS token, no color, no spacing value, no
   transition, and no `<details>` element in this task. The stage is a semantic
   grouping proven by an attribute, and Phase 17A decides what it looks like.
  </action>
  <verify>
  <automated>python -c "import sys; sys.path.insert(0,'.'); import capabilities, model, re; from surfaces import lesson; assert capabilities.profile('callout_prerequisite')['renderer_availability']=='available'; assert capabilities.profile('nope') is None; assert 'PREREQUISITE' in lesson._CALLOUT_KINDS and len(lesson._CALLOUT_KINDS)==5; qs=model.load('fixtures/lesson_bank.md'); L=model.parse_lesson('fixtures/lesson_bank.md'); a=lesson.lesson_page('fixtures/lesson_bank.md',qs,L); b=lesson.lesson_page('fixtures/lesson_bank.md',qs,L,mode='guided'); assert 'dir=\"auto\"' in a and 'lang=\"en\"' in a; assert 'data-stage=\"0\"' in b and b.count('data-stage-open=\"1\"')==1; assert 'data-stage' not in a; print('registry and render layers ok')"</automated>
Expected: prints `registry and render layers ok` and exits 0. The degraded state
this task must also prove is the unavailable-renderer direction of the contract:
run `python -c "import capabilities; print(repr(capabilities.static_path('callout_prerequisite')), repr(capabilities.static_path('nope')))"` and
confirm the first is the non-empty offline-fallback sentence and the second is
the empty string, so an unregistered capability degrades to nothing rather than
to a crash. Also confirm `lesson_page(..., mode="sideways")` raises `ValueError`
rather than silently rendering continuous.
  </verify>
  <acceptance_criteria>
- `capabilities.py` exists at the repository root and
  `python -c "import capabilities; print(capabilities.CAPABILITY_PROFILE_KEYS, capabilities.RENDERER_AVAILABILITY, len(capabilities.profiles()))"`
  prints exactly
  `('name', 'accessible_behavior', 'offline_fallback', 'renderer_availability', 'version', 'validation', 'known_limits') ('available', 'degraded', 'unavailable') 1`.
- `grep -c "open(" capabilities.py` reports `0`, and
  `grep -cE "^import (evidence|runtime)|^from (evidence|runtime)" capabilities.py`
  reports `0`.
- `len(surfaces.lesson._CALLOUT_KINDS)` is `5` and `"PREREQUISITE"` is a key.
- `surfaces.lesson.lesson_page` accepts a `mode` keyword and raises `ValueError`
  on any value other than `"continuous"` or `"guided"`.
- A continuous render of `fixtures/lesson_bank.md` contains `lang="en"` and
  `dir="auto"` on its `<html>` tag and contains no `data-stage` attribute.
- A guided render of the same bank contains at least one
  `<section class="stage" data-stage="0"` and exactly one occurrence of
  `data-stage-open="1"`.
- Every `<section class="callout` substring present in the continuous render is
  also present in the guided render, character for character.
- `grep -nE "#[0-9a-fA-F]{3,6}|var\\(--|font-size|margin|padding|transition" surfaces/lesson.py`
  produces no line whose line number falls inside the range this task added.
  Record the added line ranges in the summary so this is checkable.
- `python tests/lesson_roundtrip.py` exits 0.
- `python tests/presentation_roundtrip.py` exits 0.
- No em dash character appears in `capabilities.py` or in any line this task
  added to `surfaces/lesson.py`.
  </acceptance_criteria>
  <reversibility rating="costly">`capabilities.py`'s name and its seven-key
  profile shape become a published contract that plans 04 through 10 import and
  that Phases 16B, 16C, and 17A read. Rated costly rather than one-way because
  the one-way door was already walked deliberately at plan 16A-01 Task 3's
  blocking `D-16A-2` checkpoint; this task implements the chosen answer and does
  not reopen it. What remains is the ordinary cost of renaming a symbol before
  any authored content depends on it.</reversibility>
  <done>One authored `[!PREREQUISITE]` block renders in both modes through one
  parsed document, its capability profile is inspectable, and no visual decision
  was made.</done>
</task>

<task type="auto">
  <name>Task 3: the tracer that asserts the whole trip, and the additivity proof</name>
  <files>tests/capability_stress_corpus_tracer.py</files>
  <read_first>
- `tests/evidence_roundtrip.py` lines 1 to 40, the shipped test-file convention:
  the shebang, the standard-library-only import block, the `ROOT`/`sys.path`
  insertion, and the local `fail(msg)` helper. Every `tests/*.py` in this
  repository follows it and there is no test framework anywhere.
- `16A-PATTERNS.md`, the `tests/capability_stress_corpus_tracer.py` Pattern
  Assignment section in full, including the note that the
  `TRACER: N passed, M skipped, 0 failed` summary-line convention is a
  plan-text analog from 14A and 14B, not a shipped one.
- `.planning/phases/16A-semantic-capability-activity-contract/16A-PRECONDITION.md`,
  the Additivity baseline section, for the two SHA-256 values this task asserts.
- `.planning/phases/16A-semantic-capability-activity-contract/16A-VALIDATION.md`,
  the Per-Task Verification Map, so the scenario names this task creates match
  the names recorded there.
  </read_first>
  <action>
1. Create `tests/capability_stress_corpus_tracer.py` following
   `tests/evidence_roundtrip.py`'s opening convention exactly: shebang, module
   docstring stating it is standard library only and runnable as
   `python tests/capability_stress_corpus_tracer.py`, the standard-library
   import block, `ROOT` computed from `__file__`, `sys.path.insert(0, ROOT)`,
   and a local `fail(msg)` helper that prints `FAIL: ` plus the message and
   exits 1.

   Add a `shipped_suite_check()` helper that runs, as subprocesses, before any
   16A scenario: `tests/lesson_roundtrip.py`, `tests/protocol_roundtrip.py`, and
   `tests/presentation_roundtrip.py`. If any exits non-zero, every scenario is
   SKIPPED rather than failed, and the summary line reports the skips. A phase
   tracer that reports passes while the shipped renderer is broken hides which
   layer moved, which is worse than a red tracer.

2. Add `scenario_thin_slice()`. It is one end to end assertion over one authored
   block, not three per-layer assertions. In one function, in this order:
   - Build the corpus into a temporary directory with
     `fixtures.lesson_capability_corpus.build_thin_slice`.
   - Parse it with `model.load` and `model.parse_lesson`, and assert
     `semantic_profile` is `1`, `lang` is `"en"`, `dir` is `"ltr"`.
   - Assert `capabilities.profile("callout_prerequisite")` is not `None` and its
     `renderer_availability` is `"available"`.
   - Render it with `surfaces.lesson.lesson_page` in continuous mode and assert
     the output contains `lang="en"`, `dir="ltr"`, the literal
     `class="callout callout-prerequisite"`, and the literal label text
     `Before this`.
   - Render it again in guided mode and assert the output contains
     `data-stage="0"`, exactly one `data-stage-open="1"`, and the identical
     `<section class="callout callout-prerequisite"` container substring the
     continuous render produced.
   - Assert `python itembank.py lint <corpus path>` exits 0 as a subprocess.

   The scenario fails, by name, if any one of those assertions fails, and the
   failure message names which hop broke. That naming is the whole value of a
   tracer: a per-layer suite would tell you a field exists and a renderer runs,
   without telling you they met.

3. Add `scenario_additivity_golden_parse()`. It reads the two SHA-256 values
   from `16A-PRECONDITION.md`'s Additivity baseline section by parsing that
   file, rather than carrying them as literals in the test, so the baseline has
   one home. It then recomputes the SHA-256 of
   `fixtures/lesson_golden_phase3_parse.json` and
   `fixtures/lesson_golden_phase3_content.txt` and asserts both match. It also
   runs `tests/lesson_roundtrip.py` as a subprocess and asserts exit code 0.

   If `16A-PRECONDITION.md` is missing or its Additivity baseline section
   carries no hash lines, the scenario FAILS rather than skips. A missing
   baseline is a missing proof, and PLANNING-DIRECTIVES section 4 number 4
   requires the proof, quoted: format changes are additive, "proven by a
   byte-identical fixture, not promised".

4. Add `main()`: run `shipped_suite_check()`, then each `scenario_*` function in
   source order, counting passes and skips, and print as the final line exactly
   `TRACER: %d passed, %d skipped, 0 failed`. Exit 0 only when the failed count
   is zero. Add the standard `if __name__ == "__main__": main()` guard.

5. Update
   `.planning/phases/16A-semantic-capability-activity-contract/16A-VALIDATION.md`'s
   Per-Task Verification Map: fill the rows for plan 16A-02's three tasks with
   the requirement ids, behaviors, test types, automated commands, assertion
   function names (`scenario_thin_slice`,
   `scenario_additivity_golden_parse`), and a Status of `passing`. Tick the Wave
   0 Requirements checkbox for `tests/capability_stress_corpus_tracer.py` and
   for `fixtures/lesson_capability_corpus.py`, and leave the other three
   unticked. Do not touch the Estimated runtime placeholder; plan 16A-10
   replaces it with a measured figure.
  </action>
  <verify>
  <automated>python tests/capability_stress_corpus_tracer.py</automated>
Expected final line: `TRACER: 2 passed, 0 skipped, 0 failed`, exit code 0. The
degraded state this task must also prove is the shipped-suite guard: temporarily
rename `tests/lesson_roundtrip.py`, re-run the tracer, and confirm it reports
skips rather than passes and does not claim a green phase. Restore the file
immediately and re-run to confirm `2 passed, 0 skipped, 0 failed`.
  </verify>
  <acceptance_criteria>
- `python tests/capability_stress_corpus_tracer.py` exits 0 and its final line is
  exactly `TRACER: 2 passed, 0 skipped, 0 failed`.
- The tracer file defines a local `fail(msg)` and imports no test framework;
  `grep -cE "^import (pytest|unittest)|^from (pytest|unittest)" tests/capability_stress_corpus_tracer.py`
  reports `0`.
- `scenario_additivity_golden_parse` reads its expected hashes from
  `16A-PRECONDITION.md` and carries no SHA-256 literal;
  `grep -cE "[0-9a-f]{64}" tests/capability_stress_corpus_tracer.py` reports `0`.
- `for t in tests/*.py; do python "$t" || exit 1; done` exits 0.
- `python itembank.py guard .` reports `0 offending files`.
- `16A-VALIDATION.md`'s Per-Task Verification Map has three filled rows naming
  plan `16A-02` and its three tasks, and two of the five Wave 0 checkboxes are
  ticked.
- No em dash character appears in the tracer file or in the
  `16A-VALIDATION.md` rows this task added.
  </acceptance_criteria>
  <reversibility rating="reversible">A test file and a validation-map row.
  Both can be rewritten at any point without migrating content or renaming a
  published surface.</reversibility>
  <done>One tracer run proves an authored block travelled parser, registry, and
  both renderers, and proves the shipped format did not move while it did.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| authored Markdown to parser | Authored lesson text is untrusted input to `model.parse_lesson`; a malformed directive must degrade rather than raise, because a reader that crashes on a typo is a reader that loses a lesson. |
| capability profile to disclosure | A profile's `renderer_availability` field sits next to disclosure decisions and could be misread as permission; it describes whether a renderer exists and nothing else. |
| fixture generator to repository | Synthetic lesson material enters version control and could drift toward real course content. |
| pre-phase tree to additivity claim | The golden hashes recorded at wave 1 are the only evidence this plan's format change stayed additive. |
| guided mode to Phase 17A | A second rendering mode is where visual decisions leak in ahead of the phase that owns them. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-16A-02-01 | Elevation of Privilege | a capability profile read as a disclosure permission | high | mitigate | `capabilities.py`'s docstring states that a profile never decides what a learner may see; the module imports neither `runtime` nor `evidence`, asserted by a grep in the acceptance criteria, so it structurally cannot reach a disclosure decision. Plan 16A-09's adversarial suite attacks this directly. |
| T-16A-02-02 | Denial of Service | a malformed lesson directive raising instead of degrading | high | mitigate | All three directives fall back to a documented default and are validated at lint time only; the Task 1 verify step builds a bank with two malformed directives and confirms `parse_lesson` returns the defaults without an exception. |
| T-16A-02-03 | Tampering | a format change that is not additive | high | mitigate | `scenario_additivity_golden_parse` asserts both shipped golden fixtures still carry their wave-1 SHA-256 and re-runs `tests/lesson_roundtrip.py`; a missing baseline fails the scenario rather than skipping it. |
| T-16A-02-04 | Information Disclosure | real course, exam, or learner content entering the repository through the corpus | high | mitigate | Every string in `fixtures/lesson_capability_corpus.py` is a literal fictional constant with no `random` and no external read; `python itembank.py guard .` reporting `0 offending files` is an acceptance criterion on all three tasks. |
| T-16A-02-05 | Tampering | a guided-mode render that disagrees with continuous mode about what a block means | high | mitigate | Both modes render blocks through the same `render_markdown` call and guided mode only groups the results; the tracer asserts the callout container substring is character-for-character identical in both renders. |
| T-16A-02-06 | Spoofing | a green tracer masking a regression in the shipped renderer | medium | mitigate | `shipped_suite_check()` runs three shipped suites as subprocesses before any scenario, and a red suite skips every scenario rather than reporting passes; the Task 3 verify step exercises that path by renaming a shipped test. |
| T-16A-02-07 | Tampering | supply chain: a third-party dependency introduced by this plan | high | mitigate | None is added; every new file is standard library only. Per `PLANNING-DIRECTIVES.md` section 4a the absence of dependencies is explicitly not the mitigation: the mitigation is that any dependency ever added here is vendored at a pinned version with a recorded checksum and a named license review, following the KaTeX precedent in `09-03-PLAN.md`. |
| T-16A-02-08 | Repudiation | a tracer carrying its own expected hashes, so a changed fixture could be papered over by editing the test | medium | mitigate | The scenario reads its expected values from `16A-PRECONDITION.md`, and the acceptance criteria assert the test file contains no 64-character hex literal. |
</threat_model>

<out_of_scope>
Refused by this plan, by name, so no adjacent temptation is decided by executor
judgment:

- The six remaining callout kinds. Only `PREREQUISITE` is registered here; plan
  16A-03 registers `MISCONCEPTION`, `TIP`, `COUNTEREXAMPLE`, `EXCERPT`,
  `UNCERTAINTY`, and `SUMMARY`.
- The required-semantic trailing marker and the unknown-semantic contract
  (`D-16A-3`). `guided_stages`' `requires` list is present and empty in this
  plan; plan 16A-03 fills it.
- The full capability registry, `schemas/capability_profile.schema.json`, the
  output-mode vocabulary, and the media vocabulary. Plan 16A-04 owns all four.
- `## MEDIA` and `## ACTIVITIES`. Plans 16A-05 and 16A-06 own them, and no
  second preamble-section scanner is written by this plan or by either of them.
- The localization fixture set. Plan 16A-08 owns RTL, CJK, combining marks, long
  strings, and localized numbers and units; this plan lands only the two fields
  they will be authored against.
- Every visual decision. No color, spacing, typography, motion, token constant,
  or `<details>` element is introduced. Phase 17A owns them and this plan may
  not name one.
- Reading position, resume, and stage navigation. Phase 16B owns them, per
  `D-16A-9`.
- Any edit to `runtime.py` or `evidence.py`. This plan reads neither and changes
  neither.
</out_of_scope>

<flagged_assumptions>
- **A11Y-02's empty probe row is resolved by this plan** as the explicit
  criterion carried in `must_haves.truths`: a lesson with no `[LESSON-LANG:]`
  parses to `en` and `auto`, and an empty directive value parses to the same
  defaults and is `lesson.lang_empty` rather than an emitted empty attribute.
- **PORT-01's empty probe row is resolved by this plan** as the explicit
  criterion carried in `must_haves.truths`: a canonical lesson using none of the
  16A semantics parses and renders unchanged, proven by the two golden SHA-256
  values holding through every change in this plan.
- **The `LESSON_CSS` per-slug question is left to inspection, not decided
  here.** Task 2 step 2 tells the executor to check whether `LESSON_CSS` carries
  a per-slug rule for the four shipped kinds and to add nothing if it does not.
  This is a factual check with one right answer readable from the file, not a
  design decision, and the summary records which branch was taken.
</flagged_assumptions>

<summary_obligations>
`16A-02-SUMMARY.md` records: which `D-16A-1` and `D-16A-2` options were in force
and whether any consequence list applied; the exact `(slug, label)` pair
registered; the line ranges added to `surfaces/lesson.py`, so the no-visual-token
grep in the acceptance criteria is checkable; which branch Task 2 step 2 took on
`LESSON_CSS`; the two golden SHA-256 values as re-verified, and whether either
moved; the tracer's final summary line verbatim; the result of the shipped-suite
guard exercise, including that the renamed test was restored; which truth was
verified by which command with the command's actual stdout; and any deviation
from this plan with its reason.
</summary_obligations>

<output>
Create
`.planning/phases/16A-semantic-capability-activity-contract/16A-02-SUMMARY.md`
when done.
</output>
