# PDF and DOCX intake research (IL-20260815-07)

Date: 2026-08-17. One bounded research pass; judged on merit per the 2026-08-09
constraint relaxation. Deciding criterion per the 2026-08-10 audit F4: locator
fidelity for citations (can an extracted passage be traced to a page,
paragraph, or table cell so an objective can cite its source).

## Question

Which library or approach should itembank adopt for PDF and DOCX text
extraction, given that the importer must emit Markdown plus a locator sidecar
(never a second document model), the supply-chain policy prefers pinned,
near-zero-transitive, license-clean dependencies with a stated removal path,
and the acceptance gate is the Phase 11 fixture set in
`fixtures/audit/locator_fidelity_cases.py` (page, paragraph, column, table
cell, header, footer, footnote, tracked change, comment locators plus explicit
unsupported results for scanned, encrypted, malformed inputs).

## Method

Web searches run 2026-08-17 (all claims dated to sources read that day):
release status and locator APIs for pypdf, pdfminer.six, PyMuPDF, pdfplumber,
docling, markitdown, python-docx, mammoth; PyMuPDF licensing; docling install
weight; markitdown dependency stack and page-number limits; pypdf
visitor-function coordinates. Local reading: the locator fidelity gold cases
(path above), which define what "fidelity" must mean here.

## Candidates table

| Library | License | Pure Python | Runtime deps | Latest release (as of 2026-08-17) | Locators | First-cut verdict |
|---|---|---|---|---|---|---|
| pypdf | BSD-3 | yes | zero required | 6.16.1, 2026-08-14, weekly cadence | page number; x/y via visitor_text matrices, no word bboxes or tables | keep (fallback) |
| pdfminer.six | MIT | yes | charset-normalizer, cryptography (encrypted PDFs only) | 20260107, annual-ish cadence, healthy | per-char bbox, LTPage/LTTextLine layout tree | keep (as pdfplumber's engine) |
| pdfplumber | MIT | yes | pdfminer.six, Pillow + pypdfium2 only for visual debug (optional) | active; tracks pdfminer.six 20260107; adds page.search() with bboxes | page, word and char bboxes, lines/rects, table extraction with cell geometry | keep (primary PDF) |
| PyMuPDF (fitz) | AGPL-3.0 or paid Artifex commercial | no (MuPDF C, ~50MB wheels) | none beyond bundled MuPDF | 1.27.x, 2026-08-06, very active | best in class: words/blocks/spans with bboxes, fast | keep only if AGPL is explicitly accepted |
| docling (IBM) | MIT | no (torch, layout models) | heavy: torch, TableFormer, OCR extras; docling-slim core ~50MB but models still needed for PDF | active, Granite-Docling 258M model era | excellent: every element carries page + bbox provenance | cut: dependency weight and model downloads violate near-zero-deps preference |
| markitdown (Microsoft) | MIT | mostly | mammoth, pdfminer.six, pdfplumber, python-pptx, pandas, BeautifulSoup, more | active 2026 | none exposed: emits flat Markdown, page numbers not surfaced; strips headings from PDFs | cut: no locator output, wide dependency fan-out |
| python-docx | MIT | no (lxml is compiled) | lxml, typing_extensions | 1.2.0, slow but stable cadence | body order gives paragraph/table indices; styles give heading levels; no pages (DOCX has none pre-render) | keep (primary DOCX) |
| mammoth | BSD-2 | yes | cobble (tiny) | 1.12.0, 2026-03-13 | none: HTML output, structure preserved but no source locators; text boxes flattened | cut for import; note as a rendering reference |

## Locator-fidelity findings

- PDF pages are real objects, so page locators are cheap everywhere. The gate
  cases need more: paragraph index within page, column assignment, table cell
  row/col, header/footer separation, footnote separation. Those require
  character or word geometry, which is exactly what pdfminer.six exposes (per
  character bboxes in a layout tree) and pdfplumber makes usable (words with
  bboxes, `extract_tables()` with cell geometry, `page.search()` returning
  match bboxes, added in a 2026 release). Header/footer and footnote splitting
  is y-band classification over those bboxes, our code, not the library's.
- pypdf gives page number plus raw transformation matrices through
  `visitor_text`; reconstructing word bboxes and tables from that is
  re-implementing pdfminer. Fine as a light fallback and for PDF surgery
  (split, decrypt-check, metadata), not as the locator engine.
- PyMuPDF's `get_text("words")` returns (x0, y0, x1, y1, word, block, line,
  word_no) directly and is the fastest and most robust extractor surveyed, but
  it is AGPL-3.0 dual-licensed with a paid Artifex commercial option. The
  supply-chain policy makes GPL/AGPL an explicit user decision, so it cannot
  be the default recommendation.
