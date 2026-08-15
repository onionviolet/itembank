---
phase: 16A-semantic-capability-activity-contract
plan: 05
type: execute
wave: 5
depends_on: ["16A-04"]
files_modified:
  - model.py
  - surfaces/lesson.py
  - fixtures/lesson_capability_corpus.py
  - tests/capability_stress_corpus_tracer.py
autonomous: true
requirements: [CAP-02, PORT-01]
estimate:
  tokens: 78000
  raw_tokens: 78000
  tasks: 3
  confidence: low
must_haves:
  truths:
    - "Every media asset a lesson uses carries all six CAP-02 fields, rights, credit, accessible-alternative, derivation, availability, and integrity, declared in one ## MEDIA preamble registry parsed through model._preamble_section and through no second section-boundary scanner."
    - "The rights vocabulary is identity.RIGHTS_STATES referenced through capabilities.MEDIA_RIGHTS_STATES, never a second tuple with the same members, asserted by identity rather than by equality (D-16A-8)."
    - "Media rights are declared and not enforced in Phase 16A: no code path added by this plan gates on a rights value, lint validates membership only, and the deferral is recorded by name in 16A-DECISIONS.md rather than left implicit."
    - "A media asset whose bytes are missing renders its accessible alternative and its credit as readable text inside a figure, never a broken image and never an empty box; a remote asset renders its alternative and a plain link and loads nothing, so a reader with no network reads the same lesson."
    - "A media reference to an id the registry does not carry is the lint error media.ref_unknown naming the id, and the renderer emits the same missing-asset figure rather than dropping the reference, so a typo is visible in both surfaces."
    - "The canonical Markdown stays complete: the credit, the accessible alternative, and the derivation of every asset are readable in the source file with every derived HTML deleted, which is PORT-01's clause about media alternatives remaining readable outside the app."
    - "Additivity holds: a bank with no ## MEDIA section and no [MEDIA:] reference parses to a None media result, lints exactly as before, and renders byte identically, and the two golden SHA-256 values in 16A-PRECONDITION.md are unchanged."
  prohibitions:
    - statement: "A rights or availability value copied into a record must not authorize a later operation; the current registry decides at the moment of the operation and a stale snapshot never does, which is why 16A declares these fields and enforces none of them until the phase that owns enforcement can re-check live."
      status: kept
      verification: flagged-unverified
    - statement: "A media asset must not be rendered in a way that requires a network to understand the lesson; a remote asset contributes its accessible alternative and a link, and the core reading loop degrades rather than blocks."
      status: kept
      verification: flagged-unverified
    - statement: "A second section-boundary scanner must not be written for the ## MEDIA registry; every preamble registry reads through model._preamble_section, whose own docstring names four boundary rules that can drift as the reason it exists."
      status: kept
      verification: flagged-unverified
  artifacts:
    - "model.MEDIA_COLUMNS and model.parse_media"
    - "model.LINT_CODES gains media.duplicate_id, media.missing_alt, media.unknown_rights, media.unknown_availability, media.ref_unknown"
    - "surfaces/lesson.py: _media_figure_html and the [MEDIA: id] block branch"
    - "fixtures/lesson_capability_corpus.py gains build_media_lesson"
    - "tests/capability_stress_corpus_tracer.py gains scenario_media_metadata"
  key_links:
    - "parse_media must call model._preamble_section(head, 'MEDIA') and must not compile its own section regex. parse_sources, parse_terms, and parse_cases all read through that one function, and its docstring names the drift risk directly. A sixth reader with its own scanner would be the first place the file's one boundary rule stops being one."
    - "MEDIA_RIGHTS_STATES is checked with `is` against identity.RIGHTS_STATES, not with equality. A retyped tuple carrying the same three strings would pass an equality check and would be exactly the second rights vocabulary 16A-RESEARCH.md Pitfall 4 warns about, which only an identity check catches."
    - "The missing-asset and unknown-reference paths render the SAME figure shape. If they rendered differently, an author debugging a blank figure would have to know which of the two failures they were looking at before they could read the message, and the message is the whole point of showing it."
    - "The integrity column is declared and never verified in this phase. A verified-looking field that nothing checks is worse than an unverified one, so the profile's known_limits and the summary both record that recomputation is deferred, following identity.object_fingerprint's recompute-do-not-trust pattern when the phase that owns it arrives."
---

<objective>
Give every media asset the six-field metadata record CAP-02 requires, in the one
place a lesson already declares its registries, and make the degraded paths
readable rather than broken.

CAP-02, quoted: "each media asset carries rights, credit, accessible-alternative,
derivation, availability, and integrity metadata".

