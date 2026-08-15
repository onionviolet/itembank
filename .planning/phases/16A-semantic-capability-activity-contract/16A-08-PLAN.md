---
phase: 16A-semantic-capability-activity-contract
plan: 08
type: execute
wave: 8
depends_on: ["16A-07"]
files_modified:
  - model.py
  - surfaces/lesson.py
  - fixtures/lesson_capability_corpus.py
  - tests/capability_stress_corpus_tracer.py
autonomous: true
requirements: [A11Y-02, PORT-01]
estimate:
  tokens: 74000
  raw_tokens: 74000
  tasks: 2
  confidence: low
must_haves:
  truths:
    - "The localization fixture set covers all seven cases A11Y-02 names, RTL, mixed code and math direction, CJK, combining marks, long strings, localized numbers and units, and culturally dependent examples, as synthetic strings inside the stress corpus, and each case is a named constant the tracer asserts on individually rather than one blob that could pass by accident."
    - "No Unicode normalization, reordering, stripping, or width folding is applied to authored lesson text anywhere in Phase 16A: every fixture string round-trips byte for byte from the Markdown source through parse and render, asserted by SHA-256 of the source substring against the rendered substring after HTML unescaping, and a precomposed and a decomposed spelling of the same visible text stay two distinct strings (A11Y-02 encoding probe)."
    - "Equality and length in this phase are byte equality of UTF-8; nothing measures a length in code points or grapheme clusters, because nothing in this phase needs to, and the tracer asserts the long-string case survives untruncated rather than asserting anything about its length."
    - "A bidi override character embedded in authored text is preserved byte for byte and never stripped, because stripping it would corrupt legitimate right-to-left content, and the display-spoofing risk it carries is recorded as an accepted characteristic of any right-to-left-capable renderer rather than papered over."
    - "Explicit is opt-in for per-element direction: a lesson that writes [LESSON-DIR: auto] gets dir=auto on every text-run element so each run resolves from its own first strong character, and a lesson that writes no direction directive renders byte identically to before this plan, which is what keeps the shipped golden fixtures green."
    - "A11Y-02's Degraded clause holds in the only form this tool can offer it: itembank applies no locale transformation, so no locale can be mishandled into corrupt text, and the one unhandled input, a direction value outside ltr, rtl, auto, falls back to auto with the named lint error lesson.invalid_direction rather than rendering something wrong."
  prohibitions:
    - statement: "Authored text must not be normalized, reordered, case folded, width folded, or stripped of bidi or combining characters; a renderer that corrects the learner's script is corrupting the source, and the correct posture is the one every text editor and browser takes."
      status: kept
      verification: flagged-unverified
    - statement: "A derived view must not become the only understandable copy for localized content either; the corpus's non-Latin text must be readable in the plain Markdown source with every rendered page deleted."
      status: kept
      verification: flagged-unverified
    - statement: "Real learner, course, or exam material must not enter the repository through the localization corpus; every non-Latin string is a synthetic fixture whose only job is to exercise an encoding path."
      status: kept
      verification: flagged-unverified
  artifacts:
    - "model.parse_lesson gains dir_declared"
    - "surfaces/lesson.py emits dir=auto on text-run elements only when the direction is explicitly declared as auto"
    - "fixtures/lesson_capability_corpus.py gains build_localization_lesson and the seven named case constants"
    - "tests/capability_stress_corpus_tracer.py gains scenario_localization"
  key_links:
    - "The per-element dir=auto attribute is emitted only when the author explicitly writes [LESSON-DIR: auto], never when auto is the parsed default. Emitting it on the default path would add an attribute to every paragraph of every existing bank, which would change the shipped golden content fixture's bytes and turn tests/lesson_roundtrip.py red for a reason unrelated to localization. Explicit opt-in is what makes this addition additive."
    - "The byte-identity assertion compares SHA-256 of the source substring against SHA-256 of the rendered substring after HTML unescaping, not against the raw rendered bytes. Escaping is a legitimate transformation of markup characters; normalization is not. Comparing raw bytes would fail on a legitimate ampersand escape and would teach the executor to weaken the assertion, which is how the real check gets lost."
    - "The precomposed and decomposed pair must stay two distinct strings. A single normalization call anywhere in the parse or render path would silently collapse them into one, and no other assertion in this phase would notice, because both spellings look identical on screen."
    - "The seven cases are seven named module-level constants, not one long fixture string. A single blob could pass its assertion while one case had been quietly dropped from it; seven constants each asserted by name cannot."
