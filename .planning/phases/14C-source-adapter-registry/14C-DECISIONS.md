# Phase 14C decisions

Decisions this phase made and locked, each recorded where a later plan can find
it without reading chat history, per `AGENT-WORKFLOW.md`.

Created 2026-08-27 by the session that put the checkpoints to Weibao, ahead of
plan 14C-01 running. Plan 14C-01 Task 1 appends to this file rather than
creating it.

## D-14C-1. The locator sidecar contract is frozen, and the adapter path is promoted

**Date:** 2026-08-27. **Decided by Weibao.** Rated one-way by plan 14C-01: a
sidecar field name becomes a published contract the moment a citation names a
span in it, and renaming later means migrating every sidecar and every citation
already written.

**Question.** Two things frozen in one answer, because they are the same
decision seen from two sides: the exact field names of
`schemas/source_locator.schema.json`, and whether a source carrying an adapter
and a locator sidecar becomes the primary source representation or is added
alongside the existing Markdown-only path.

**Recorded answer: option-a, freeze the tabled contract and promote.**

The frozen root fields are `schema_version` (integer const 1), `source_id`,
`adapter`, `adapter_version`, `fingerprint`, `captured_at`, `origin`, `rights`,
`confidence`, `reading_order`, `locators`, `unsupported`, with
`additionalProperties: false` at every object level. `$defs.origin` requires
`kind`, `value`, `fetched_at`, `http_etag`, `http_last_modified`,
`snapshot_rel_path`. `$defs.locator` requires `id`, `span_id`, `kind`, `body`.
`$defs.rights` requires exactly `read`, `quote`, `transform`, `remote_process`,
`package`, `export`, `share`. Per-medium bodies are `body_markdown`, `body_pdf`,
`body_docx`, `body_pptx`, `body_epub`, `body_web`, `body_transcript`,
`body_ocr`.

**What promote means in practice.** `markdown` and `text` register as identity
adapters from the first commit, so a hand-written Markdown file and a PDF reach
disk through the same function and no Markdown-only side door survives. Every
locator `id` shape and `kind` string is lifted verbatim from gold cases already
committed in `fixtures/audit/locator_fidelity_cases.py`, so the acceptance
corpus and the schema cannot disagree. `span_id` joins the sidecar to the one
parser's own span ids, so a citation record needs no new shape.

**Accepted costs, named rather than glossed.** Registering `markdown` and `text`
is a few lines the `14C-CONTEXT.md` roster did not ask for. Typing `bbox` and
`confidence` as strictly `null` in `body_ocr` means a future structured-OCR mode
needs a schema version bump rather than a field loosening.

**What was rejected.** Option-b (freeze but add alongside) would have left two
ways for a source to reach disk, so a later phase writing a Markdown source
without a sidecar would produce a source no citation can locate, with nothing
going red. It also contradicted this plan's own frontmatter, which already
carries `assumption_delta_decision: decision: promote`. Option-c (defer the
freeze) would have stopped the wave and forced replanning of 14C-02 through
14C-08, since every one of them names `schemas/source_locator.schema.json` in
its verification.

**Executor consequence.** Plan 14C-01 proceeds to Task 2 unchanged. Task 3
builds exactly the tabled contract and registers `markdown`, `text`, and `pdf`.

## D-14C-3. The six source-adapter packages are approved for adoption

**Date:** 2026-08-27. **Approved by Weibao**, answering plan 14C-01 Task 2, the
batched package-legitimacy sign-off, and the `SUPPLY-CHAIN-POLICY.md` section 3
adoption gate.

| Package | Pin | License |
|---|---|---|
| `pdfplumber` | 0.11.10 | MIT |
| `pdfminer.six` | 20260107 | MIT |
| `python-docx` | 1.2.0 | MIT |
| `pypdf` | 6.16.1 | BSD-3-Clause |
| `python-pptx` | 1.0.2 | MIT |
| `readability-lxml` | 0.8.4.1 | Apache-2.0 |

All six were flagged `SUS` by the legitimacy checker for the single reason
`unknown-downloads`; `pypdf` additionally for `too-new`, which reflects only its
most recent point-release date. All six licenses are acceptable by default under
policy section 2.4.

**Refused, and named so the refusal is visible rather than silent.** `ebooklib`
0.20 is AGPL and is parked pending D-14C-2 below. `trafilatura` 2.2.0 is
Apache-2.0 and legitimate but pulls six hard runtime dependencies against
`readability-lxml`'s two to three; it is not adopted on dependency weight, not
on legitimacy. `webvtt-py` was considered for transcripts and refused as not
earning its cost; transcript intake uses a hand-rolled stdlib SRT and VTT
parser.

