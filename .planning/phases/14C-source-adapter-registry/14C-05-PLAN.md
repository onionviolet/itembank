---
phase: 14C-source-adapter-registry
plan: 05
type: execute
wave: 5
depends_on: ["14C-04"]
files_modified:
  - source_adapters.py
  - fixtures/audit/transcript_fidelity_cases.py
  - tests/source_adapters_roundtrip.py
autonomous: true
requirements: [D-01, D-05, ROSTER-4-TRANSCRIPT, TREAT-02]
estimate:
  tokens: 110000
  raw_tokens: 55000
  tasks: 2
  confidence: low
must_haves:
  truths:
    - "A learner-supplied .srt file, a .vtt file, and a plain bracketed-timestamp transcript all extract to Markdown through the one transcript adapter, and every emitted locator carries integer start_ms and end_ms so a citation names a moment rather than a line number."
    - "The timestamp locator is proven end to end before any ASR backend exists, which is the entire reason roster item 4 is sequenced ahead of roster item 5."
    - "The transcript parser is hand-rolled stdlib regex with no third-party dependency, so the transcript adapter works on a machine where none of the six pinned adapter packages is installed."
    - "A malformed cue, a missing timestamp line, an out-of-order cue, and an end time earlier than its start time each produce a typed refusal or a recorded unsupported entry naming the cue number, never a silently dropped line and never a negative duration."
    - "WebVTT cue settings, region blocks, style blocks, and NOTE comments are recognized and skipped without breaking the cue stream, and each skipped construct appears in the sidecar unsupported list so the loss is reported rather than silent."
  prohibitions:
    - statement: "No second parser, scorer, or evidence store. The transcript grammar is a cue reader, not a document model; span identity still comes from auditor.normalize_source over the derived Markdown."
      status: flagged-unverified
      verification: "check_no_second_parser is re-run; git diff --stat model.py runtime.py auditor.py reports no change."
    - statement: "No rewrite of itembank in TypeScript and no plugin kernel reimplemented in Python."
      status: flagged-unverified
      verification: "files_modified contains three Python files, none of them a loader or kernel module."
    - statement: "No hosted multi-tenant anything."
      status: flagged-unverified
      verification: "every fixture materializes into a tempfile.mkdtemp() base; the fixture module writes nothing in the repository."
    - statement: "PyMuPDF and ebooklib are not adopted, and webvtt-py is not adopted."
      status: flagged-unverified
      verification: "grep -i -E 'pymupdf|fitz|ebooklib|webvtt' source_adapters.py deps/source-adapter-pins.txt finds no import and no pin line for any of the four."
    - statement: "An unresolved rights grant is never treated as permissive."
      status: flagged-unverified
      verification: "check_rights_refusal is re-run with a transcript input."
  artifacts:
    - "fixtures/audit/transcript_fidelity_cases.py with its own CASE_TABLE, sha256 helper, and materialize function"
    - "_extract_transcript, _parse_srt, _parse_vtt, _parse_plain_timestamps, and _timestamp_to_ms in source_adapters.py"
    - "the transcript key in ADAPTER_REGISTRY"
    - "check_transcript_gold_cases, check_transcript_timestamp_locators, and check_transcript_no_dependency in tests/source_adapters_roundtrip.py"
  key_links:
    - "SRT separates a timestamp's seconds from its milliseconds with a comma and WebVTT uses a period. A single regex that accepts either is correct and is what _timestamp_to_ms takes; two separate parsers that each accept only their own separator will silently reject half the real files a learner has, because exported captions are routinely renamed between the two extensions without being reformatted."
    - "WebVTT timestamps may omit the hour field entirely (MM:SS.mmm). A regex that requires HH: silently rejects most real WebVTT files, which is the single most likely way this adapter fails on real material rather than on fixtures."
    - "start_ms and end_ms are plain integer milliseconds, per 14C-CONTEXT.md's own wording and the frozen body_transcript row. They are deliberately not a Media Fragments URI string: that syntax exists for browser interoperability, which does not apply to an internal JSON sidecar, and parsing it back would be a second grammar."
---

