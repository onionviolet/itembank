# 16A-08 summary: seven localization cases, one direction opt-in, and a proof that nothing is transformed

**Executed 2026-08-28.** Darwin arm64, Python 3.14.6. Plan
`16A-08-PLAN.md`, two tasks, both complete.

Output: ten named fixture constants, an explicit per-element direction opt-in
that keeps the shipped goldens green, and a preservation proof that fails the
day anyone adds a normalization pass.

---

## 1. The seven A11Y-02 cases and the three encoding probes

Ten module-level constants in `fixtures/lesson_capability_corpus.py`, each a
short synthetic string, each covering exactly one case. They are ten named
constants rather than one blob on purpose: a single fixture string could pass
its assertion while one case had been quietly dropped from it, and seven
constants each asserted by name cannot.

| Constant | Case | What makes it a real test |
|---|---|---|
| `LOC_RTL` | RTL | synthetic Arabic prose |
| `LOC_MIXED_DIRECTION` | mixed code and math direction | one RTL sentence carrying an LTR inline code span and an LTR formula fragment, mixed **within one run** rather than as two adjacent runs |
| `LOC_CJK` | CJK | Japanese prose including a full-width period |
| `LOC_COMBINING` | combining marks | four diacritics stacked on one base character |
| `LOC_LONG_STRING` | long strings | one unbroken 318-character token with no space, hyphen, or zero-width break opportunity |
| `LOC_NUMBERS_UNITS` | localized numbers and units | a comma decimal, a period decimal, a non-breaking space before a unit, and a degree symbol |
| `LOC_CULTURAL` | culturally dependent examples | one date in two formats, a family name written surname first, and a currency amount, all fictional |
| `LOC_BIDI_OVERRIDE` | (probe) | U+202E and U+202C, written as escapes |
| `LOC_PRECOMPOSED` / `LOC_DECOMPOSED` | (probe) | the same visible text, two spellings |

Non-ASCII characters are spelled as `\uXXXX` escapes throughout, so the fixture
source stays reviewable in a diff. For `LOC_BIDI_OVERRIDE` that is not just
convenience: writing U+202E as a literal would mean every diff viewer and code
review tool showed the reordering happening.

## 2. The bidi override is preserved on purpose, and the risk is accepted

U+202E RIGHT-TO-LEFT OVERRIDE and U+202C POP DIRECTIONAL FORMATTING pass
through parse and render byte for byte, asserted in both the source bytes and
the rendered page.

**Stripping them would corrupt legitimate right-to-left content.** The
display-spoofing risk they carry is an accepted characteristic of any
right-to-left-capable renderer, and it is the same posture every text editor and
browser takes. It is recorded in three places rather than papered over: a
comment above the fixture constant, a comment in the tracer's bidi assertion,
and this summary, which is what the 16A freeze record should carry forward.

The threat register rates it **medium and accepted**, and the reason is worth
repeating because it is specific to this product: the authored content here is
authored by the learner or by an agent operating on the learner's own approved
sources, so there is no untrusted third-party author in the threat model. That
reasoning changes if external installs ever accept banks from strangers, which
is Phase 18's problem to notice.

## 3. The precomposed and decomposed pair, and why it is the sharpest check

`LOC_PRECOMPOSED` spells its text with U+00E9; `LOC_DECOMPOSED` spells the same
visible text as `e` plus U+0301. They look identical on screen.

The scenario asserts their SHA-256 digests differ in the source **and** differ
after the round trip. A single `unicodedata.normalize` call anywhere in the
parse or render path would collapse them into one string, and **no other
assertion in this phase would notice**, because both spellings render to the
same pixels.

A source assertion backs it up, in both the tracer and
`tests/localization_render_check.py`: none of `model.py`,
`surfaces/lesson.py`, or `capabilities.py` contains the substring
`unicodedata`.

```
$ grep -cE "unicodedata|NFC|NFD|NFKC|NFKD" model.py surfaces/lesson.py capabilities.py
surfaces/lesson.py:0
model.py:0
capabilities.py:0
```

No ICU binding, no bidi algorithm, no Unicode segmentation library, and no
normalization pass was added. That absence is the deliverable.

## 4. The direction opt-in, and why it is three conditions and not one

`model.parse_lesson` gains `dir_declared`, present on every return path
including both `[LESSON-SRC:]` early returns. It is `True` when the
`[LESSON-DIR:]` directive is present at all, whatever its value.