**This approval creates `VENDORED.md`**, which does not exist at the repository
root today. Plan 14C-01 Task 2 step 4 creates it with columns artifact, pin,
upstream project URL, release URL, SHA-256, license, reviewer, review date, the
six rows above, and a `## Backfill owed` section naming KaTeX and CodeMirror as
pre-policy vendored artifacts whose rows and CI checksum step are owed by plan
14C-08.

**Two things the executor must not treat as settled by this approval.**

1. **The eye check on the six PyPI pages.** Plan 14C-01 Task 2 is gated
   `checkpoint:human-verify`, `gate="blocking-human"`, with the resume signal
   'Type "approved" once the six PyPI pages check out'. Weibao approved the
   adoption on the basis of the summary presented to him. Whether he opened the
   six pages was not established, and this record does not assert that he did.
   The executor confirms this before the pins land.
2. **Vendored versus pinned install.** Policy section 2.1 says vendored by
   default, copied into the repository at a pinned version. Plan 14C-01 Task 2
   implements adoption as a one-time pinned `pip install` plus
   `deps/source-adapter-pins.txt`, leaning on the section 2.5 build-tool
   carve-out with `deps/lti-pins.txt` as precedent. That is arguably a fifth
   thing being approved here and it was not put to Weibao separately. Recorded
   so it is a visible known state rather than a silent one.

## D-14C-2. The EPUB path is stdlib, and ebooklib is parked on AGPL

**Date:** 2026-08-27. **Decided by Weibao**, on the second asking. Rated
one-way, because adopting an AGPL dependency is a product-wide licensing
commitment that cannot be quietly undone once code depends on it; parking is the
reversible branch, which is why parking was the recommended default.

**Recorded answer: option-a.** The stdlib `zipfile` plus `xml.etree` path is the
accepted way to import EPUB. `ebooklib` 0.20 is **parked, not rejected**,
pending an explicit AGPL decision, exactly as PyMuPDF is parked for the PDF
path.

**The rider he attached, quoted:** "consider how good it even looks and more".

**Interpretation of the rider, the agent's and kept separate.** Read as an
instruction that shipping EPUB is not sufficient on its own: the stdlib
adapter's extraction fidelity and the resulting reading presentation are part
of whether this answer holds. Two consequences, both additive to plan 14C-07 and
neither changing its option-a path:

1. **Fidelity is evaluated, not assumed.** The EPUB gold cases in
   `fixtures/audit/epub_fidelity_cases.py` are judged on what a learner actually
   reads, not only on whether locators resolve. A spine-order read that loses
   headings, lists, tables, or figure captions is a failure of this rider even
   if every assertion passes.
2. **Presentation quality is a named reconsideration trigger.** See the
   condition below.

**Reconsideration condition, widened by the rider.** Revisit this parking if any
of the following becomes true. The first two are the plan's own; the third is
new and comes from the rider.

- A real EPUB proves unreadable by the stdlib path.
- The product's licensing posture changes, for example a decision that itembank
  ships as AGPL open source, at which point `ebooklib` costs nothing.
- **The stdlib path's extraction fidelity or reading presentation is visibly
  worse than what a library would give**, and the gap matters to a learner
  rather than only to a test.

**The reasoning recorded so it is not re-derived.**

- **For personal use alone, AGPL costs nothing.** Its obligations trigger on
  distribution and on network service use. A tool Weibao runs on his own machine
  and never hands to anyone triggers neither.
- **For the recorded product goal it is expensive and one-way.** `ROADMAP.md`
  Phase 18 is a packaged desktop app that a friend installs, and the 2026-08-14
  vision entry made external installations a supported goal. Distribution
  triggers the copyleft source-offer obligation over the whole product, not just
  the one adapter, and forecloses a closed-source or dual-licensed future.
- **The decisive technical point, which only became true once D-14C-1 was
  answered the same day.** `ebooklib`'s main advantage over the stdlib path is
  the navigation document's hierarchical table of contents. The `body_epub`
  field set frozen in D-14C-1 carries `spine_index`, `spine_idref`,
  `element_index`, and `fragment`, and **has no field for a TOC hierarchy**. So
  adopting `ebooklib` today would buy data the frozen contract cannot store
  without a schema version bump. The advantage is real and currently unusable.
  If the rider's quality review concludes the TOC hierarchy is what is missing,
  the honest response is a `body_epub` schema field first, and only then a
  library decision.
