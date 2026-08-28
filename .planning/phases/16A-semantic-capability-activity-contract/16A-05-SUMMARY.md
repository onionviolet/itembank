# 16A-05 summary: the media registry, the figure renderer, and two readable degraded paths

**Executed 2026-08-28.** Darwin arm64, Python 3.14.6. Plan
`16A-05-PLAN.md`, three tasks, all complete.

Output: one `## MEDIA` registry parsed through the one boundary rule, one
reference form, four asset states that all render something a reader can read,
and rights proven declared rather than enforced by a byte-identity assertion.

---

## 1. The eight `MEDIA_COLUMNS` in order as written

```python
MEDIA_COLUMNS = ("id", "path", "credit", "alt", "rights", "derivation",
                 "availability", "integrity")
```

`model.py:2314`. Eight columns: an id and a path, plus CAP-02's own six media
fields verbatim, in `D-16A-7`'s order. The rows are positional, so this order is
a content contract and not a code detail.

The `rights` and `availability` vocabularies deliberately do not live in
`model.py`. `rights` is `identity.RIGHTS_STATES` reached through
`capabilities.MEDIA_RIGHTS_STATES`, and `availability` is
`capabilities.MEDIA_AVAILABILITY`, both read at lint time through a
function-local `import capabilities`.

## 2. The reference form, and whose choice it was

```
[MEDIA: <id>]
```

`model._MEDIA_REF_RE` at `model.py:845`, sitting directly under
`_SRC_DIRECTIVE_RE` and `_OBJ_DIRECTIVE_RE` so the three directive patterns stay
together.

**This is plan 16A-05's own choice, not a decision `16A-DECISIONS.md` records.**
`D-16A-7` settles the registry shape and says nothing about how a lesson refers
to a row. The form follows the shipped `[SRC: id]` and
`[OBJ: framework/id]` precedent rather than inventing a third spelling. It is
recorded here so a later phase finds the choice rather than assuming it was
handed down. It is additive and nothing outside this phase's corpus uses it yet.

A second, narrower regex governs rendering: `surfaces.lesson._MEDIA_BLOCK_RE` at
`surfaces/lesson.py:649` is anchored at both ends, so only a line that is
**only** a `[MEDIA:]` directive becomes a figure. A `[MEDIA:]` inside a
paragraph, a list item, a table cell, or a fence is left alone and renders as
literal text. That narrowing is deliberate: a figure is block-level and inlining
one would break the run it sits in.

## 3. `media.duplicate_id`'s severity, and which shipped code was checked

**Error.** The shipped code checked is `prov.src_duplicate`, at
`model.py:3727`, which handles the same class of problem for `## SOURCES` and is
appended to `errors`. All five new media codes are errors, which matches the
existing provenance-registry severities rather than guessing.

## 4. Line ranges added, so the no-visual-attribute grep is checkable

| File | Added ranges | What |
|---|---|---|
| `surfaces/lesson.py` | 643 to 649 | `_MEDIA_BLOCK_RE` and its comment |
| `surfaces/lesson.py` | 924 to 940 | `MEDIA_MISSING_COPY` and `MEDIA_REMOTE_COPY` |
| `surfaces/lesson.py` | 1282 to 1360 | `_media_figure_html` |
| `surfaces/lesson.py` | 1787 to 1798 | the `[MEDIA:]` block-classifier branch |
| `surfaces/lesson.py` | 1964 to 1972 | the `media` key seeded into the reader context |
| `surfaces/lesson.py` | 2010, 2032 to 2038 | `lesson_page`'s `media` argument and its docstring paragraph |
| `model.py` | 838 to 845 | `_MEDIA_REF_RE` |
| `model.py` | 924 to 1010 | `parse_media` |
| `model.py` | 2300 to 2315 | `MEDIA_COLUMNS` |
| `model.py` | 2420 to 2433 | `MEDIA_UNCHECKED` |
| `model.py` | 2185 to 2196 | five new SPEC lint-table rows |
| `model.py` | 3725 to 3773 | the media lint branch |

`grep -nE "width=|height=|style=|#[0-9a-fA-F]{3,6}"` matches no line inside any
of the `surfaces/lesson.py` ranges above. The figure markup carries `class`,
`id`, `src`, `alt`, and `href` and nothing else. `.media`,
`.media-unavailable`, and `.media-remote` have no CSS rule; that is a recorded
handoff to Phase 17A, in section 9.