`surfaces/lesson.py`'s `_dir_attr(ctx)` emits ` dir="auto"` on paragraphs, list
items, table cells, figcaptions, and callout bodies, and `lesson_page` sets
`ctx["auto_dir"]` only when **all three** of these hold:

1. `dir_declared` is `True`, so the author wrote the directive at all.
2. `dir_raw` is empty, so the value survived validation and nothing was refused.
3. `dir` is `"auto"`.

The plan named the first and third. The second was added during execution and is
deviation D1 below: `[LESSON-DIR: sideways]` falls back to `"auto"`, so
conditions 1 and 3 alone would have treated a **refused** value as a
declaration, which is exactly what the plan's own behavior block forbids.

The four behaviors, all asserted:

| Directive | `<html>` | per-element |
|---|---|---|
| absent | `dir="auto"` (shipped) | none |
| `[LESSON-DIR: auto]` | `dir="auto"` | `dir="auto"` on every text run |
| `[LESSON-DIR: rtl]` | `dir="rtl"` | none, because the author asserted one direction |
| `[LESSON-DIR: sideways]` | `dir="auto"` | none, plus `lesson.invalid_direction` |

Emitting the attribute on the parsed default would have added it to every
paragraph of every existing bank, changed
`fixtures/lesson_golden_phase3_content.txt`'s bytes, and turned
`tests/lesson_roundtrip.py` red for a reason unrelated to localization. The
explicit opt-in is what makes this addition additive, and the golden values
below are the proof it worked.

## 5. A11Y-02's Degraded clause, read honestly

"An unhandled locale renders a clearly-marked fallback rather than corrupt text"
presumes a tool that processes locales. **This one does not.** It emits `lang`
and `dir` attributes and passes raw UTF-8 through, so there is no transformation
in which a locale could be mishandled into corrupt text.

The clause is satisfied in the two places where an input can actually be wrong,
both landed by plan 16A-02 and both asserted here: a direction outside
`("ltr", "rtl", "auto")` falls back to `auto` with `lesson.invalid_direction`,
and an empty language tag falls back to `en` with `lesson.lang_empty`. The
tracer's degraded leg additionally asserts that under an invalid direction **all
ten constants still round-trip byte for byte**, which is the real content of
"rather than corrupt text".

## 6. The encoding pin, and determinism

`build_localization_lesson` opens with `encoding="utf-8"` and `newline="\n"`,
which is what every other builder in
`fixtures/lesson_capability_corpus.py` already does; the module's established
open call **does** pin the encoding, so nothing had to change. Two builds into
two different temporary directories produce files with the same SHA-256,
asserted directly.

`python itembank.py lint` on the generated bank: `1 items, 0 errors, 10
warnings`. The ten warnings are one unminted-id warning and nine
`lesson.orphan_heading` warnings, one per case heading that no item references,
which is correct: the localization cases are material to render, not material to
test.

## 7. The tracer's final summary line, verbatim

```
scenario thin_slice: pass
scenario additivity_golden_parse: pass
scenario fourteen_roles: pass
scenario unknown_semantics: pass
scenario example_order: pass
scenario capability_profiles: pass
scenario unavailable_renderer: pass
scenario media_metadata: pass
scenario activity_declarations: pass
scenario unsupported_response_form: pass
scenario output_modes: pass
scenario backburner_catalog: pass
scenario localization: pass
TRACER: 13 passed, 0 skipped, 0 failed
```

Exit 0. `16A-VALIDATION.md`'s expected count after 16A-08 is 13.

`tests/localization_render_check.py` prints `localization render ok` and
exits 0.

## 8. The additivity proof, re-verified

```
fixtures/lesson_golden_phase3_parse.json 4078e7532ed33b341a6d551791d8ecc72175e1e479c63420b56db2b635a8e5aa
fixtures/lesson_golden_phase3_content.txt 800edb4cc180cda67885dc558e6784e713e9d636f9ebf8336919c1df93318a3c
fixtures/lesson_bank.md e34d5c9d3c2c16115257d5b1640f8aa9386e037ff6a15bc1eb6480d82c64398e
```

Unchanged, which is the direct evidence that the per-element attribute did not
leak onto the default path. `python itembank.py guard .` reports
`0 offending files`. `git diff -U0 | grep '^+' | grep -c "—"` returns `0`.