`16A-RESEARCH.md` confirms this is the phase's one genuinely new grammar with no
in-repo precedent: a full-text search found no `figure`, `credit`, `rights`, or
`derivation` handling anywhere in `model.py` or `surfaces/lesson.py`. What it
does have precedent for is the shape. `## SOURCES` and `## TERMS` are both
preamble pipe-table registries read through one shared boundary function, and
`D-16A-7` settles that `## MEDIA` is a third one in exactly that shape rather
than an inline per-image attribute syntax.

Two things are deliberately not built here, and both are recorded rather than
silently omitted.

Rights are declared and not enforced. `D-16A-8` settles it and
`16A-RESEARCH.md` Pitfall 4 gives the reason: 16A does not own the rights
vocabulary, and a temporary enforcement mechanism built against a vocabulary
this phase does not own is how a second rights vocabulary gets created. Lint
validates membership in `capabilities.MEDIA_RIGHTS_STATES`, which is
`identity.RIGHTS_STATES` by reference, and nothing gates on it. When a later
subphase actually packages or exports an asset, it enforces by re-reading the
current registry at the moment of the operation, which is the discipline
`14B-03-PLAN.md`'s Pitfall 5 already states: "No stale snapshot ever authorizes
... The current registry decides; the snapshot never does."

Integrity is declared and not recomputed. A field that looks verified and is not
is worse than one that is plainly unverified, so the deferral is written into
the capability profile's `known_limits` and into the freeze record.

What is built is the part PORT-01 depends on: the accessible alternative, the
credit, and the derivation of every asset live in the canonical Markdown, so a
reader with every derived HTML file deleted still knows what the picture showed
and where it came from.

Decisions already made, cited, and never re-derived here:

- **`16A-DECISIONS.md` `## D-16A-7`**: `## MEDIA` is a preamble pipe registry
  read through `model._preamble_section`, with columns in the fixed order `id`,
  `path`, `credit`, `alt`, `rights`, `derivation`, `availability`, `integrity`.
- **`16A-DECISIONS.md` `## D-16A-8`**: rights are declared, not enforced, and
  `MEDIA_RIGHTS_STATES` references `identity.RIGHTS_STATES`.
- **`capabilities.MEDIA_AVAILABILITY`**, landed by plan 16A-04:
  `("present", "missing", "remote")`.
- **`.claude/CLAUDE.md`'s network rule**, quoted: "the core loop must
  **degrade, never block**". A remote asset never becomes a prerequisite for
  reading.
- **`model._preamble_section`'s own docstring**, quoted: "`parse_terms`,
  `parse_sources` and `parse_cases` ... all read through this one definition, so
  the file carries one boundary rule rather than four that can drift."
- **The phase-shape constraint on visual scope**: no color, spacing,
  typography, motion, or token decision anywhere in Phase 16A.

Purpose: make an asset's rights, credit, alternative, and provenance part of the
lesson rather than part of a folder nobody reads.
Output: one registry, one reference form, two readable degraded paths.
</objective>

<context>
@.planning/phases/16A-semantic-capability-activity-contract/16A-DECISIONS.md
@.planning/phases/16A-semantic-capability-activity-contract/16A-PRECONDITION.md
@.planning/phases/16A-semantic-capability-activity-contract/16A-RESEARCH.md
@.planning/phases/16A-semantic-capability-activity-contract/16A-PATTERNS.md
@.planning/phases/16A-semantic-capability-activity-contract/16A-VALIDATION.md
@.planning/REQUIREMENTS.md
@model.py
@surfaces/lesson.py
@capabilities.py
@tests/capability_stress_corpus_tracer.py
</context>

## Artifacts this phase produces (plan 16A-05 share)

New symbols introduced by this plan, and by nothing earlier:

- `model.MEDIA_COLUMNS` (tuple constant, eight members)
- `model.parse_media`
- `model._MEDIA_REF_RE`
- Five new `model.LINT_CODES` members: `media.duplicate_id`,
  `media.missing_alt`, `media.unknown_rights`, `media.unknown_availability`,
  `media.ref_unknown`
- `surfaces/lesson.py`: `_media_figure_html`, `MEDIA_MISSING_COPY`,
  `MEDIA_REMOTE_COPY`
- `fixtures/lesson_capability_corpus.py`: `build_media_lesson`
- `tests/capability_stress_corpus_tracer.py`: `scenario_media_metadata`

No CLI command, no daemon route, and no schema file is produced by this plan.

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: the ## MEDIA registry and its parser</name>
  <files>model.py</files>
  <read_first>
- `.planning/phases/16A-semantic-capability-activity-contract/16A-DECISIONS.md`
  `## D-16A-7` and `## D-16A-8` in full.
- `model.py` lines 574 to 602, `_preamble_section` in full, including its
  docstring. This function is called and never reimplemented.