- docling attaches page + bbox provenance to every element natively, the best
  locator story of the set, but drags torch and layout/table models (hundreds
  of MB to GB). Its own tracker (issue 2393) confirms the weight is a known
  complaint with only partial slimming. Wrong cost profile for a local-first
  tool with a removal-path requirement.
- markitdown emits Markdown with no locator sidecar and its maintainers state
  page numbers are not accessible through it; it also strips PDF headings. It
  answers a different question (LLM-ready flat text), not citation fidelity.
- DOCX has no pages at all before rendering (paginate-at-render is a format
  fact, confirmed in markitdown discussion 1258). The honest DOCX locator is
  body-order index: paragraph n, table t cell (r, c), heading by style, plus
  footnote/comment/tracked-change ids from their XML parts. python-docx walks
  exactly that structure. The gold cases already encode this shape (p.0,
  t.r0c0, fn.1, ins.1), so the fixture gate and python-docx agree. Note:
  python-docx does not read headers/footers/footnotes parts fully; those four
  cases (docx-footnote-endnote, docx-header-footer, docx-tracked-changes,
  docx-comments) need direct XML reads of the extra parts, which stdlib
  zipfile + xml.etree handle, as the fixture builders themselves demonstrate.
- Scanned or image-only PDFs: none of the text extractors produce anything,
  and the pdf-scanned-image-only gold case expects an explicit
  unsupported/lossy result, not OCR. That is the correct behavior to ship.

## Recommendation

Primary, PDF: **pdfplumber, pinned, with pdfminer.six pinned as its engine.**
Exact costs: two pure-Python packages (pdfplumber wheel under 100KB,
pdfminer.six a few MB); transitive runtime deps are charset-normalizer plus
cryptography (only exercised for encrypted PDFs, which we reject as
unsupported anyway, so it can be treated as inert or excluded if we vendor
selectively); MIT/MIT licenses, no review escalation; Windows-clean pure
wheels; record SHA-256 of both pinned wheels. It provides page numbers, word
and char bboxes, and table cell geometry, which covers every PDF gold case
except scanned/encrypted/truncated, where the required answer is an explicit
unsupported result.

Primary, DOCX: **python-docx, pinned**, for body order, styles, and tables,
plus direct stdlib XML reads (zipfile + xml.etree) for footnotes, endnotes,
headers, footers, comments, and tracked-change parts. Exact costs: MIT
license; deps lxml (compiled, but ships mature Windows wheels) and
typing_extensions; record SHA-256s. If the lxml compiled dep is judged too
heavy at pinning time, the demonstrated stdlib path (the fixture assembler
already round-trips these parts) covers the gate cases without python-docx at
all; that is also the removal path.

Fallback, PDF: **pypdf** (BSD-3, zero deps, pure Python, weekly releases) for
page-level extraction and PDF hygiene when geometry is not needed. It cannot
meet the column/table/footnote locator cases alone.

Explicitly not now: **PyMuPDF** (adopt only if Weibao makes the AGPL decision
on the record; it would then be the single strongest replacement for the whole
PDF stack), **docling** (locator quality is real but the torch-scale cost is
not justified for one learner's importer), **markitdown** and **mammoth** (no
locators, wrong output contract).

OCR: defer explicitly. Scanned pages return the unsupported/lossy result the
gold manifest already requires; when OCR is wanted, route through the existing
workspace `ocr` skill (local Ollama vision) as a separate, learner-invoked
step, and do not adopt an OCR library dependency.

Removal path (binding): the importer writes Markdown plus a JSON locator
sidecar at import time; both are plain UTF-8 on disk, so uninstalling every
library above leaves all previously imported learner data fully readable. Only
the ability to import new PDF/DOCX files degrades, with a clear error naming
the missing dependency.

## What this does not decide

- The locator sidecar schema itself (field names, span encoding, versioning);
  the gold manifests are the constraint but the schema is a design task.
- Whether pdfplumber and python-docx are vendored or pip-pinned, and the
  concrete SHA-256 pinning mechanism (no lockfile tooling exists here yet).
- Column-detection and header/footer y-band heuristics: library output makes
  them possible, tuning them against real course PDFs is implementation work.
- The AGPL question for PyMuPDF: parked, not rejected; revisit if pdfplumber
  fidelity or speed fails on real textbooks.
- Anything about PPTX, EPUB, HTML, or image intake (media-intake stub owns
  images), and nothing about OCR quality via the ocr skill.