---

<objective>
Give the canonical lesson its language and direction metadata a real fixture set,
and prove this tool transforms no authored text.

A11Y-02, quoted: "Canonical records carry language and direction, and
localization fixtures cover RTL, mixed code and math direction, CJK, combining
marks, long strings, localized numbers and units, and culturally dependent
examples. Owner: lesson-authoring plus MAINT. Durable object: localization
fixtures plus language metadata. Authority: capability validation. Degraded: an
unhandled locale renders a clearly-marked fallback rather than corrupt text."

Plan 16A-02 landed the two metadata fields. This plan lands the fixtures they
exist for, and the discipline those fixtures enforce.

The discipline is a negative one, and `16A-RESEARCH.md`'s Don't Hand-Roll table
states it: bidi reordering, CJK line breaking, and combining-mark glyph
composition are browser and font-stack responsibilities once the correct
attributes and untouched UTF-8 bytes are emitted. A Python-side reimplementation
would duplicate a solved, standards-governed problem and risk getting it wrong.
So this phase adds no ICU binding, no bidi algorithm, no Unicode segmentation
library, and no normalization pass. What it adds is a fixture set that fails the
day someone adds one.

The precomposed and decomposed pair is the sharpest of those checks. Two
spellings of the same visible text must stay two distinct strings through parse
and render. A single `unicodedata.normalize` call anywhere in the path would
collapse them, and nothing else in this phase would notice, because they look
identical on screen.

The bidi override character is the security case `16A-RESEARCH.md`'s Security
Domain table names. A right-to-left override embedded in authored text can
visually reorder what follows it, which is a display-spoofing risk. The correct
handling is to preserve it byte for byte, because stripping it would corrupt
legitimate right-to-left content, and to record the risk as an accepted
characteristic of any right-to-left-capable renderer rather than as an itembank
defect. That is the posture every text editor and browser takes, and this plan
records it rather than discovering it later.

The Degraded clause needs an honest reading, and this plan gives it one.
"An unhandled locale renders a clearly-marked fallback rather than corrupt text"
presumes a tool that processes locales. This one does not: it emits `lang` and
`dir` attributes and passes raw UTF-8 through, so there is no transformation in
which a locale could be mishandled. The clause is satisfied in the two places
where an input can actually be wrong: a direction value outside the closed tuple
falls back to `auto` with the named lint error `lesson.invalid_direction`, and
an empty language tag falls back to `en` with `lesson.lang_empty`. Both were
landed by plan 16A-02 and both are asserted here.

Decisions already made, cited, and never re-derived here:

- **`16A-DECISIONS.md` `## D-16A-4`** and plan 16A-02's Task 1:
  `[LESSON-LANG:]` and `[LESSON-DIR:]` ride the same directive pattern
  `D-16A-4` established for `[SEMANTIC-PROFILE:]`, with the defaults `en` and
  `auto`, validation at lint time and never at parse time, and the two lint
  codes `lesson.lang_empty` and `lesson.invalid_direction`.
- **`16A-DECISIONS.md` `## D-16A-9`**: guided mode renders the same parsed
  document, so a localized lesson's text must survive identically in both
  modes and the tracer asserts exactly that.
- **`model.LESSON_DIRECTIONS`**: `("ltr", "rtl", "auto")`.
- **`16A-RESEARCH.md`'s Don't Hand-Roll table**, the RTL and CJK row, quoted
  above.
- **`16A-RESEARCH.md`'s Security Domain table**, the bidi-override row, whose
  recommendation this plan implements verbatim.
- **PLANNING-DIRECTIVES section 4 number 4**: format changes are additive,
  proven by a byte-identical fixture.