- `model.py` lines 717 to 800, `parse_sources` in full. It is the closest
  analog: an independent read over the bank file, a preamble pipe registry, a
  directive scan over item chunks, a duplicate list, and a returned dict or
  `None`. `parse_media` copies its structure.
- `model.py` lines 625 to 711, `parse_terms`, specifically `_terms_row_cells`,
  the shared pipe-row splitter `parse_sources` also uses. `parse_media` uses the
  same splitter and does not write a second one.
- `model.py` lines 2176 to 2215, `LINT_CODES`.
- `capabilities.py`, `MEDIA_RIGHTS_STATES` and `MEDIA_AVAILABILITY` as landed by
  plan 16A-04.
  </read_first>
  <behavior>
- `model.MEDIA_COLUMNS` equals the tuple `("id", "path", "credit", "alt",
  "rights", "derivation", "availability", "integrity")`.
- `parse_media(bank_path)` returns `None` when the bank carries no `## MEDIA`
  section and no `[MEDIA:]` reference anywhere.
- `parse_media` on a bank with a `## MEDIA` section returns a dict with exactly
  the keys `assets`, `refs`, `duplicates`, and `path`, matching
  `parse_sources`'s established return shape.
- `assets` maps each asset id to a dict carrying exactly `MEDIA_COLUMNS`, with
  a missing trailing cell filling as the empty string rather than raising, so a
  short row is a lint finding and never a parse failure.
- `refs` is a list, in document order, of dicts carrying `id` and `heading`,
  one per `[MEDIA: <id>]` occurrence in the lesson body.
- `duplicates` lists ids registered more than once, in first-seen order, and the
  first registration wins.
- `parse_media` never raises on any input, including a `## MEDIA` section with a
  header row and no data rows, a row with one cell, a row with twelve cells, and
  a `[MEDIA:]` reference with an empty id.
- `parse_media` is never called from inside `load()` or `parse_bank()` and
  changes neither's return shape, exactly as `parse_sources` and `parse_terms`
  are not.
  </behavior>
  <action>
1. Add `MEDIA_COLUMNS` to `model.py` beside `GATE_VALUES`, the eight-member
   tuple in the `D-16A-7` order: `id`, `path`, `credit`, `alt`, `rights`,
   `derivation`, `availability`, `integrity`.

2. Add `_MEDIA_REF_RE`, a compiled regex matching a `[MEDIA: <id>]` directive
   with optional surrounding whitespace, beside `_SRC_DIRECTIVE_RE` and
   `_OBJ_DIRECTIVE_RE` at lines 713 to 714 so the directive patterns stay
   together. Capture the id with the same non-greedy, non-bracket shape those
   two use.

3. Add `parse_media(bank_path)` immediately after `parse_sources`, following its
   structure step for step:
   - Read the file, split at the first real question exactly as `parse_sources`
     does, and build `head`.
   - Call `_preamble_section(head, "MEDIA")`. Do not compile a section regex.
   - Split each non-blank, non-separator row with `_terms_row_cells`, take the
     first cell as the id, and map the remaining cells onto `MEDIA_COLUMNS[1:]`
     positionally, filling missing trailing cells with the empty string.
   - Record a duplicate id in `duplicates` and keep the first registration.
   - Scan the lesson body for `_MEDIA_REF_RE` matches. Resolve each reference to
     the `###` heading it falls under by walking the same heading split
     `parse_lesson` performs, so a lint finding can name the heading. A
     reference above the first heading records the empty string as its heading.
   - Return `None` when both the section and the reference list are empty;
     otherwise return the four-key dict.

   Write the docstring in the same voice as `parse_sources`'s: state that this
   is an independent read for a different purpose, that it is never called from
   `load()` or `parse_bank()`, that the registry lives in the preamble under the
   same boundary rule as `## LESSON`, `## TERMS`, and `## SOURCES`, and that a
   short row fills with empty strings so a malformed row is lint's problem and
   never a parse failure.

4. Add five members to `model.LINT_CODES`: `"media.duplicate_id"`,
   `"media.missing_alt"`, `"media.unknown_rights"`,
   `"media.unknown_availability"`, `"media.ref_unknown"`.