<objective>
Land transcript intake. `14C-CONTEXT.md` roster item 4 sequences it ahead of ASR
for one reason, stated there: a learner-supplied `.srt`, `.vtt`, or plain
timestamped transcript needs no ASR dependency, so it lands cheaply and proves
the timestamp locator. When roster item 5 eventually arrives, ASR is a new way
of producing cues, not a new locator shape and not a new sidecar field.

This is also the one adapter in the phase with no third-party dependency at all,
which makes it the honest test of the degrade-never-block claim: with none of the
six pinned packages installed, transcript intake still works end to end.

Decisions already made, cited, and never re-litigated here:

- **D-01** and `14C-RESEARCH.md`'s Standard Stack row: the SRT and VTT grammars
  are two trivial line grammars and a hand-rolled stdlib regex parser is the
  right call. `webvtt-py` 0.5.1 exists and is MIT, and it does not clear
  `SUPPLY-CHAIN-POLICY.md` section 3's "it does not earn its cost" bar for a
  grammar this small. The reconsideration condition is recorded in RESEARCH's
  Alternatives table: adopt it if the hand-rolled parser proves fragile on real
  transcript files.
- **D-05**: the adapter never touches the scorer.
- **D-14C-1** (`14C-DECISIONS.md`): the frozen `body_transcript` row, required
  `medium` const `"transcript"`, `cue_index`, `start_ms`, `end_ms`.
- **`14C-CONTEXT.md`'s locator table**: video and audio locate by start and end
  timestamps in milliseconds.

Purpose: prove the timestamp locator with no dependency and no backend.
Output: one more registry entry, one gold-case fixture file, and the tests.
</objective>

<execution_context>
@$HOME/.claude/gsd-core/workflows/execute-plan.md
@$HOME/.claude/gsd-core/templates/summary.md
</execution_context>

<context>
@.planning/phases/14C-source-adapter-registry/14C-CONTEXT.md
@.planning/phases/14C-source-adapter-registry/14C-RESEARCH.md
@.planning/phases/14C-source-adapter-registry/14C-PATTERNS.md
@.planning/phases/14C-source-adapter-registry/14C-VALIDATION.md
@.planning/phases/14C-source-adapter-registry/14C-DECISIONS.md
@.planning/phases/14C-source-adapter-registry/14C-01-PLAN.md
@fixtures/audit/locator_fidelity_cases.py
@source_adapters.py
</context>

## Artifacts this phase produces (plan 14C-05 share)

- `fixtures/audit/transcript_fidelity_cases.py`
  - `sha256`, `CASE_TABLE`, `materialize(dest_dir)`, and three builders
    `srt_bytes(cues)`, `vtt_bytes(cues, header_blocks=None)`,
    `plain_bytes(lines)`.
- `source_adapters.py`
  - New functions `_timestamp_to_ms(text)`, `_parse_srt(text)`,
    `_parse_vtt(text)`, `_parse_plain_timestamps(text)`,
    `_extract_transcript(raw_bytes, options)`.
  - New constants `TIMESTAMP_RE`, `CUE_ARROW`, `VTT_SKIP_BLOCKS`.
  - `ADAPTER_REGISTRY` gains `"transcript"`; `ADAPTER_VERSIONS` gains
    `"transcript": "1.0.0"`.
- `tests/source_adapters_roundtrip.py`
  - `check_transcript_gold_cases`, `check_transcript_timestamp_locators`,
    `check_transcript_no_dependency`.

New refusal codes introduced by this plan: none. `source.malformed_input` and
`source.unsupported` are already in `SOURCE_ADAPTER_CODES`.

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: transcript gold cases across all three input shapes</name>
  <files>fixtures/audit/transcript_fidelity_cases.py, tests/source_adapters_roundtrip.py</files>
  <read_first>
- `fixtures/audit/locator_fidelity_cases.py` lines 1 to 30 (the stdlib-only,
  deterministic, repository-independent fixture contract), 26 to 28 (`sha256`),
  183 to 205 (one complete case dict for the shape), and 613 to 626
  (`materialize`).