**Full suite.** The same three pre-existing red files and no others:
`tests/day_roundtrip.py`, `tests/phase_062_audit.py`, and
`tests/retention_ui_roundtrip.py`.

## 9. Which truth was verified by which command

| Truth | Command | Result |
|---|---|---|
| seven cases exist as named constants and reach the corpus | `scenario_localization`'s source leg | each found in the canonical Markdown |
| nothing is transformed | the per-case SHA-256 comparison in both modes | thirteen strings, two renders each, all digests equal |
| no normalization anywhere | the precomposed/decomposed digests plus the `unicodedata` source assertion | digests differ before and after; `0` in all three modules |
| a bidi override survives | the bidi leg | U+202E and U+202C present in source and page |
| a long string is not truncated | the long-string leg | the whole 318-character token present |
| both modes agree | every case asserted against the guided render too | pass |
| the opt-in is explicit | `check_undeclared_bank_unchanged` plus the golden hashes | no per-element attribute on the default path; goldens unchanged |
| an invalid direction degrades | `check_invalid_direction_degrades` and the tracer's degraded leg | `dir="auto"`, no empty attribute, no exception, all ten constants intact, `lesson.invalid_direction` present |

## 10. Deviations from the plan, with reasons

Three.

**D1. The per-element opt-in requires three conditions, not the two the plan
named.** Task 1 step 2 says to set the flag "only when the lesson dict's
`dir_declared` is `True` and its `dir` is `"auto"`". Those two alone treat
`[LESSON-DIR: sideways]` as an opt-in, because an invalid value falls back to
`"auto"` while leaving `dir_declared` `True`. That directly contradicts the same
task's own behavior block, which says a `sideways` lesson "adds no per-element
attribute because `dir_declared` is `True` but the value was not `auto`". The
third condition, `dir_raw` empty, is what distinguishes a value the author wrote
from a value the parser fell back to. It was found by
`check_invalid_direction_degrades` failing, which is the check doing its job.

**D2. `fixtures/lesson_capability_corpus.LOCALIZATION_RENDERED` and
`LOC_MIXED_DIRECTION_RENDERED` were added, and the plan's artifact list does not
name them.** The mixed-direction constant carries a Markdown inline code span,
because the plan requires it to contain "a left-to-right inline code span", and
the renderer turns a code span into a `<code>` element. That is a legitimate
transformation of **markup**, exactly as HTML escaping is, and the plan already
handles the escaping case by comparing after `html.unescape`. Rather than
weakening the assertion to ignore markup, one declared rendered form is
registered for that one case, and every other case is compared against its
source string unchanged. Every character of the mixed constant other than the
two backticks is identical between the two forms, so the Arabic run, the
identifier, and the formula fragment are all still asserted byte for byte.

**D3. `tests/lesson_roundtrip.py` and `tests/gate_roundtrip.py` gained
`dir_declared` in their `additive_defaults` dicts.** The same additivity floor
16A-03's D4 records: both files list the keys later phases added to
`parse_lesson`, each asserted to hold its documented default before being
dropped from a byte comparison. `dir_declared` is now asserted to read `False`
on a bank carrying no directive.

## 11. Open items recorded rather than filled

- **Font coverage for CJK and Arabic is Phase 17A's.** This plan adds no font
  declaration and no CSS rule. The fixture proves the bytes survive; whether the
  glyphs render on a given machine is a font-stack question 17A owns.
- **Layout of the long unbroken token is Phase 17A's.** The assertion is that
  the token survives in full, not that it wraps or scrolls well. Nothing in this
  phase measures a length, deliberately: asserting one would invite a later
  reader to add a measurement, and a measurement in code points or grapheme
  clusters is the first step toward a segmentation library.
- **The seven cases are rendered but not reviewed by a human.** A11Y-01's
  keyboard, screen-reader, zoom, contrast, and reduced-motion review is a
  different requirement this plan does not own, and plan 16A-10's freeze-gate
  human review is where a person reads this corpus.
- **`dir="auto"` is not emitted on `<th>` cells.** The table renderer emits
  header cells through a separate path; the opt-in covers `<td>`, `<p>`, `<li>`,
  `<figcaption>`, and callout bodies. A header cell in a mixed-direction table
  would resolve from the document direction rather than from its own content.
  Recorded as a known narrow spot rather than fixed, because widening it is a
  one-line change a later phase can make with a fixture that actually has a
  mixed-direction table header.