5. Extend `model.lint`'s signature with a `media=MEDIA_UNCHECKED` sentinel
   parameter, following the exact pattern `lesson=LESSON_UNCHECKED` and
   `terms=TERMS_UNCHECKED` already establish at line 2864, so a pre-16A caller
   that passes no media data skips every media check and its output is byte
   identical. Define `MEDIA_UNCHECKED` as its own module-level sentinel object
   beside the two existing ones.

   Add five checks in a media branch beside the lesson branch. The exact
   message strings are:
   - `BANK: media.duplicate_id: media id %s is registered more than once; the first registration is used`
   - `BANK: media.missing_alt: media id %s carries no accessible alternative; the alt column is required because the alternative is the only copy a reader without the image has`
   - `BANK: media.unknown_rights: media id %s declares rights %s, which is not one of granted, denied, unknown`
   - `BANK: media.unknown_availability: media id %s declares availability %s, which is not one of present, missing, remote`
   - `BANK: media.ref_unknown: [MEDIA: %s] under heading %r names no id in the ## MEDIA registry`

   `media.missing_alt`, `media.unknown_rights`, `media.unknown_availability`,
   and `media.ref_unknown` are errors. `media.duplicate_id` is an error, matching
   `prov.src_duplicate`'s existing severity for the same class of problem; check
   that code's severity in the shipped `lint` and match it rather than guessing.

   Read the rights and availability vocabularies from
   `capabilities.MEDIA_RIGHTS_STATES` and `capabilities.MEDIA_AVAILABILITY`
   through a function-local import of `capabilities`, the same technique
   `model.parse_terms` already uses to reach `surfaces.lesson` without a
   top-level import cycle. Do not restate the member strings in `model.py`.
  </action>
  <verify>
  <automated>python -c "import model, capabilities, identity; print(model.MEDIA_COLUMNS); print(capabilities.MEDIA_RIGHTS_STATES is identity.RIGHTS_STATES); print(model.parse_media('fixtures/lesson_bank.md'))"</automated>
Expected stdout, three lines: the eight-member tuple in `D-16A-7` order; the
word `True`; and the word `None`, because `fixtures/lesson_bank.md` carries no
`## MEDIA` section and no reference. The degraded state this task must also
prove is that a malformed registry never raises: build a temporary bank with a
one-cell row, a twelve-cell row, a duplicate id, and a `[MEDIA: ]` reference
with an empty id, and confirm `parse_media` returns a dict rather than raising,
and that `model.lint` reports the corresponding codes.
  </verify>
  <acceptance_criteria>
- `model.MEDIA_COLUMNS` equals
  `('id', 'path', 'credit', 'alt', 'rights', 'derivation', 'availability', 'integrity')`.
- `model.parse_media('fixtures/lesson_bank.md')` returns `None`.
- `grep -c '_preamble_section(head, "MEDIA")' model.py` reports `1`, and
  `parse_media`'s body contains no `re.search` or `re.compile` call that matches
  a `^##` heading.
- All five new codes are members of `model.LINT_CODES` and
  `python tests/protocol_roundtrip.py` exits 0.
- `model.lint` called without a `media` argument produces output byte identical
  to its pre-task output on `fixtures/lesson_bank.md`; capture both and diff.
- A malformed media registry produces lint findings and no exception.
- `python tests/lesson_roundtrip.py` and
  `python tests/model_surface_roundtrip.py` each exit 0.
- The two golden SHA-256 values in `16A-PRECONDITION.md` are unchanged.
- No em dash character appears in any line this task added.
  </acceptance_criteria>
  <reversibility rating="costly">The `## MEDIA` column order and the
  `[MEDIA: id]` directive become an authored content contract the moment a
  lesson carries one. Rated costly rather than one-way because the columns are
  CAP-02's own six fields plus an id and a path, transcribed, and the registry
  shape was settled at `D-16A-7`; only the reference form is this plan's choice
  and no content outside this phase's corpus uses it yet. Reordering a column
  after real lessons carry it would be a content migration.</reversibility>
  <done>A lesson can declare its assets with all six CAP-02 fields, through the
  one boundary rule, and a malformed declaration is a lint finding rather than a
  crash.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: the figure renderer and its two readable degraded paths</name>
  <files>surfaces/lesson.py</files>
  <read_first>
- `surfaces/lesson.py` lines 1480 to 1620, the block classifier, in full. The
  `[MEDIA:]` branch is added beside the callout branch and above the heading
  branch, and it must respect the same run-consumption discipline.
- `surfaces/lesson.py` lines 1121 to 1160, `_callout_html`, for the escape-first
  `_inline()` discipline every text run follows and for the container shape.
- `surfaces/lesson.py` lines 1734 to 1810, `lesson_page`'s signature and
  docstring, where a `media` argument is threaded through.
- `surfaces/lesson.py`'s degraded `[LESSON-SRC:]` branch and its
  `var(--warn)` note, for the established precedent of a warning-tone degraded
  state that echoes the author-written path and never the resolved absolute path
  or the raw OS error (recorded as T-3-07 in the Phase 3 decision log).