- **The phase-shape constraint on visual scope**: no color, spacing,
  typography, motion, or token decision anywhere in Phase 16A. Font selection
  for CJK and Arabic coverage is Phase 17A's and is named out of scope below.

Purpose: prove the tool passes text through rather than fixing it.
Output: seven named localization cases, one direction opt-in, and one
no-normalization proof.
</objective>

<context>
@.planning/phases/16A-semantic-capability-activity-contract/16A-DECISIONS.md
@.planning/phases/16A-semantic-capability-activity-contract/16A-PRECONDITION.md
@.planning/phases/16A-semantic-capability-activity-contract/16A-RESEARCH.md
@.planning/phases/16A-semantic-capability-activity-contract/16A-PATTERNS.md
@.planning/phases/16A-semantic-capability-activity-contract/16A-VALIDATION.md
@.planning/REQUIREMENTS.md
@.planning/UI-SPEC.md
@model.py
@surfaces/lesson.py
@fixtures/lesson_capability_corpus.py
@tests/capability_stress_corpus_tracer.py
</context>

## Artifacts this phase produces (plan 16A-08 share)

New symbols introduced by this plan, and by nothing earlier:

- `model.parse_lesson`'s new key `dir_declared`
- `fixtures/lesson_capability_corpus.py`: `build_localization_lesson` and seven
  module-level case constants, `LOC_RTL`, `LOC_MIXED_DIRECTION`, `LOC_CJK`,
  `LOC_COMBINING`, `LOC_LONG_STRING`, `LOC_NUMBERS_UNITS`, `LOC_CULTURAL`, plus
  `LOC_BIDI_OVERRIDE` and `LOC_PRECOMPOSED`, `LOC_DECOMPOSED`
- `tests/capability_stress_corpus_tracer.py`: `scenario_localization`

No new module, no CLI command, no daemon route, and no schema file is produced
by this plan. No third-party dependency is added by this plan, and that is the
point of it.

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: the explicit direction opt-in and the seven-case localization corpus</name>
  <files>model.py, surfaces/lesson.py, fixtures/lesson_capability_corpus.py</files>
  <read_first>
- `.planning/REQUIREMENTS.md` `A11Y-02` in full, for the seven case names in the
  order the requirement lists them, and its Degraded clause.
- `.planning/REQUIREMENTS.md` `A11Y-01`, the requirement immediately above, so
  the keyboard, screen reader, zoom and reflow, high contrast, and reduced
  motion review is recognized as a different requirement this plan does not own.
- `model.py`'s `parse_lesson` as extended by plans 16A-02 and 16A-03, in
  particular the `dir`, `dir_raw`, `lang`, and `lang_raw` keys and both
  `[LESSON-SRC:]` early-return dicts.
- `surfaces/lesson.py` lines 332 to 346 and 1974 to 1993, `LESSON_TEMPLATE`'s
  opening and its replace chain as extended by plan 16A-02, where `__LANG__`
  and `__DIR__` already substitute.
- `surfaces/lesson.py` lines 1536 to 1620, the heading, list, table, and
  paragraph branches of the block classifier, which are the text-run elements
  the per-element attribute is added to.
- `surfaces/lesson.py` lines 1121 to 1160, `_callout_html`, whose body div is
  also a text run.
- `fixtures/lesson_golden_phase3_content.txt`, the first twenty lines, so it is
  clear which elements would gain an attribute and why the default path must not.
- `16A-RESEARCH.md`'s Security Domain table, the bidi-override row, verbatim.
- `fixtures/lesson_capability_corpus.py` in full as it stands after plan
  16A-07.
  </read_first>
  <behavior>
- `parse_lesson` returns a new key `dir_declared`, `True` when the
  `[LESSON-DIR:]` directive is present in the effective lesson preamble at all
  regardless of its value, and `False` when it is absent. It is present on every
  return path including both `[LESSON-SRC:]` early returns.
- A lesson with no `[LESSON-DIR:]` directive renders byte identically to before
  this task: no text-run element gains a `dir` attribute.