`git diff -U0 | grep '^+' | grep -c "—"` returns `0`.

## 5. The placeholder asset

A synthetic **67-byte** one-pixel greyscale PNG, written from the literal byte
string `fixtures/lesson_capability_corpus.PLACEHOLDER_PNG`. No image library is
imported and nothing is generated at build time. It is not a photograph, not a
diagram, and not derived from anything: it exists so the `present` state has
real bytes on disk to point at.

`build_media_lesson` writes two files, not one. Pointing `present` at a file
that is not there would make `present` and `missing` render the same thing and
prove nothing.

## 6. The four media rows as generated, and the exact lint findings

| id | availability | rights | alt | notes |
|---|---|---|---|---|
| `tide-chart` | `present` | `granted` | full sentence | points at the 67-byte placeholder |
| `harbour-photo` | `missing` | `unknown` | full sentence | points at a path that does not exist |
| `remote-diagram` | `remote` | `denied` | full sentence | an `https://example.invalid/...` URL |
| `no-alt-asset` | `present` | `granted` | empty | exercises `media.missing_alt` against a real rendered image |

The lesson body carries a `[MEDIA:]` reference to each of the four plus one
`[MEDIA: ghost]`, so five references resolve to four assets.

`python itembank.py lint` on the generated bank, verbatim:

```
error  BANK: media id no-alt-asset carries no accessible alternative; the alt column is required because the alternative is the only copy a reader without the image has
error  BANK: [MEDIA: ghost] under heading 'Reading A Lock Diagram' names no id in the ## MEDIA registry
warn   Q1: no [ID:] line; run `itembank id-assign` before evidence is recorded against this item
warn   BANK: lesson heading 'Reading A Lock Diagram' is not referenced by any item's [LESSON-REF:] -- fine if it's background reading, but check it wasn't meant to be tested

1 items, 2 errors, 2 warnings
```

Exactly `media.missing_alt` and `media.ref_unknown`, and no other media code.
`media.duplicate_id`, `media.unknown_rights`, and `media.unknown_availability`
do not fire, which is correct: every id is unique, every rights value is a
member of `identity.RIGHTS_STATES`, and every availability value is a member of
`capabilities.MEDIA_AVAILABILITY`.

## 7. The rights-rewritten byte-identity result

**Byte identical.** `scenario_media_metadata`'s last leg rewrites every
`## MEDIA` row's `rights` cell to `denied`, confirms the rewrite took (the set
of rights values across all four assets is exactly `{"denied"}`), renders the
rewritten bank, and compares the two pages. They match.

That is what "declared, not enforced" means as an executable statement rather
than as a sentence, and it is the assertion that goes red the day someone
quietly adds enforcement without deciding to. `D-16A-8` names the later subphase
that owns enforcement, and names that it must re-read the current registry at
the moment of the operation rather than trusting a snapshot.

## 8. The tracer's final summary line, verbatim

```
scenario thin_slice: pass
scenario additivity_golden_parse: pass
scenario fourteen_roles: pass
scenario unknown_semantics: pass
scenario example_order: pass
scenario capability_profiles: pass
scenario unavailable_renderer: pass
scenario media_metadata: pass
TRACER: 8 passed, 0 skipped, 0 failed
```

Exit 0. `16A-VALIDATION.md`'s expected count after 16A-05 is 8.

## 9. Which truth was verified by which command

| Truth | Command | Result |
|---|---|---|
| eight columns, no second boundary scanner | `python -c "import model; print(model.MEDIA_COLUMNS)"` and `grep -c '_preamble_section(head, "MEDIA")' model.py` | the eight-member tuple; `1` |
| the rights vocabulary is referenced, not copied | `capabilities.MEDIA_RIGHTS_STATES is identity.RIGHTS_STATES` in the tracer | `True`, asserted with `is` |
| additivity: a bank with no media parses and renders unchanged | `model.parse_media('fixtures/lesson_bank.md')`, and two renders of that bank with and without `media=` | `None`; two identical strings |
| a malformed registry lints rather than raises | the media lint branch over the fixture's empty-alt row and unknown reference | two errors, no exception |
| a missing asset keeps the author's words | `scenario_media_metadata`'s missing leg | the declared alternative is in the page; no `img` points at the absent path |
| a remote asset loads nothing | the same scenario's remote leg | no `img` at that URL, one `href` to it, the locked remote copy present |
| an unknown reference is visible in both surfaces | the ghost leg plus the lint output above | `media-ghost` figure in the page; `media.ref_unknown` in lint |
| PORT-01: alternatives survive in the Markdown | the portability leg, over the bank's raw bytes | every non-empty `credit`, `alt`, and `derivation` found in the source |
| rights are declared, not enforced | the enforcement leg | rights-rewritten render byte identical |
| additivity holds | the three golden SHA-256 values | unchanged |