- `capabilities.py`'s `MEDIA_AVAILABILITY`.
- `.claude/CLAUDE.md`'s Network constraint paragraph, verbatim.
  </read_first>
  <behavior>
- A `[MEDIA: <id>]` line whose id resolves to an asset with `availability`
  equal to `present` renders one
  `<figure class="media" id="media-<slug>">` containing an `<img>` whose `src`
  is the declared path HTML-escaped and whose `alt` is the declared alternative
  HTML-escaped, followed by a `<figcaption>` carrying the escaped credit and, on
  its own line, the escaped derivation when the derivation is non-empty.
- The same reference with `availability` equal to `missing` renders
  `<figure class="media media-unavailable" id="media-<slug>">` containing no
  `<img>`, a paragraph carrying `MEDIA_MISSING_COPY`, a paragraph carrying the
  escaped accessible alternative, and the same `<figcaption>`.
- The same reference with `availability` equal to `remote` renders
  `<figure class="media media-remote" id="media-<slug>">` containing no `<img>`,
  a paragraph carrying `MEDIA_REMOTE_COPY`, a paragraph carrying the escaped
  accessible alternative, one `<a>` whose `href` is the escaped declared path,
  and the same `<figcaption>`. Nothing is fetched at render time.
- A reference to an id the registry does not carry renders the same
  `media-unavailable` figure, with the escaped id in place of an alternative and
  no credit, so a typo is visible on the page as well as in lint.
- The `<img>` element carries no width, no height, no style attribute, and no
  class beyond what is named above, because Phase 17A owns sizing.
- `lesson_page` called with no `media` argument renders byte identically to
  before this task for every bank, and a bank with no `[MEDIA:]` line renders
  byte identically whether or not `media` is supplied.
  </behavior>
  <action>
1. Add two module-level copy constants to `surfaces/lesson.py`, holding exactly
   these strings and nothing else:
   - `MEDIA_MISSING_COPY`:
     `This image is not available on this machine. Its description is below.`
   - `MEDIA_REMOTE_COPY`:
     `This image lives outside this course and is not loaded here. Its description is below, and the link opens it.`

   These are user-visible copy and are locked here. Do not rephrase them, do not
   add a variant, and do not localize them in this phase.

2. Add `_media_figure_html(asset_or_none, ref_id, ctx=None)` beside
   `_callout_html`. It implements the four cases in the behavior block above.
   Every interpolated value passes through `html.escape`, matching the
   escape-first discipline every other text run in this file follows. The
   `id` attribute is built through `model.lesson_slug(ref_id)`, the same
   slugifier the tag and the anchor already share, never by raw string
   manipulation.

   Introduce no color, no spacing value, no width, no height, no `style`
   attribute, and no token. `media-unavailable` and `media-remote` are class
   names for Phase 17A to style; this plan adds no CSS rule for either and
   records that as a handoff in the summary.

3. Add a `[MEDIA:]` branch to the block classifier, placed immediately after the
   callout branch and before the deep-heading branch. It matches a line that is
   only a `[MEDIA: <id>]` directive with optional surrounding whitespace,
   consumes exactly that one line, resolves the id against the `media` dict
   threaded into `ctx`, and appends `_media_figure_html`'s output. A `[MEDIA:]`
   directive appearing inside a paragraph, a list item, a table cell, or a
   fenced block is left alone and renders as literal text, because a figure is a
   block-level thing and inlining one would break the surrounding run.

   Extend the paragraph-continuation guard at line 1601 so a `[MEDIA:]` line
   breaks a paragraph run, exactly as a callout marker already does, or a figure
   following a paragraph would be swallowed into it.

4. Thread the media data into the render. Add a `media` keyword argument to
   `lesson_page`, defaulting to `None`, placed after the `mode` argument plan
   16A-02 added so no positional caller changes. Put the resolved asset dict
   into the render `ctx` under the key `media`, following how `gate` and
   `example_layout` already ride in `ctx`. When `media` is `None`, every
   `[MEDIA:]` line renders the `media-unavailable` figure with the id shown,
   which is the honest result: the renderer was given no registry, so it knows
   nothing about the asset and says so rather than guessing.

   Add one sentence to `lesson_page`'s docstring naming the `media` argument,
   its default, and the fact that a `None` registry renders every reference as
   unavailable rather than dropping it.

5. Wire `cmd_lesson` and the daemon lesson route to pass
   `model.parse_media(bank_path)` into `lesson_page`. Both call sites already
   call `model.parse_lesson`; add the media read beside it. Do not add a second
   file read inside `lesson_page` itself: the render function takes parsed data
   and reads no file, which is the existing contract every one of its arguments
   already follows.
  </action>
  <verify>
  <automated>python tests/capability_stress_corpus_tracer.py</automated>