- **The asymmetry.** Parking is reversible and adoption is not, in practice.
- **Consistency.** PyMuPDF was parked on identical grounds for the PDF path
  (D-01, `14C-CONTEXT.md`, and `IDEA-LEDGER.md` IL-20260815-07, parked and not
  rejected). Parking `ebooklib` treats the same license the same way twice.

**Recording obligations this answer carries**, per plan 14C-07 Task 1 on
option-a. Both are owed and neither is done yet:

1. A dated `## D-14C-2. ebooklib is parked on an AGPL decision` section carrying
   all seven `PLANNING-DIRECTIVES.md` section 3a fields. This entry is its
   substance; the executor confirms the seven fields are present in the form
   that document requires.
2. One appended `IL-` entry in `.planning/IDEA-LEDGER.md` with disposition
   `Parked (needs an explicit Weibao AGPL decision)` and the widened
   reconsideration condition above.

**Executor consequence.** Plan 14C-07 proceeds to Task 2 unchanged, with the
fidelity rider applied to its gold-case review.

### Superseded framing, preserved for trace

This decision was first recorded on 2026-08-27 as STILL OPEN, because Weibao
answered the first asking with a question ("idk whats the best method, for
personal use and potential product wise for future and more?") rather than a
selection. The analysis above was given in reply and the checkpoint was
re-asked rather than answered on his behalf. The costs of each option, as the
plan states them, are unchanged:

**Date raised:** 2026-08-27. Rated one-way, because adopting an AGPL dependency
is a product-wide licensing commitment that cannot be quietly undone once code
depends on it; parking is the reversible branch.

**Question.** Is the stdlib `zipfile` plus `xml.etree` path the accepted way to
import EPUB, with `ebooklib` parked alongside PyMuPDF pending an explicit AGPL
decision?

**What happened.** Put to Weibao on 2026-08-27. He did not select an option and
asked instead what the best method is for personal use and for a potential
future product. The analysis given in reply is summarised below; the checkpoint
was re-asked rather than answered on his behalf.

**The analysis presented, recorded so it is not re-derived.**

- **For personal use alone, AGPL costs nothing.** Its obligations trigger on
  distribution and on network service use. A tool Weibao runs on his own machine
  and never hands to anyone triggers neither.
- **For the recorded product goal it is expensive and one-way.** `ROADMAP.md`
  Phase 18 is a packaged desktop app that a friend installs, and the 2026-08-14
  vision entry made external installations a supported goal. Distribution
  triggers the copyleft source-offer obligation, and taking AGPL for one adapter
  is a licensing commitment over the whole product.
- **The decisive technical point, which follows from D-14C-1 above.**
  `ebooklib`'s main advantage over the stdlib path is the navigation document's
  hierarchical table of contents. The `body_epub` field set just frozen carries
  `spine_index`, `spine_idref`, `element_index`, and `fragment`, and **has no
  field for a TOC hierarchy**. So adopting `ebooklib` today would buy data the
  contract cannot store without a schema version bump. The advantage is real but
  unusable in this phase.
- **The asymmetry.** Parking is reversible and adoption is not, in practice.
  `ebooklib` can be adopted later if a real EPUB proves unreadable by the stdlib
  path. Code that already depends on it is not easily unwound.
- **Consistency.** PyMuPDF was parked on identical grounds for the PDF path
  (D-01, `14C-CONTEXT.md`, and `IDEA-LEDGER.md` IL-20260815-07, parked and not
  rejected). Parking `ebooklib` treats the same license the same way.

**What each answer costs, unchanged from the plan.** The stdlib path costs about
a hundred lines of container and OPF parsing this project then maintains, and no
TOC hierarchy in this phase; it reuses the hardened seam plan 14C-02 already
built, so zip-bomb and entity-expansion guards cover EPUB for free. Adopting
`ebooklib` stops the plan: it needs a full section 3 adoption record, a
`VENDORED.md` row, and a legitimacy checkpoint, none of which is in this plan,
and it enlarges the six-package list approved in D-14C-3. Deferring EPUB leaves
`body_epub` frozen in the contract with no adapter producing it, which plan
14C-08 must then record in the phase freeze as a known untested contract.

**Effect on sequencing.** Plans 14C-01 through 14C-06 and 14C-08 do not depend
on this answer. Plan 14C-07 does and is stopped.