- A lesson writing `[LESSON-DIR: auto]` renders each `<p>`, `<li>`, each
  `<td>`, each `<figcaption>`, and each callout body `<div>` carrying
  `dir="auto"`, so each run resolves its direction from its own first strong
  character.
- A lesson writing `[LESSON-DIR: rtl]` or `[LESSON-DIR: ltr]` carries that value
  on the `<html>` element and adds no per-element attribute, because the author
  asserted one direction for the document.
- A lesson writing `[LESSON-DIR: sideways]` carries `dir="auto"` on the `<html>`
  element, adds no per-element attribute because `dir_declared` is `True` but
  the value was not `auto`, and produces the lint error
  `lesson.invalid_direction` landed by plan 16A-02.
- `build_localization_lesson(dest_dir)` writes one bank and returns its absolute
  path. The written bytes are identical across two calls into two different
  directories.
  </behavior>
  <action>
1. Add `dir_declared` to `parse_lesson`'s returned dict and to both
   `[LESSON-SRC:]` early-return dicts, following the discipline plan 16A-02
   established that every path out of the function returns the same key set. It
   is `True` when the `[LESSON-DIR:]` grab matched at all, `False` otherwise.

2. Emit the per-element direction attribute in `surfaces/lesson.py`, and only on
   the explicit opt-in path. Thread one boolean into the render `ctx` under the
   key `auto_dir`, set by `lesson_page` to `True` only when the lesson dict's
   `dir_declared` is `True` and its `dir` is `"auto"`. When `ctx["auto_dir"]` is
   truthy, the paragraph, list-item, table-cell, figcaption, and callout-body
   elements each carry `dir="auto"`. When it is falsy, every one of those
   elements is emitted exactly as it is today.

   This opt-in is the whole reason the change is additive. Emitting the
   attribute on the parsed default would add it to every paragraph of every
   existing bank, change the shipped golden content fixture's bytes, and turn
   `tests/lesson_roundtrip.py` red for a reason that has nothing to do with
   localization. Do not simplify the condition to "when dir is auto".

   Introduce no CSS rule, no color, no spacing value, and no font declaration.
   Font coverage for CJK and Arabic is Phase 17A's, and this plan names it out
   of scope below rather than reaching for it.

3. Add ten module-level constants to `fixtures/lesson_capability_corpus.py`,
   each a short synthetic string, each covering exactly one case, each written
   as an explicit Python string literal with non-ASCII characters spelled as
   `\uXXXX` escapes where that makes the intent readable in a diff:
   - `LOC_RTL`: a sentence of synthetic Arabic or Hebrew prose.
   - `LOC_MIXED_DIRECTION`: one right-to-left sentence containing a
     left-to-right inline code span and a left-to-right formula fragment, so the
     mixed code and math direction case is genuinely mixed within one run rather
     than two adjacent runs.
   - `LOC_CJK`: a sentence of synthetic Japanese or Chinese prose including at
     least one full-width punctuation mark.
   - `LOC_COMBINING`: Latin base letters followed by combining diacritics, at
     least three in a row on one base character so the stacking case is real.
   - `LOC_LONG_STRING`: one unbroken token of at least three hundred characters
     with no space, no hyphen, and no zero-width break opportunity.
   - `LOC_NUMBERS_UNITS`: a sentence containing at least four differently
     formatted numbers and units, including a comma decimal separator, a period
     decimal separator, a non-breaking space before a unit, and a degree symbol.
   - `LOC_CULTURAL`: a sentence containing a date in two formats, a family name
     written surname first, and a currency amount, with fictional values.
   - `LOC_BIDI_OVERRIDE`: a sentence containing the right-to-left override
     character, code point U+202E, written in the fixture source as the Python
     escape `\u202E`, followed by Latin text and then the pop-directional
     formatting character U+202C written as `\u202C`. Write both as escapes and
     never as literal characters, so the fixture source stays reviewable in a
     diff and no reviewing tool sees an invisible reordering control. Write a
     comment above the constant stating that this string is
     preserved byte for byte on purpose, that stripping it would corrupt
     legitimate right-to-left content, and that the display-spoofing risk is an
     accepted characteristic of any right-to-left-capable renderer, citing
     `16A-RESEARCH.md`'s Security Domain table.
   - `LOC_PRECOMPOSED` and `LOC_DECOMPOSED`: the same visible text spelled once
     with a precomposed character and once with a base plus a combining mark.
     Write a comment stating that these two must remain distinct strings through
     parse and render, and that a single `unicodedata.normalize` call anywhere
     in the path would collapse them and no other assertion in this phase would
     notice.

   Every string is fictional. None is drawn from a real course, a real exam, a
   real document, or a real person's name.