- `fixtures/audit/pptx_fidelity_cases.py` and
  `fixtures/audit/web_capture_fidelity_cases.py` as built by plans `14C-03` and
  `14C-04`, the two most recent members of this file family.
- `.planning/phases/14C-source-adapter-registry/14C-VALIDATION.md`, the
  "Roster 4 transcript" row: `.srt` and `.vtt` byte fixtures produce `start_ms`
  and `end_ms` locators.
  </read_first>
  <behavior>
Write `check_transcript_fixture_determinism` first, watch it fail, then build.

- Every case's `build()` is byte-stable across two calls in one process and
  hashes to its recorded `gold["sha256"]`.
- `materialize()` writes only inside the temporary directory it is given.
- The fixture module has no attribute named `webvtt` after import, proving it
  builds its bytes by hand rather than with a library.
  </behavior>
  <action>
1. Create `fixtures/audit/transcript_fidelity_cases.py` with a module docstring
   in the register of its three sibling fixture files: name the phase and plan
   (14C, plan `14C-05`), state that the case table is immutable data, the
   builders are pure functions, nothing reads or writes the repository, and
   imports are stdlib only (`hashlib`, `os`). Add one sentence stating that
   these fixtures are the timestamp locator's acceptance corpus and that roster
   item 5, ASR, will reuse them unchanged, because ASR produces cues and does
   not produce a new locator shape.

2. Build these eight cases. Every `gold` records `sha256`, `structures`,
   `reading_order`, `unsupported`, and `adapter_expectation`.
   - `srt-three-cues`, filename `lecture.srt`: three numbered cues with
     `HH:MM:SS,mmm --> HH:MM:SS,mmm` timing lines and one text line each.
     `reading_order` is `["c.0", "c.1", "c.2"]`. `adapter_expectation`
     `"supported"`.
   - `srt-multiline-cue`, filename `lecture-multiline.srt`: one cue whose text
     spans three lines, which must join into one locator and one Markdown line,
     not three. `reading_order` is `["c.0"]`.
   - `srt-bom-and-crlf`, filename `lecture-bom.srt`: the `srt-three-cues`
     content prefixed with a UTF-8 byte order mark and using CRLF line endings,
     which is what a Windows-exported caption file actually looks like.
     `reading_order` is the same three ids, which is the point: the BOM and the
     line endings must not shift the parse.
   - `vtt-hour-omitted`, filename `lecture.vtt`: a `WEBVTT` header followed by
     three cues whose timing lines use `MM:SS.mmm --> MM:SS.mmm` with no hour
     field. `reading_order` is `["c.0", "c.1", "c.2"]`. This is the case that
     goes red if the timestamp regex requires an hour field.
   - `vtt-with-settings-and-notes`, filename `lecture-styled.vtt`: a `WEBVTT`
     header, a `NOTE` comment block, a `STYLE` block, a `REGION` block, then two
     cues whose timing lines carry cue settings after the end timestamp
     (`align:start position:10%`). `reading_order` is `["c.0", "c.1"]`, and
     `unsupported` records three entries naming the skipped `NOTE`, `STYLE`,
     and `REGION` blocks. `adapter_expectation` `"supported"`, because the deck
     of cues extracts; the skipped blocks are recorded loss, not a whole-file
     refusal.
   - `plain-bracketed-timestamps`, filename `lecture-notes.txt`: plain lines
     each beginning `[HH:MM:SS]` followed by text, the shape a learner produces
     by hand or by pasting from a video player. Each line becomes one cue whose
     `end_ms` is the next line's `start_ms`, and whose final line's `end_ms`
     equals its own `start_ms`. `reading_order` is `["c.0", "c.1", "c.2"]`.
   - `srt-end-before-start`, filename `lecture-inverted.srt`: two valid cues and
     one whose end timestamp precedes its start. `reading_order` is the two
     valid ids and `unsupported` records
     `["cue 2: end timestamp precedes start timestamp"]`.
     `adapter_expectation` `"supported"`.
   - `transcript-no-timestamps`, filename `lecture-plain.txt`: prose with no
     timestamp of any shape. `structures` and `reading_order` are empty,
     `unsupported` is `["no timestamped cue found"]`, `adapter_expectation`
     `"unsupported"`. A transcript with no timestamps is a plain text file and
     belongs to the `text` adapter; the refusal message says so.