`python itembank.py guard .` reports `0 offending files`.

**Full suite.** The same three pre-existing red files and no others:
`tests/day_roundtrip.py`, `tests/phase_062_audit.py`, and
`tests/retention_ui_roundtrip.py`.

## 10. Deviations from the plan, with reasons

Five.

**D1. `surfaces/cli.py` was edited, and the plan's `files_modified` does not
name it.** Task 3's acceptance criteria require that
`python itembank.py lint` on the media bank report exactly `media.missing_alt`
and `media.ref_unknown`. `cmd_lint` is the only place that runs, and it passes
`lesson`, `terms`, and `keys` into `model.lint` explicitly; without a `media`
argument beside them the new checks never execute and the criterion is
unreachable. One argument was added at the one call site, plus `parse_media` to
that file's `from model import` list. A bank with no media parses to `None`, so
the media branch is skipped and the output is byte identical.

**D2. `tests/protocol_roundtrip.py`'s `LINT_PREFIXES` gained `"media"`.** That
tuple is the declared list of published lint namespaces, and every new code is
checked against it. `media` is the eighth namespace, and it is declared rather
than derived on purpose so a typo'd prefix fails by name instead of quietly
founding a ninth namespace nobody agreed to. `schemas/lint_error.schema.json`'s
`code` enum gained the same five strings, for the reason recorded as 16A-03's
D2.

**D3. `model.SPEC`'s lint table gained five media rows.** Not required by any
test, but every other published lint code has a SPEC row, and a code that lint
emits and the SPEC does not name is a contract with a hole in it.

**D4. `scenario_media_metadata` asserts two `<img>` elements, not one.** Task 3
step 2 says "the render contains exactly one `<img` element". Task 3 step 1's
own fixture spec makes `no-alt-asset` a **second** asset with `availability`
equal to `present`, and a present asset renders an image. Following both
instructions literally is arithmetically impossible. The fixture spec was kept
(the alt-less asset must be `present` for `media.missing_alt` to fire against a
real rendered image rather than against a state that renders no image anyway),
and the assertion counts two, with the reason written into the scenario. The
substantive half of the criterion, that the `<img>` for `tide-chart` carries its
declared alternative as its `alt` attribute, is asserted unchanged.

**D5. `_media_figure_html` takes `(asset, ref_id, ctx=None)` and ignores
`ctx`.** The plan names the signature `(asset_or_none, ref_id, ctx=None)`. The
argument is kept for signature compatibility with the plan and with every other
render helper in the file, and nothing in the four states needs it. It is
recorded rather than silently dropped so a later reader does not think a
context-dependent branch was lost.

## 11. Open items and recorded handoffs

- **`.media`, `.media-unavailable`, and `.media-remote` have no CSS rule.**
  Phase 17A owns appearance and sizing. No width, height, or `style` attribute
  appears on any figure or image, which is what keeps this plan inside the
  phase-shape constraint on visual scope.
- **The `integrity` column is declared and never recomputed.** A field that
  looks verified and is not is worse than one that is plainly unverified. The
  deferral is recorded here, in the plan's out-of-scope section, and belongs in
  the 16A freeze record. When the phase that owns it arrives, it should follow
  `identity.object_fingerprint`'s recompute-do-not-trust pattern.
- **A `[MEDIA:]` reference in the lesson intro, above the first `###` heading,
  renders nothing.** `lesson_page` renders one section per heading and does not
  render the intro at all, which is shipped pre-16A behavior this plan did not
  change. `parse_media` still records the reference with an empty heading, so
  `media.ref_unknown` still fires on a typo there. Recorded so the narrowness is
  a known boundary rather than a surprise.
- **`media.missing_alt` is an error, so a lesson cannot ship an undescribed
  asset.** That is deliberate: the alternative is the only copy of the picture a
  reader without the image has, which is the same reason
  `item.visual_empty_accessibility` is an error.