4. Add `build_localization_lesson(dest_dir)`. It writes one bank,
   `capability_localization_bank.md`, whose preamble carries
   `[LESSON-LANG: en]` and `[LESSON-DIR: auto]`, and whose `## LESSON` section
   places each of the ten constants in its own paragraph or callout under a
   `### ` heading whose text names the case in English, so a human reading the
   file can tell which case is which. Add at least one `Qn.` item so the bank
   lints as a bank.

   Write the file with an explicit `encoding="utf-8"` and no `newline`
   translation surprises: open it the same way every other builder in the module
   does, and record in the summary whether the module's established open call
   already pins the encoding.

   Run `python itembank.py lint` on the generated bank and fix the fixture until
   it exits 0 with no errors.
  </action>
  <verify>
  <automated>python tests/localization_render_check.py</automated>
Create `tests/localization_render_check.py` as part of this task, following
`tests/evidence_roundtrip.py`'s convention (shebang, standard library only,
`ROOT` plus `sys.path.insert`, a local `fail(msg)`). It asserts: `parse_lesson`
on `fixtures/lesson_bank.md` returns `dir_declared` equal to `False`; the render
of that bank is byte identical to a render captured before this task, compared
by SHA-256 recorded in the test's own temporary run rather than as a literal;
`parse_lesson` on the localization bank returns `dir_declared` equal to `True`
and `dir` equal to `auto`; the localization bank's render contains
`dir="auto"` on at least one `<p>` element; a temporary copy of the localization
bank with `[LESSON-DIR: rtl]` renders `dir="rtl"` on the `<html>` element and no
`dir="auto"` on any `<p>`; and a temporary copy with `[LESSON-DIR: sideways]`
renders `dir="auto"` on `<html>`, no per-element attribute, and produces
`lesson.invalid_direction` from `model.lint`. It prints
`localization render ok` and exits 0 on success.
The degraded state this task must also prove is the invalid-direction fallback:
the `sideways` copy must render a readable page with `dir="auto"`, never an
empty attribute and never a raised exception, which is A11Y-02's Degraded clause
in the only form this tool can offer it.
  </verify>
  <acceptance_criteria>
- `python tests/localization_render_check.py` prints `localization render ok`
  and exits 0.
- `python tests/lesson_roundtrip.py` exits 0.
- The two golden SHA-256 values in `16A-PRECONDITION.md` are unchanged.
- `python itembank.py lint` on the generated localization bank exits 0 with no
  errors.
- `grep -cE "unicodedata|normalize\\(|NFC|NFD|NFKC|NFKD" model.py surfaces/lesson.py capabilities.py`
  reports `0` across all three files.
- `grep -cE "^import (unicodedata|icu|bidi)" model.py surfaces/lesson.py capabilities.py fixtures/lesson_capability_corpus.py`
  reports `0`.
- All ten localization constants exist as module-level names in
  `fixtures/lesson_capability_corpus.py`.
- `build_localization_lesson` called twice into two different temporary
  directories produces two files with the same SHA-256.
- `python itembank.py guard .` reports `0 offending files`.
- No em dash character appears in any line this task added, including inside the
  ten fixture constants.
  </acceptance_criteria>
  <reversibility rating="costly">The explicit `[LESSON-DIR: auto]` opt-in
  becomes an authored behavior a lesson depends on for correct bidi resolution.
  Changing it later would change how existing localized lessons render, though
  no content would need migrating.</reversibility>
  <done>A lesson can declare its language and direction, an explicit auto
  declaration gives every text run its own bidi resolution, a lesson that
  declares nothing renders exactly as before, and ten synthetic cases sit in the
  corpus waiting to be asserted on.</done>