3. Compute each case's `sha256` by running the builder once and recording the
   result. Do not hand-write a hash.

4. Implement `materialize(dest_dir)` in the same shape the three sibling fixture
   files use.

5. Add `check_transcript_fixture_determinism` to
   `tests/source_adapters_roundtrip.py` and to its `__main__` sequence.
  </action>
  <verify>
  <automated>python3 tests/source_adapters_roundtrip.py</automated>
Expected: exit 0. The degraded state this task must prove is fixture drift
detection: a builder whose output no longer hashes to its recorded gold fails
the check, which is the same guarantee the three sibling fixture files give.
  </verify>
  <acceptance_criteria>
- `python3 tests/source_adapters_roundtrip.py` exits 0.
- `python3 -c "import sys,os; sys.path.insert(0,os.path.join('fixtures','audit')); import transcript_fidelity_cases as g; assert len(g.CASE_TABLE)==8; assert all(set(c['gold'])>={'sha256','structures','reading_order','unsupported','adapter_expectation'} for c in g.CASE_TABLE); print('transcript fixtures ok')"` prints `transcript fixtures ok`.
- `python3 -c "import sys,os; sys.path.insert(0,os.path.join('fixtures','audit')); import transcript_fidelity_cases as g; assert not hasattr(g,'webvtt'); print('fixture is stdlib only')"` prints `fixture is stdlib only`.
- `python3 -c "import sys,os,tempfile,shutil; sys.path.insert(0,os.path.join('fixtures','audit')); import transcript_fidelity_cases as g; d=tempfile.mkdtemp(); r=g.materialize(d); assert len(r)==8; shutil.rmtree(d); print('materialize ok')"` prints `materialize ok`.
- `python3 itembank.py guard .` exits 0.
- The new fixture file contains no em dash character.
  </acceptance_criteria>
  <precondition>fixtures/audit/ exists and tests import fixture modules through sys.path.insert.</precondition>
  <reversibility rating="reversible">A new fixture file with no consumers until Task 2.</reversibility>
  <done>Eight deterministic transcript fixtures cover SRT, WebVTT, and plain bracketed timestamps, including the four ways real caption files differ from tidy ones.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: the transcript adapter, one timestamp grammar for three input shapes</name>
  <files>source_adapters.py, tests/source_adapters_roundtrip.py</files>
  <read_first>
- `fixtures/audit/transcript_fidelity_cases.py` as built in Task 1, all eight
  cases and their recorded reading orders and unsupported messages.
- `source_adapters.py` as landed by plans `14C-01` through `14C-04`: the
  four-tuple extraction contract comment above `ADAPTER_REGISTRY`,
  `unsupported_result`, and the way `_extract_markdown` handles a
  `UnicodeDecodeError`.
- The frozen `body_transcript` row in `14C-01-PLAN.md`'s "The frozen sidecar
  contract" section: required `medium` const `"transcript"`, `cue_index`
  integer minimum 0, `start_ms` integer minimum 0, `end_ms` integer minimum 0.
- `.planning/phases/14C-source-adapter-registry/14C-RESEARCH.md`, the Standard
  Stack "stdlib regex-based SRT/VTT parser" row and the Don't Hand-Roll table
  row for SRT and VTT, which is the one row in that table that says building it
  is correct.
  </read_first>
  <behavior>
Write these assertions first, watch them fail, then implement.

- `check_transcript_gold_cases`: each of the eight cases produces exactly its
  recorded `reading_order` and its recorded `unsupported` messages when
  `adapter_expectation` is `"supported"`, and a typed refusal whose message
  equals the recorded `unsupported[0]` string when it is `"unsupported"`.
- `check_transcript_timestamp_locators`: for `srt-three-cues`, the three
  locators carry `start_ms` values of exactly the millisecond integers the
  fixture encoded, `end_ms` strictly greater than `start_ms` for each, and
  `cue_index` values of 0, 1, and 2. For `vtt-hour-omitted`, the same
  assertions hold with hour-less timestamps, which proves the hour field is
  optional in the regex.
