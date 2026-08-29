# Plan 14C-07 summary

Executed 2026-08-28 on Darwin arm64, Python 3.14.6. All three tasks ran.

## Task 1: the checkpoint was already answered

**Recorded answer: option-a**, decided by Weibao on 2026-08-27 and written up
in full as `D-14C-2` in `14C-DECISIONS.md`. The stdlib `zipfile` plus
`xml.etree` path is the accepted way to import EPUB, and `ebooklib` 0.20 is
**parked, not rejected**, pending an explicit AGPL decision, exactly as PyMuPDF
is parked for the PDF path. No stand-in was made and the wave did not stop.

**The verbatim answer to the Task 1 checkpoint**, quoted from `D-14C-2`:
option-a, with the rider **"consider how good it even looks and more"**. That
section carries his answer, the rider, the agent's separately-labelled reading
of it, and the reconsideration condition the rider widened; this summary does
not restate it.

**One thing the checkpoint owed was missing and is now written.** `D-14C-2`
existed in the phase decisions file, but step 3's second durable record, the
append to `.planning/IDEA-LEDGER.md`, had never been made. `IL-20260828-05` is
appended now, carrying the proposal, the origin, the conflicting rule quoted
from `SUPPLY-CHAIN-POLICY.md` section 2.4, the evidence, the retained
alternative, the disposition `Parked`, the decision pointer, and all three
revisit triggers including the one the rider added. `git diff` on the ledger
shows 38 insertions and zero deletions, so the append-only rule holds.

## What landed

- `fixtures/audit/epub_fidelity_cases.py`: seven hand-assembled EPUB fixtures
  with `container_xml`, `opf_xml`, `xhtml`, `chapter_xhtml`, and `epub_bytes`
  builders and a `materialize`.
- `_extract_epub`, `_epub_container_root`, `_epub_spine_order`, `_epub_blocks`,
  and `_local_tag` in `source_adapters.py`, with the `EPUB_CONTAINER_PATH`,
  `EPUB_ENCRYPTION_PATH`, `EPUB_BLOCK_TAGS`, `EPUB_HEADING_TAGS`, and
  `EPUB_SKIPPED_TAGS` constants. `epub` is registered at `1.0.0`.
- Seven checks in `tests/source_adapters_roundtrip.py`, plus the epub case
  added to `check_degrades_without_dependencies`.

## Gold reading orders the adapter could not reproduce

**None.** All seven cases resolve exactly as recorded, including the three
typed refusals, and they did so on the first run of the adapter against them.

## Which truth was verified by which command and which check

| Truth | Command | `check_*` |
|---|---|---|
| Seven deterministic cases, a correct uncompressed `mimetype` member first, no ebooklib in the builder | `python3 tests/source_adapters_roundtrip.py` | `check_epub_fixture_determinism` |
| All seven resolve as recorded | same | `check_epub_gold_cases` |
| Reading order comes from the spine, asserted on the emitted **text** and not only on the ids | same | `check_epub_spine_order` |
| The OPF path comes from the container's `rootfile`, not a hard-coded constant | same | `check_epub_container_indirection` |
| A citation resolves back to the exact spine item, element index, and fragment, with high envelope confidence and one derived line per locator | same | `check_epub_fragment_anchor` |
| A DRM-locked book is refused **before any content document is read**, proven with a deliberately broken content document that still refuses with `source.encrypted` | same | `check_epub_drm_refused` |
| Every archive member and every XML part goes through the one hardened reader, with no direct ZipFile read | same | `check_epub_uses_shared_seam` |
| EPUB still imports with every third-party package unimportable | same | `check_degrades_without_dependencies` |
| Unknown rights still refuse | same | `check_rights_refusal` |
| `epub` is registered and both container constants are right | `python3 -c "import source_adapters as s; ..."` | prints `epub registered` |
| The shared seam is used | `python3 -c "import inspect ..."` | prints `shared seam used` |
| The three refusal and loss strings are in source | `grep -c` for each | 1, 1, 1 |
| `ebooklib` appears only on a comment recording D-14C-2, never on an import | `grep -n -i "ebooklib" source_adapters.py` | one hit, line 1756, a comment |
| The ledger append is additive | `git diff --stat .planning/IDEA-LEDGER.md` | 38 insertions, 0 deletions |
| Every schema document still self-checks | `python3 schema_validate.py --all` | exit 0 |
| No repository-authored em dash | `python3 itembank.py guard .` | exit 0 |
| `runtime.py`, `model.py`, `auditor.py`, `journal.py` untouched | `git diff --stat` on the four | empty |
| The whole suite | `for t in tests/*.py; do python3 "$t" || exit 1; done` | 88 of 88 pass |

## Deviations from the plan, each with its reason

1. **`D-14C-2`'s heading is not the literal the plan's acceptance criterion
   names.** The criterion asks for `## D-14C-2. ebooklib is parked on an AGPL
   decision`; the recorded heading, written by the session that actually got
   Weibao's answer, is `## D-14C-2. The EPUB path is stdlib, and ebooklib is
   parked on AGPL`. The recorded heading says more, and renaming a heading
   inside an accepted decision record to satisfy a grep would be editing the
   record to fit the test. Left as recorded and flagged here.

2. **Two helpers the artifact list does not name: `_epub_blocks` and
   `_local_tag`.** `ElementTree` reports namespaced tags as `{uri}local`, and
   every element in an EPUB is namespaced, so a bare `element.tag == "p"`
   comparison matches nothing at all. `_local_tag` is that one line, used
   everywhere. `_epub_blocks` carries the block walk, the nested-block skip,
   and the outward fragment search, which would otherwise be three loops inline
   in `_extract_epub`.

3. **A block nested inside another block is emitted once, by its innermost
   owner.** The plan does not say what to do about a `p` inside a `li`. The web
   adapter already made this choice in plan `14C-04`, and matching it keeps one
   rule across both HTML-shaped adapters rather than two.

4. **`spine_index` is the position in the resolved spine, not the manifest.**
   Stated because it is what makes `epub-spine-out-of-order`'s ids read
   `sp0.*` for `chap3.xhtml`: the ids number the reading order, and the
   `spine_idref` beside them names which document that position actually is.
   `check_epub_spine_order` asserts both, and asserts on the text as well,
   because right-looking ids from the wrong documents would pass an id-only
   assertion.

5. **A content document that will not read or will not parse is a per-spine-item
   entry in the loss report, not a whole-file refusal.** The plan does not say.
   Refusing a whole book because one chapter is corrupt would lose the other
   chapters for no gain; the sidecar names the spine item that failed. A book
   where *every* document fails still refuses, with `no readable content
   document in the spine`.

6. **`REQUIREMENTS.md` is untouched, as the plan requires.** PORT-02 already
   describes EPUB as an interchange prototype carrying an explicit semantic
   loss report, and this adapter's `unsupported` list is that report for the
   import direction: it always names the unread navigation document, and adds
   one entry per distinct skipped tag that carried text.

## What this plan did not do

It did not open plan `14C-08`. It adopted no dependency, edited no pin file,
and left `runtime.py`, `model.py`, `auditor.py`, `journal.py`, and every file
under `surfaces/` untouched. It did not read the navigation document and
produces no hierarchical table of contents; that loss is named in every EPUB
sidecar rather than left silent. `asr` remains plan `14C-08`.