</task>

<task type="auto">
  <name>Task 2: the byte-for-byte preservation proof</name>
  <files>tests/capability_stress_corpus_tracer.py</files>
  <read_first>
- `.planning/REQUIREMENTS.md` `A11Y-02`'s Fixture sentence, verbatim: "the
  localization fixture set named above, built as synthetic strings (RTL, mixed
  code and math direction, CJK, combining marks, long strings, localized numbers
  and units) inside the 16A portable rich lesson stress corpus".
- `.planning/REQUIREMENTS.md` `PORT-01`'s clause about complete core meaning
  remaining readable outside the app.
- `fixtures/lesson_capability_corpus.py` as it stands after Task 1, in
  particular the ten constants.
- `tests/capability_stress_corpus_tracer.py` in full.
- `surfaces/lesson.py`'s `_inline` function, to confirm exactly which characters
  it escapes, so the unescaping step in the assertion reverses precisely that
  and nothing more.
- `.planning/phases/16A-semantic-capability-activity-contract/16A-VALIDATION.md`.
  </read_first>
  <action>
1. Add `scenario_localization()` to
   `tests/capability_stress_corpus_tracer.py`. It builds the localization
   lesson, reads its raw bytes, parses it, renders it in both continuous and
   guided mode, and asserts each of the following as a separately named check so
   a failure says which case broke:

   - **Source presence.** Each of the seven A11Y-02 case constants appears as a
     substring of the bank's raw UTF-8 bytes. This is PORT-01's clause for
     localized content: the non-Latin text is readable in the plain Markdown
     source with every rendered page deleted.
   - **Render preservation, per case.** For each of the seven, extract the
     rendered substring and compare `hashlib.sha256` of the source string
     against `hashlib.sha256` of the rendered substring after reversing exactly
     the escaping `_inline` applies, using `html.unescape`. Compare the two
     digests, not the raw rendered bytes: escaping a markup character is a
     legitimate transformation and normalization is not, and comparing raw bytes
     would fail on a legitimate escape and would teach a later reader to weaken
     the check.
   - **Bidi override preserved.** `LOC_BIDI_OVERRIDE`'s `\u202E` and `\u202C`
     characters are present in both the source bytes and the rendered page. Add
     a comment in the test stating that this is deliberate, that stripping them
     would corrupt legitimate right-to-left content, and that the
     display-spoofing risk is accepted and recorded.
   - **No normalization.** `LOC_PRECOMPOSED` and `LOC_DECOMPOSED` are distinct
     strings in the source and remain distinct strings in the rendered page.
     Assert their SHA-256 digests differ both before and after the round trip.
     This is the assertion a single `unicodedata.normalize` call anywhere in the
     path would fail and that nothing else in this phase would catch.
   - **Long string untruncated.** `LOC_LONG_STRING` appears in the rendered page
     in full. Assert on the whole string's presence, not on a length, because
     nothing in this phase measures a length and asserting one would invite a
     later reader to add a measurement.
   - **Both modes agree.** The guided render and the continuous render contain
     the same ten constants, so mode selection does not change what text
     survives.

2. Add the Degraded-clause assertions to the same scenario: build a temporary
   copy of the localization bank with `[LESSON-DIR: zz-invalid]` and assert the
   render carries `dir="auto"` on the `<html>` element, that every one of the
   ten constants still survives the round trip byte for byte, and that
   `model.lint` reports `lesson.invalid_direction`. An unhandled input produces
   a named finding and readable text, never corrupt text.

3. Add one negative assertion covering the whole phase's posture: assert that
   none of `model.py`, `surfaces/lesson.py`, and `capabilities.py` contains the
   substring `unicodedata`, by reading each file's source in the test. This is a
   source assertion rather than a behavior assertion on purpose: the behavior it
   guards against is invisible in output, so the only place to catch it early is
   the source.