- `check_transcript_separator_tolerance`: an SRT file renamed to `.vtt` and a
  WebVTT file renamed to `.srt` both parse, because format detection reads the
  content and never the filename extension. Build these two inputs inside the
  test from the existing fixture bytes rather than adding two more gold cases.
- `check_transcript_no_dependency`: with every one of `pdfplumber`, `pdfminer`,
  `docx`, `pptx`, and `readability` forced unimportable in the process,
  `import_source(adapter="transcript", ...)` still returns `ok` with a
  schema-valid sidecar and one applied journal entry. This is the phase's
  cleanest proof of degrade-never-block.
- `check_transcript_end_to_end`: one SRT case imported through
  `source_adapters.import_source` produces a schema-valid sidecar whose
  `reading_order` length equals the derived Markdown's line count, and one
  applied journal entry.
  </behavior>
  <action>
1. Add `TIMESTAMP_RE` to `source_adapters.py`: a single compiled regex matching
   `(?:(\d+):)?(\d{1,2}):(\d{2})[.,](\d{1,3})`, so the hour group is optional and
   the fractional separator is a comma or a period. One regex covers SRT and
   WebVTT because exported caption files are routinely renamed between the two
   extensions without being reformatted, and a parser that accepts only its own
   separator silently rejects half of a learner's real files. Record that
   sentence in a comment above the constant.

2. Add `_timestamp_to_ms(text)` returning an integer millisecond count, or
   `None` when the text does not match. Pad a one-digit or two-digit fractional
   part to three digits rather than treating `1:02.5` as 5 milliseconds; a
   half-second is 500 milliseconds and getting this wrong is a silent
   hundred-fold error in every cue.

3. Add `_parse_srt(text)` returning `(cues, unsupported)`. A cue is a dict with
   `index`, `start_ms`, `end_ms`, and `text`. Split on blank lines, tolerate a
   leading numeric index line and tolerate its absence, find the line containing
   `CUE_ARROW` (the literal `-->`), parse the two timestamps around it, and join
   every remaining line of the block with a single space into one cue text. A
   block with no arrow line appends
   `"cue %d: no timestamp line" % block_number` to `unsupported` and is skipped.
   A cue whose `end_ms` is less than its `start_ms` appends
   `"cue %d: end timestamp precedes start timestamp" % block_number` and is
   skipped; it is never emitted with a negative duration.

4. Add `_parse_vtt(text)` returning the same pair. Skip the `WEBVTT` header
   line and any header metadata lines before the first blank line. Recognize and
   skip a block whose first line begins with any member of
   `VTT_SKIP_BLOCKS = ("NOTE", "STYLE", "REGION")`, appending
   `"skipped a %s block" % keyword` to `unsupported` for each so the loss is
   reported rather than silent. On a timing line, parse only up to the second
   timestamp and discard the trailing cue settings, which are presentation and
   not content. Otherwise identical to `_parse_srt`.

5. Add `_parse_plain_timestamps(text)` returning the same pair. Each line
   beginning with a bracketed timestamp becomes one cue whose `start_ms` is that
   timestamp and whose `end_ms` is the next cue's `start_ms`; the last cue's
   `end_ms` equals its own `start_ms`, because a final line has no known
   duration and inventing one would put a wrong number in a citation. Record
   that reasoning in the function docstring. A line with no bracketed timestamp
   is appended to the preceding cue's text, so a wrapped paragraph does not
   become a lost line.

6. Add `_extract_transcript(raw_bytes, options)`. Decode as UTF-8, stripping a
   leading byte order mark and normalizing CRLF to LF before any parsing, so the
   `srt-bom-and-crlf` case parses identically to the plain one. Detect the shape
   from the content and never from a filename: a first non-blank line equal to
   `WEBVTT` selects `_parse_vtt`; otherwise a body containing `CUE_ARROW`
   selects `_parse_srt`; otherwise a body with at least one bracketed timestamp
   at a line start selects `_parse_plain_timestamps`; otherwise return the
   refusal `no timestamped cue found`. Emit one locator per cue with id
   `"c.%d" % cue_index`, `kind` `"cue"`, and body
   `{"medium": "transcript", "cue_index": ..., "start_ms": ..., "end_ms": ...}`.
   Emit one Markdown line per cue, prefixed with the cue's start timestamp in
   `[HH:MM:SS]` form followed by a space, so the derived Markdown is readable
   on its own and a human reading it can find the moment without the sidecar.