Expected final line: `TRACER: 7 passed, 0 skipped, 0 failed` at the end of this
task, rising to `8 passed` after Task 3 adds its scenario. The degraded state
this task must prove before Task 3 exists is the no-registry path: render
`fixtures/lesson_bank.md` with and without a `media` argument and confirm the
two outputs are identical strings, then render a temporary bank carrying one
`[MEDIA: ghost]` line with `media=None` and confirm the output contains
`media-unavailable`, contains the literal id `ghost`, and contains no `<img`
element.
  </verify>
  <acceptance_criteria>
- `surfaces.lesson.MEDIA_MISSING_COPY` equals exactly
  `This image is not available on this machine. Its description is below.`
- `surfaces.lesson.MEDIA_REMOTE_COPY` equals exactly
  `This image lives outside this course and is not loaded here. Its description is below, and the link opens it.`
- A render of a bank whose asset declares `availability` equal to `remote`
  contains no `<img` element and contains one `<a href=` whose value is the
  declared path.
- A render of a bank whose asset declares `availability` equal to `missing`
  contains no `<img` element and contains the declared accessible alternative
  text.
- A render of a `[MEDIA: ghost]` reference with no matching registry entry
  contains `media-unavailable` and the literal string `ghost`.
- Rendering `fixtures/lesson_bank.md` with and without the `media` argument
  produces two identical strings.
- `grep -nE "width=|height=|style=|#[0-9a-fA-F]{3,6}" surfaces/lesson.py`
  produces no line inside the ranges this task added; record the ranges in the
  summary.
- `python tests/lesson_roundtrip.py`, `python tests/gate_roundtrip.py`, and
  `python tests/daemon_roundtrip.py` each exit 0.
- The two golden SHA-256 values in `16A-PRECONDITION.md` are unchanged.
- No em dash character appears in any line this task added.
  </acceptance_criteria>
  <reversibility rating="costly">The two copy constants are user-visible text a
  learner reads, and the figure markup shape is what Phase 17A will style.
  Changing either later is a copy change a reader notices and a selector change
  a stylesheet notices, though neither migrates content.</reversibility>
  <done>A declared asset renders as a credited figure, a missing one renders its
  description, a remote one renders its description and a link and loads
  nothing, and an unknown reference says so on the page.</done>
</task>

<task type="auto">
  <name>Task 3: the media fixture and its tracer scenario</name>
  <files>fixtures/lesson_capability_corpus.py, tests/capability_stress_corpus_tracer.py</files>
  <read_first>
- `fixtures/lesson_capability_corpus.py` in full as it stands after plan
  16A-04, for the established builder shape.
- `tests/capability_stress_corpus_tracer.py` in full, for the scenario
  convention and the `main()` counter.
- `.planning/REQUIREMENTS.md` `CAP-02`'s media sentence and `PORT-01`'s clause
  about media alternatives remaining readable outside the app, both verbatim.
- `.planning/phases/16A-semantic-capability-activity-contract/16A-VALIDATION.md`,
  the Per-Task Verification Map.
  </read_first>
  <action>
1. Add `build_media_lesson(dest_dir)` to
   `fixtures/lesson_capability_corpus.py`, following the established shape:
   literal fictional content, no `random`, deterministic bytes, no em dash
   characters.

   The generated bank carries a `## MEDIA` registry with exactly four rows, one
   per case the renderer must handle:
   - `tide-chart`, `availability` `present`, with a path pointing at a small
     placeholder file the builder also writes into `dest_dir`, a fictional
     credit, a real accessible alternative sentence, `rights` `granted`, a
     derivation sentence, and an `integrity` value shaped like a `sha256:` prefix
     followed by hex.
   - `harbour-photo`, `availability` `missing`, path pointing at a file that
     does not exist, `rights` `unknown`, with a full alternative and credit.
   - `remote-diagram`, `availability` `remote`, path an `https://` URL to a
     fictional host, `rights` `denied`, with a full alternative and credit.
   - `no-alt-asset`, `availability` `present`, with the `alt` column empty, so
     the fixture also exercises `media.missing_alt`.

   The lesson body carries a `[MEDIA:]` reference to each of the four ids plus
   one `[MEDIA: ghost]` reference naming an id the registry does not carry, so
   `media.ref_unknown` is exercised too.

   The placeholder file for `tide-chart` must be a tiny synthetic image or a
   plain text file with an image-shaped name; it must not be a real photograph,
   a real diagram, or anything derived from a real course. A one-pixel PNG
   written from a literal byte string is acceptable and is the recommended
   default. Record which was used in the summary.