4. Update `16A-VALIDATION.md`'s Per-Task Verification Map with two rows for plan
   16A-08's tasks, naming `tests/localization_render_check.py` and
   `scenario_localization`, with a Status of `passing`.
  </action>
  <verify>
  <automated>python tests/capability_stress_corpus_tracer.py</automated>
Expected final line: `TRACER: 13 passed, 0 skipped, 0 failed`, exit code 0. The
degraded state this task must also prove is the invalid-direction case in step
2: the render must stay readable, every constant must still survive, and the
lint finding must be present.
  </verify>
  <acceptance_criteria>
- `python tests/capability_stress_corpus_tracer.py` exits 0 with the final line
  `TRACER: 13 passed, 0 skipped, 0 failed`.
- Each of the seven A11Y-02 cases is asserted by its own named check inside
  `scenario_localization`; a grep for the seven constant names in the test file
  finds each at least once.
- `LOC_PRECOMPOSED` and `LOC_DECOMPOSED` have different SHA-256 digests in the
  source and different SHA-256 digests after the round trip.
- The rendered page contains the `\u202E` and `\u202C` characters.
- `LOC_LONG_STRING` appears in the rendered page in full.
- The `zz-invalid` direction copy renders `dir="auto"` on `<html>`, preserves
  all ten constants, and produces `lesson.invalid_direction`.
- The source assertion in step 3 passes, meaning none of the three modules
  contains the substring `unicodedata`.
- `for t in tests/*.py; do python "$t" || exit 1; done` exits 0.
- `python itembank.py guard .` reports `0 offending files`.
- `16A-VALIDATION.md` has two new filled rows naming plan `16A-08`.
- No em dash character appears in any line this task added.
  </acceptance_criteria>
  <reversibility rating="reversible">One test scenario and one validation-map
  row. Both can be rewritten without migrating content or renaming a published
  surface.</reversibility>
  <done>Seven localization cases are asserted individually, no text is
  transformed anywhere in the path, a bidi override survives on purpose with the
  risk recorded, and an unhandled direction value degrades to a named finding
  rather than to corrupt text.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| authored non-Latin text to renderer | Authored text in any script passes through parse and render, and any transformation applied there is invisible in the output to a reader who does not know both spellings. |
| bidi control characters to display | A right-to-left override embedded in authored text can visually reorder what follows it. |
| localized source to derived view | Non-Latin content is where a derived HTML view is most tempting to treat as the readable copy. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-16A-08-01 | Tampering | a normalization pass silently collapsing two distinct authored spellings | high | mitigate | The precomposed and decomposed pair must stay distinct through parse and render, asserted by differing SHA-256 digests before and after; a source assertion additionally proves the substring `unicodedata` appears in none of the three modules. |
| T-16A-08-02 | Spoofing | a bidi override character used to visually spoof authored text | medium | accept | The character is preserved byte for byte, because stripping it would corrupt legitimate right-to-left content. The risk is a documented characteristic of any right-to-left-capable renderer, the same posture every text editor and browser takes, and it is recorded in the fixture comment, in the test comment, and in the freeze record rather than papered over. Accepted at medium because the authored content in this product is authored by the learner or by an agent operating on the learner's own approved sources, so there is no untrusted third-party author in the threat model. |
| T-16A-08-03 | Tampering | a format change that is not additive, caught by a per-element attribute on the default path | high | mitigate | The per-element `dir="auto"` is emitted only on the explicit opt-in, the action forbids simplifying the condition, and the acceptance criteria re-assert both golden SHA-256 values and require `tests/lesson_roundtrip.py` green. |
| T-16A-08-04 | Denial of Service | a long unbroken token truncating or breaking the render | medium | mitigate | `LOC_LONG_STRING` is at least three hundred characters with no break opportunity and is asserted present in full in the rendered page; overflow appearance is Phase 17A's, and the assertion is about survival rather than layout. |
| T-16A-08-05 | Information Disclosure | real learner or course material entering the repository through non-Latin fixture strings | high | mitigate | Every one of the ten constants is a synthetic fictional string, non-ASCII characters are spelled as escapes where that aids review, and `python itembank.py guard .` reporting `0 offending files` is an acceptance criterion. |
| T-16A-08-06 | Tampering | supply chain: an ICU, bidi, or Unicode-segmentation dependency introduced for this work | high | mitigate | None is added and the acceptance criteria grep for exactly that. Per `PLANNING-DIRECTIVES.md` section 4a the absence of dependencies is explicitly not the mitigation: the mitigation is that any dependency ever added here is vendored at a pinned version with a recorded checksum and a named license review, following the KaTeX precedent in `09-03-PLAN.md`. |
</threat_model>