7. Register `"transcript"` in `ADAPTER_REGISTRY` and add
   `"transcript": "1.0.0"` to `ADAPTER_VERSIONS`. This adapter imports nothing
   outside the standard library, so it has no lazy-import guard and no
   `source.dependency_missing` path; state that in a comment beside its registry
   entry so a later reader does not add one for symmetry.

8. Set the sidecar envelope `confidence` to `"high"` for SRT and WebVTT, whose
   timings are declared by the file, and to `"medium"` for the plain bracketed
   shape, whose `end_ms` values are inferred from the following cue rather than
   declared. The `confidence` field exists for exactly this distinction.

9. Add every check named in the `behavior` block to
   `tests/source_adapters_roundtrip.py` and to its `__main__` sequence.
  </action>
  <verify>
  <automated>python3 tests/source_adapters_roundtrip.py</automated>
Expected: exit 0. The degraded state this task must prove is
`check_transcript_no_dependency`: with all five third-party adapter libraries
forced unimportable, a transcript still imports end to end with a schema-valid
sidecar and an applied journal entry.
  </verify>
  <acceptance_criteria>
- `python3 tests/source_adapters_roundtrip.py` exits 0.
- `python3 -c "import source_adapters as s; assert 'transcript' in s.ADAPTER_REGISTRY and s.ADAPTER_VERSIONS['transcript']=='1.0.0'; print('transcript registered')"` prints `transcript registered`.
- `python3 -c "import source_adapters as s; assert s._timestamp_to_ms('00:01:02,500')==62500; assert s._timestamp_to_ms('01:02.500')==62500; assert s._timestamp_to_ms('00:00:01.5')==1500; assert s._timestamp_to_ms('nope') is None; print('timestamps ok')"` prints `timestamps ok`.
- `python3 -c "import source_adapters as s; assert s.VTT_SKIP_BLOCKS==('NOTE','STYLE','REGION'); print('vtt blocks ok')"` prints `vtt blocks ok`.
- `grep -c "end timestamp precedes start timestamp" source_adapters.py` returns
  at least 1.
- `grep -c "no timestamped cue found" source_adapters.py` returns at least 1.
- `python3 schema_validate.py --all` exits 0.
- `for t in tests/*.py; do python3 "$t" || exit 1; done` exits 0.
- `python3 itembank.py guard .` exits 0.
- `git diff --stat runtime.py model.py auditor.py journal.py` reports no change.
- No file changed by this task contains an em dash character.
  </acceptance_criteria>
  <precondition>Task 1's fixture file exists. No third-party package is needed by this task at all.</precondition>
  <reversibility rating="reversible">One registry entry and four private parsing functions.</reversibility>
  <done>Three transcript input shapes parse through one timestamp grammar, every cue carries integer milliseconds, and the whole path works with zero third-party packages installed.</done>
</task>

</tasks>

<threat_model>
ASVS level 1. Block on `high`.

## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| Learner-supplied transcript bytes to the cue parser | An arbitrary text file, possibly very large or adversarially shaped, reaches a regex-driven parser. |
| Adapter to durable disk | Derived Markdown and a sidecar are written under the approved root. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-14C-31 | Denial of Service | catastrophic regex backtracking on a crafted line | high | mitigate | `TIMESTAMP_RE` uses only bounded quantifiers (`\d{1,2}`, `\d{2}`, `\d{1,3}`) and one unbounded `\d+` for the optional hour, with no nested quantifier and no alternation inside a repeated group, so it cannot backtrack catastrophically. `check_transcript_gold_cases` includes a wall-clock bound so a future edit that introduces a nested quantifier fails the test rather than hanging the suite. |
| T-14C-32 | Denial of Service | an enormous transcript file | medium | mitigate | `import_source` caps the input at `options["max_input_bytes"]` before the adapter sees it, from plan `14C-01` step 10c. The parser is a single linear pass with no quadratic join. |
| T-14C-33 | Tampering | a cue with a negative or inverted duration reaching a citation | medium | mitigate | A cue whose `end_ms` precedes its `start_ms` is refused by name and never emitted, so no locator can carry a negative duration. The frozen `body_transcript` schema additionally sets `minimum: 0` on both fields, so an invalid pair fails `schema_validate.validate` before the sidecar is written. |
| T-14C-34 | Repudiation | inferred end times presented as declared ones | medium | mitigate | The plain bracketed shape's `end_ms` values are inferred from the following cue, so the sidecar envelope `confidence` is set to `"medium"` rather than `"high"` for that shape. A citation into an inferred timing carries the honest confidence rather than an invented certainty. |
| T-14C-35 | Information Disclosure | transcript content on disk | low | accept | A learner's own transcript stays under their approved root. Nothing transmits it. |
| T-14C-SC | Tampering | npm/pip/cargo installs | high | mitigate | No package at all is introduced or used by this plan. `webvtt-py` is refused on the "does not earn its cost" test in `SUPPLY-CHAIN-POLICY.md` section 3 and appears in no pin line. `deps/source-adapter-pins.txt` is not edited here. |
</threat_model>

<out_of_scope>
- **ASR.** Roster item 5 is registered and planned last; plan `14C-08` adds the
  `"asr"` registry key and its typed refusal. This plan builds no speech
  backend, downloads no model, and constructs no request.
- **Media file inspection.** This adapter reads a transcript, not a video or an
  audio file. A `.mp4` handed to it is not a transcript and returns
  `no timestamped cue found`.
- **`webvtt-py`.** Refused on the cost test. The reconsideration condition is in
  `14C-RESEARCH.md`'s Alternatives table: adopt it if the hand-rolled parser
  proves fragile on real transcript files. Record any such fragility in the
  summary rather than silently adding the dependency.
- **Speaker labels and diarization.** A cue's text is its text. Splitting
  `Speaker 1:` prefixes into structured fields is a richer transcript model with
  no consumer yet.
- **Cue settings, styling, and regions as content.** They are presentation. They
  are recorded as skipped in the sidecar `unsupported` list and dropped.
- **Any change to `runtime.py`, `model.py`, `auditor.py`, `journal.py`, or
  `surfaces/`.**
</out_of_scope>

<verification>
1. `python3 tests/source_adapters_roundtrip.py` (exit 0)
2. `python3 schema_validate.py --all` (exit 0)
3. `for t in tests/*.py; do python3 "$t" || exit 1; done` (exit 0)
4. `python3 itembank.py guard .` (exit 0)
5. `git diff --stat runtime.py model.py auditor.py journal.py` (no output)
</verification>

<success_criteria>
- All eight transcript gold cases resolve as recorded.
- The hour field is optional and the fractional separator may be a comma or a
  period, proven by the two cases built for exactly those two failures.
- Every cue carries integer `start_ms` and `end_ms` with `end_ms` never less
  than `start_ms`.
- The whole path works with zero third-party packages installed.
- Zero em dash characters in any file this plan created or changed.
</success_criteria>

<summary_obligations>
`.planning/phases/14C-source-adapter-registry/14C-05-SUMMARY.md` records:

- Any real caption-file shape the hand-rolled parser could not read, which is
  the recorded trigger for reconsidering `webvtt-py`. Name the shape; do not add
  the dependency in this phase.
- Whether format detection from content alone was sufficient, or whether any
  fixture needed the filename extension as a tiebreaker.
- The measured wall-clock time of `check_transcript_gold_cases`, so the regex
  backtracking bound has a recorded baseline.
- Which truth was verified by which command and which `check_*` function.
</summary_obligations>

<output>
Create `.planning/phases/14C-source-adapter-registry/14C-05-SUMMARY.md` when done.
</output>