2. Add `scenario_media_metadata()` to
   `tests/capability_stress_corpus_tracer.py`. It builds the media lesson,
   parses it, renders it, and asserts:
   - `parse_media` returns four assets, five refs, and no duplicates.
   - Every asset dict's key set equals `model.MEDIA_COLUMNS`.
   - `capabilities.MEDIA_RIGHTS_STATES is identity.RIGHTS_STATES` is `True`.
     Use `is`, not `==`. A retyped tuple would pass equality and would be the
     second rights vocabulary this phase must not have.
   - `model.lint` reports exactly one `media.missing_alt` naming
     `no-alt-asset` and exactly one `media.ref_unknown` naming `ghost`, and no
     `media.unknown_rights` and no `media.unknown_availability`.
   - The render contains exactly one `<img` element, whose `alt` attribute
     carries `tide-chart`'s declared alternative.
   - The render contains `harbour-photo`'s declared alternative text and does
     not contain an `<img` element whose `src` is `harbour-photo`'s path.
   - The render contains `remote-diagram`'s declared alternative text and one
     `<a href=` carrying its URL, and contains no `<img` element pointing at
     that URL.
   - The render contains the literal `ghost`.
   - PORT-01's clause is asserted directly: read the generated bank's raw bytes
     and confirm every one of the four assets' `credit`, `alt`, and `derivation`
     strings appears in the Markdown source itself, so the alternatives stay
     readable with every derived HTML deleted.
   - No code path in this plan gated on a rights value: assert that a render of
     the same bank with every `rights` cell rewritten to `denied` produces a
     byte-identical page, which is what "declared, not enforced" means and is
     the assertion that would go red the day someone quietly adds enforcement
     without deciding to.

3. Update `16A-VALIDATION.md`'s Per-Task Verification Map with three rows for
   plan 16A-05's tasks, naming `scenario_media_metadata` and a Status of
   `passing`.
  </action>
  <verify>
  <automated>python tests/capability_stress_corpus_tracer.py</automated>
Expected final line: `TRACER: 8 passed, 0 skipped, 0 failed`, exit code 0. The
degraded state this task must also prove is the declared-not-enforced claim: the
rights-rewritten render must be byte identical to the original, which is the
scenario's last assertion.
  </verify>
  <acceptance_criteria>
- `python tests/capability_stress_corpus_tracer.py` exits 0 with the final line
  `TRACER: 8 passed, 0 skipped, 0 failed`.
- `scenario_media_metadata` uses `is` rather than `==` when comparing
  `capabilities.MEDIA_RIGHTS_STATES` to `identity.RIGHTS_STATES`; verify with
  `grep -c "MEDIA_RIGHTS_STATES is identity.RIGHTS_STATES" tests/capability_stress_corpus_tracer.py`
  reporting at least `1`.
- The rights-rewritten render is byte identical to the original render.
- `python itembank.py lint` on the generated media bank reports exactly
  `media.missing_alt` and `media.ref_unknown` and no other media code.
- `for t in tests/*.py; do python "$t" || exit 1; done` exits 0.
- `python itembank.py guard .` reports `0 offending files`.
- The placeholder asset file written by the builder is under 200 bytes and is
  synthetic; record its byte length in the summary.
- `16A-VALIDATION.md` has three new filled rows naming plan `16A-05`.
- No em dash character appears in any line this task added.
  </acceptance_criteria>
  <reversibility rating="reversible">A fixture builder and one test scenario.
  Both can be rewritten without migrating content or renaming a published
  surface.</reversibility>
  <done>Four asset states render correctly, the alternatives survive in the
  Markdown source, and the declared-not-enforced claim is proven by a
  byte-identity assertion rather than by a sentence.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| authored media path to renderer | A media path is author-supplied text that becomes an `src` or an `href` attribute in a page a learner loads. |