<out_of_scope>
Refused by this plan, by name, so no adjacent temptation is decided by executor
judgment:

- Any Unicode normalization, case folding, width folding, or segmentation pass,
  anywhere, for any reason.
- Any ICU binding, bidi algorithm implementation, or text-shaping library.
- Any font declaration or font vendoring for CJK or Arabic coverage. Phase 17A
  owns the type system, and a lesson whose script has no covering font is a
  visual gap that phase closes, not a semantic one this phase can.
- Any translation of the callout labels, the unsupported-block copy, the media
  copy, or any other user-visible string this phase landed. Interface
  localization is not A11Y-02's subject and no requirement in this phase asks
  for it; the capability profiles record the untranslated labels as a known
  limit.
- The A11Y-01 review: keyboard, screen reader, zoom and reflow, high contrast,
  and reduced motion. That is a different requirement with its own fixture and
  its own owning phase.
- Any per-block direction grammar beyond the document-level directive. A
  `dir` attribute on an individual callout would be new authored syntax no
  requirement asks for, and `dir="auto"` on every text run already gives each
  run its own resolution.
- The adversarial suite and the freeze gate. Plans 16A-09 and 16A-10 own them.
</out_of_scope>

<flagged_assumptions>
- **A11Y-02's two probe rows are resolved across plans 16A-02 and this one** as
  explicit criteria carried in `must_haves.truths`: the empty row in plan
  16A-02 as the absent-directive defaults and the empty-value fallback, and the
  encoding row here as byte equality of UTF-8 with no normalization anywhere and
  no length ever measured.
- **The Degraded clause is read narrowly and the reading is recorded.**
  "An unhandled locale renders a clearly-marked fallback rather than corrupt
  text" presumes locale processing this tool does not do. The reading adopted
  here is that the clause is satisfied by the two places an input can actually
  be wrong, an invalid direction and an empty language tag, both of which fall
  back with a named lint code. If a later phase adds locale-dependent formatting,
  it inherits a clause that will then have more surface to cover, and this note
  is where that phase finds the current reading.
- **A11Y-02 names seven cases and this plan builds ten constants.** The three
  extra, the bidi override and the precomposed and decomposed pair, are not
  requirement cases; they are the checks that make the seven trustworthy. They
  are recorded here so a later reader does not treat them as scope creep or
  delete them as unrequired.
- **Culturally dependent examples are exercised as an encoding and formatting
  case only.** Whether a culturally dependent example is pedagogically
  appropriate for a given learner is a course-design judgment, not something a
  fixture can assert, and no requirement in this phase asks for one.
</flagged_assumptions>

<summary_obligations>
`16A-08-SUMMARY.md` records: the ten localization constants as written, with
their escape spellings, so a reviewer can see exactly which characters were
exercised; whether the fixture module's established open call already pinned
`encoding="utf-8"` and what was done if not; the seven per-case SHA-256
comparison results; confirmation that the precomposed and decomposed digests
differ before and after the round trip; confirmation that the bidi override
characters survived and that the accepted-risk comments were written in both the
fixture and the test; the `zz-invalid` degraded result; the result of the
`unicodedata` source assertion; the tracer's final summary line verbatim; the
two golden SHA-256 values as re-verified; which truth was verified by which
command with the command's actual stdout; and any deviation from this plan with
its reason.
</summary_obligations>

<output>
Create
`.planning/phases/16A-semantic-capability-activity-contract/16A-08-SUMMARY.md`
when done.
</output>
