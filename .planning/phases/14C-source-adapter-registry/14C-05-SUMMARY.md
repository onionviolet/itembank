# Plan 14C-05 summary

Executed 2026-08-28 on Darwin arm64, Python 3.14.6. Both tasks ran. The plan
is `autonomous: true` and carries no blocking human checkpoint.

## What landed

- `fixtures/audit/transcript_fidelity_cases.py`: eight deterministic fixtures
  across SRT, WebVTT, and plain bracketed timestamps, with `srt_bytes`,
  `vtt_bytes`, and `plain_bytes` builders and a `materialize`.
- In `source_adapters.py`: `TIMESTAMP_RE`, `CUE_ARROW`, `VTT_SKIP_BLOCKS`,
  `_timestamp_to_ms`, `_ms_to_stamp`, `_cue_from_block`, `_blocks`,
  `_parse_srt`, `_parse_vtt`, `_parse_plain_timestamps`, and
  `_extract_transcript`. `transcript` is registered at `1.0.0`, with no
  lazy-import guard and no `source.dependency_missing` path, and a comment
  saying not to add one for symmetry.
- Six checks in `tests/source_adapters_roundtrip.py`.

## Real caption shapes the hand-rolled parser could not read

**None found.** All eight gold cases parse, including the four that exist
because real files differ from tidy ones: a UTF-8 BOM with CRLF endings, a
WebVTT with no hour field, a WebVTT carrying `NOTE`, `STYLE`, and `REGION`
blocks plus trailing cue settings, and a cue whose end precedes its start.

The recorded trigger for reconsidering `webvtt-py` is therefore **not** fired,
and the dependency stays refused on the cost test in
`SUPPLY-CHAIN-POLICY.md` section 3. The honest limit on that claim: these are
fixtures written from the specifications, not files exported by a real
captioning tool. The first real `.vtt` or `.srt` from a lecture that this
parser mishandles is the thing to record here, and it has not happened yet
because no real file has been run through it.

Two tolerances were built beyond what the fixtures strictly required, both
because leaving them out would fail on ordinary files: `_parse_srt` accepts a
block with **no** leading numeric index line as readily as one with it, and
`_parse_vtt` accepts a cue identifier line before the timing line. Neither has
a gold case; both are one-line branches whose absence would reject common
exports.

## Format detection from content alone

**Sufficient. No fixture needed the filename extension as a tiebreaker**, and
`check_transcript_separator_tolerance` proves the stronger claim by feeding
the SRT fixture through as if it were a `.vtt` and the WebVTT fixture as if it
were an `.srt`; both produce the recorded three-cue order. The detection order
is: a first non-blank line beginning `WEBVTT` selects the VTT parser,
otherwise a body containing `-->` selects the SRT parser, otherwise a line
beginning with a bracketed timestamp selects the plain parser, otherwise the
refusal `no timestamped cue found`.

One regex serves all three, with an optional hour group and a comma-or-period
fractional separator, which is what makes a renamed file a non-event.

## Measured wall-clock time of `check_transcript_gold_cases`

**0.001 s** for all eight fixtures, printed by the check itself on every run so
the number is never stale. The check fails above 5.0 s, which is the recorded
baseline for T-14C-31: a future edit that introduces a nested quantifier into
`TIMESTAMP_RE` fails that bound rather than hanging the suite.

## Which truth was verified by which command and which check

| Truth | Command | `check_*` |
|---|---|---|
| Eight deterministic cases, every recorded sha256 stable, no caption library in the builder, materialize contained | `python3 tests/source_adapters_roundtrip.py` | `check_transcript_fixture_determinism` |
| All eight resolve as recorded, inside a 5 s backtracking bound | same | `check_transcript_gold_cases` |
| Integer milliseconds, monotonic cue indexes, no negative duration, the hour field genuinely optional | same | `check_transcript_timestamp_locators` |
| One grammar reads both separators and both extensions, detected from content | same | `check_transcript_separator_tolerance` |
| A transcript imports end to end with all six pinned packages unimportable | same | `check_transcript_no_dependency` |
| One derived line per cue, the moment readable without the sidecar, inferred ends recorded as medium confidence | same | `check_transcript_end_to_end` |
| Unknown rights still refuse | same | `check_rights_refusal` |
| No second parser | same | `check_no_second_parser` |
| `transcript` is registered at 1.0.0 | `python3 -c "import source_adapters as s; ..."` | prints `transcript registered` |
| The timestamp grammar, including the padded fraction | `python3 -c "... _timestamp_to_ms ..."` | prints `timestamps ok` |
| The skip-block vocabulary | `python3 -c "... VTT_SKIP_BLOCKS ..."` | prints `vtt blocks ok` |
| The two refusal strings are in source | `grep -c` for each | 1, 2 |
| Every schema document still self-checks | `python3 schema_validate.py --all` | exit 0 |
| No repository-authored em dash | `python3 itembank.py guard .` | exit 0 |
| `runtime.py`, `model.py`, `auditor.py`, `journal.py` untouched | `git diff --stat` on the four | empty |
| The whole suite | `for t in tests/*.py; do python3 "$t" || exit 1; done` | 88 of 88 pass |

## Deviations from the plan, each with its reason

1. **`_ms_to_stamp`, `_cue_from_block`, and `_blocks` are three helpers the
   plan's artifact list does not name.** They are the shared body of the three
   parsers. Writing the block splitter and the timing-line reader once rather
   than three times is what makes "one grammar for three shapes" true in the
   code rather than only in the prose.

2. **The plain shape's `end_ms` is filled in a second pass.** The plan has each
   cue's end come from the next cue's start; the parser therefore builds every
   cue with `end_ms == start_ms` and then walks the list once to fill in the
   ends, leaving the final cue's end equal to its own start. Same result, and
   it keeps the single-pass reader from needing lookahead.

3. **The `vtt-with-settings-and-notes` fixture passes its whole timing line
   through the builder.** `vtt_bytes` treats an `end` of `None` as "start
   already holds the complete timing line", which is how that case carries its
   trailing `align:start position:10%` without a second builder. Documented at
   the branch.

4. **`check_transcript_no_dependency` blocks `lxml` too.** The plan names five
   libraries; `readability` and `python-pptx` both pull `lxml`, and blocking
   the wrappers while leaving the shared parser importable would understate
   the claim. All six top-level names are blocked.

5. **The applied-entry assertions count `import` entries, not all applied
   entries.** Linking the raw file is itself a journalled operation, so a bare
   count is 2. Caught by the assertion going red on the first run, which is
   the assertion working.

## What this plan did not do

It did not open plan `14C-06`. It built no ASR backend, downloaded no model,
and constructed no request; roster item 5 remains registered and unbuilt until
plan `14C-08` adds its key and typed refusal. It adopted `webvtt-py` no more
than the previous plans adopted PyMuPDF or ebooklib, edited no pin file, and
left `runtime.py`, `model.py`, `auditor.py`, `journal.py`, and every file
under `surfaces/` untouched. It parsed no speaker labels and read no media
file. `ocr`, `epub`, and `asr` remain plans 06 through 08.