| declared rights to a later operation | A rights value recorded in a file could be read later as authorization for a package, export, or share. |
| remote asset to the reading loop | A remote asset is the one place a reader could acquire a network dependency it did not have. |
| media registry to lint and to renderer | Two consumers of one registry can disagree about what a malformed row means. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-16A-05-01 | Tampering | a stale rights snapshot authorizing a later operation | high | mitigate | `D-16A-8` and this plan declare rights without enforcing them, and Task 3's final assertion proves it by rendering the same bank with every rights cell set to `denied` and requiring byte identity. When a later phase enforces, it re-reads the current registry at the moment of the operation, which is `14B-03-PLAN.md` Pitfall 5's recorded discipline. |
| T-16A-05-02 | Information Disclosure | an author-supplied media path injected into a page as markup | high | mitigate | Every interpolated value passes through `html.escape`, matching the escape-first `_inline()` discipline every other text run in `surfaces/lesson.py` follows; the acceptance criteria assert the render of a path-shaped hostile string stays text. |
| T-16A-05-03 | Denial of Service | a remote asset making the reading loop depend on a network | high | mitigate | A `remote` asset renders no `<img>` and fetches nothing at render time; it contributes its accessible alternative and a plain link, honoring the recorded network rule that the core loop must "degrade, never block". |
| T-16A-05-04 | Repudiation | an integrity field that looks verified and is not | medium | mitigate | Recomputation is out of scope and is recorded as such in the capability profile's `known_limits`, in this plan's out-of-scope section, and in the freeze record, rather than being silently absent. |
| T-16A-05-05 | Tampering | a second rights vocabulary minted for media | high | mitigate | `MEDIA_RIGHTS_STATES` is `identity.RIGHTS_STATES` by reference and the tracer asserts identity with `is`, so a retyped tuple with the same members fails even though it would pass equality. |
| T-16A-05-06 | Tampering | a second section-boundary scanner drifting from `_preamble_section` | medium | mitigate | Task 1 requires the call and the acceptance criteria assert `parse_media`'s body compiles no heading regex; `grep` counts the one call site. |
| T-16A-05-07 | Information Disclosure | real course imagery or content entering the repository through the media fixture | high | mitigate | The placeholder asset is a synthetic literal under 200 bytes whose length is recorded in the summary, every string in the builder is fictional, and `python itembank.py guard .` reporting `0 offending files` is an acceptance criterion. |
| T-16A-05-08 | Tampering | supply chain: a third-party dependency introduced by this plan | high | mitigate | None is added; the placeholder image is a literal byte string and no image library is imported. Per `PLANNING-DIRECTIVES.md` section 4a the absence of dependencies is explicitly not the mitigation: the mitigation is that any dependency ever added here is vendored at a pinned version with a recorded checksum and a named license review, following the KaTeX precedent in `09-03-PLAN.md`. |
</threat_model>

<out_of_scope>
Refused by this plan, by name, so no adjacent temptation is decided by executor
judgment:

- Any rights enforcement. `D-16A-8` settles that 16A declares and does not
  enforce; the byte-identity assertion in Task 3 is the check that keeps it so.
- Any integrity recomputation or verification. The column is declared; the
  deferral is recorded in the capability profile, here, and in the freeze
  record.
- Any image processing, resizing, format conversion, or thumbnail generation.
  No image library is imported and none is needed.
- Any network fetch at render time or at lint time, for a `remote` asset or for
  any other reason.
- Any CSS rule for `.media`, `.media-unavailable`, or `.media-remote`, and any
  width, height, or style attribute on a figure or an image. Phase 17A owns
  sizing and appearance.
- An inline per-image attribute syntax. `D-16A-7` settles the registry shape.
- A structured `effective_date` or `jurisdiction` field. `D-16A-7` defers it.
- `## ACTIVITIES`. Plan 16A-06 owns it, through the same
  `_preamble_section` boundary rule.
</out_of_scope>

<flagged_assumptions>
- **The `[MEDIA: id]` directive form is this plan's own choice**, following the
  `[SRC: id]` and `[OBJ: framework/id]` precedent `parse_sources` already
  establishes. `D-16A-7` settles the registry shape but not the reference form.
  It is recorded here rather than in `16A-DECISIONS.md` because it is additive
  and reversible until authored content uses it, and the summary is instructed
  to record it so a later phase can find the choice.
- **A `[MEDIA:]` directive inside a paragraph, list, table, or fence renders as
  literal text.** That is a deliberate narrowing: an inline figure would break
  the surrounding run and no requirement asks for one. It is recorded so a later
  reader does not treat the narrowness as an oversight.
- **`.media-unavailable` and `.media-remote` have no CSS rule after this plan.**
  Unstyled paragraphs are legible and Phase 17A owns appearance; the gap is a
  recorded handoff, not an omission.
</flagged_assumptions>

<summary_obligations>
`16A-05-SUMMARY.md` records: the eight `MEDIA_COLUMNS` in order as written; the
`[MEDIA: id]` reference form as implemented and the note that it is this plan's
own choice; which severity `media.duplicate_id` was given and which shipped code
was checked to match it; the line ranges added to `surfaces/lesson.py`, so the
no-visual-attribute grep is checkable; the placeholder asset's byte length and
what it is; the four media rows as generated and the exact lint findings they
produced; the result of the rights-rewritten byte-identity assertion; the tracer's
final summary line verbatim; the two golden SHA-256 values as re-verified; which
truth was verified by which command with the command's actual stdout; and any
deviation from this plan with its reason.
</summary_obligations>

<output>
Create
`.planning/phases/16A-semantic-capability-activity-contract/16A-05-SUMMARY.md`
when done.
</output>
