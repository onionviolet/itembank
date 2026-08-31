# Vendored and pinned third-party artifacts

Created 2026-08-27 by plan `14C-01` Task 2, which is the first plan to adopt a
dependency after `.planning/SUPPLY-CHAIN-POLICY.md` was written. Section 2.2 of
that policy says this file is created by exactly that plan, and that the
pre-policy KaTeX and CodeMirror rows are backfilled by the same plan; the
backfill is scheduled in the final section below rather than guessed at here.

Every row records a pin, the upstream project, the release artifact, its
SHA-256, its license, who reviewed the license, and when. A pin is an exact
release, never a range. Nothing in this file loads from a CDN or fetches at run
time on a learner's machine: these are development and optional-adapter
artifacts, and the shipped product degrades rather than blocks when they are
absent.

## Rows

| Artifact | Pin | Upstream project | Release artifact | SHA-256 | License | Reviewer | Review date |
|---|---|---|---|---|---|---|---|
| `pdfplumber` | 0.11.10 | https://github.com/jsvine/pdfplumber | `pdfplumber-0.11.10-py3-none-any.whl` | `7741ea81bf165b474b153e6789d10d18e06b6ddcf3ec84289c3ef2fed6802580` | MIT | Weibao | 2026-08-27 |
| `pdfminer.six` | 20260107 | https://github.com/pdfminer/pdfminer.six | `pdfminer_six-20260107-py3-none-any.whl` | `366585ba97e80dffa8f00cebe303d2f381884d8637af4ce422f1df3ef38111a9` | MIT | Weibao | 2026-08-27 |
| `python-docx` | 1.2.0 | https://github.com/python-openxml/python-docx | `python_docx-1.2.0-py3-none-any.whl` | `3fd478f3250fbbbfd3b94fe1e985955737c145627498896a8a6bf81f4baf66c7` | MIT | Weibao | 2026-08-27 |
| `pypdf` | 6.16.1 | https://github.com/py-pdf/pypdf | `pypdf-6.16.1-py3-none-any.whl` | `63fec31c4092ae50b6729beedcb469055b60d20c834bde1c402df241f371f644` | BSD-3-Clause | Weibao | 2026-08-27 |
| `python-pptx` | 1.0.2 | https://github.com/scanny/python-pptx | `python_pptx-1.0.2-py3-none-any.whl` | `160838e0b8565a8b1f67947675886e9fea18aa5e795db7ae531606d68e785cba` | MIT | Weibao | 2026-08-27 |
| `readability-lxml` | 0.8.4.1 | https://github.com/buriy/python-readability | `readability_lxml-0.8.4.1-py3-none-any.whl` | `874c0cea22c3bf2b78c7f8df831bfaad3c0a89b7301d45a188db581652b4b465` | Apache-2.0 | Weibao | 2026-08-27 |
| `playwright` | 1.62.0 | https://github.com/microsoft/playwright-python | `playwright-1.62.0-py3-none-macosx_11_0_arm64.whl` | `db755ab27db21a04186f1fe8169888e42356086e439b1059b923ef417f0b6034` | Apache-2.0 | Weibao (D-17A-04-1) | 2026-08-27 |
| `vendor/katex/katex.min.js` | 0.18.4 | https://github.com/KaTeX/KaTeX | https://github.com/KaTeX/KaTeX/releases/tag/v0.18.4 | `2ec5916941ef4383e0314eaabcc712301b06001d9fb68e08d751d2bae5a27a1a` | MIT | Weibao | 2026-08-28 |
| `vendor/katex/katex.min.css` | 0.18.4 | https://github.com/KaTeX/KaTeX | https://github.com/KaTeX/KaTeX/releases/tag/v0.18.4 | `180c2d77d434d7da51d6625c50a964d4fd6fdbdb9bc8796a0a016c30c49931fb` | MIT | Weibao | 2026-08-28 |
| `assets/vendor/codemirror/codemirror.bundle.js` | state 6.7.1, view 6.43.8, commands 6.10.4 | https://github.com/codemirror/dev | npm packages, bundled locally; see `assets/vendor/codemirror/VENDOR.md` | `58de2c136ca4bbfd92a08e50d64884708109fd3d18843fc1c47dce6e657be588` | MIT | Weibao | 2026-08-28 |
| `fonts/source-serif` | 4.005R | https://github.com/adobe-fonts/source-serif | `source-serif-4.005_WOFF2.zip` | see `fonts/MANIFEST.json` | SIL OFL 1.1 | Weibao | 2026-08-10 |
| `fonts/ia-writer-quattro` | f32c04c (commit; upstream publishes no release tags) | https://github.com/iaolo/iA-Fonts | raw files at the pinned commit | see `fonts/MANIFEST.json` | SIL OFL 1.1 | Weibao | 2026-08-10 |

Release URLs are the PyPI project pages of the same names
(`https://pypi.org/project/<name>/<version>/`); the release artifact column
names the exact wheel each hash was computed over. All six wheels are
`py3-none-any`, so the hashes are not platform specific.

The `playwright` row is the 17A-04 dev-only browser QA harness (decision
`D-17A-04-1`, approved by Weibao 2026-08-27; the executor resolved the pin to
the latest stable release on 2026-08-31 as the decision instructed). Its pin
line lives in `deps/visual-qa-pins.txt`, which also records the LGPL ffmpeg
sub-decision (option A), the dev-only isolation story, and the note that the
wheel is platform-specific, so its hash is of the macOS arm64 wheel actually
installed. Nothing in the shipped runtime imports it; with it absent,
`tools/visual_qa.py` refuses with one line and the QA matrix falls back to
scripted human review.

The pin lines the six adapter rows correspond to live in `deps/source-adapter-pins.txt`,
which also carries the CVE disposition, the transitive-dependency note, and the
four packages refused by name (PyMuPDF and `ebooklib` parked on AGPL,
`trafilatura` refused on dependency weight, `webvtt-py` refused on cost). The
adoption decision is `D-14C-3` in
`.planning/phases/14C-source-adapter-registry/14C-DECISIONS.md`.

## What each row means, and what the checker does with it

The six package rows are **pins, not vendored files**: those wheels are
installed from PyPI and are not committed to this tree, so
`scripts/check_vendored.py` verifies each one against its pin line in
`deps/source-adapter-pins.txt` rather than against bytes on disk. The KaTeX
and CodeMirror rows name **files in this repository**, so the checker
recomputes their SHA-256 and fails on a mismatch or a missing file.

The two font rows carry `see fonts/MANIFEST.json` in the SHA-256 column,
because that manifest already records a SHA-256 for every font file and
`tests/presentation_roundtrip.py` already recomputes them. This table points
at that one record rather than creating a second one that would drift; the
checker follows the pointer and verifies every file the manifest names.

`assets/vendor/codemirror/check-editor-boot.js` is deliberately absent from
this table: it is repository-authored configuration that happens to live
beside the vendored bundle, not a third-party artifact. Its own SHA-256 is
recorded in `assets/vendor/codemirror/VENDOR.md` and asserted by
`tests/check_roundtrip.py`.

## Update cadence

Per `.planning/SUPPLY-CHAIN-POLICY.md` section 4, vendored artifacts are
reviewed at each phase that touches their surface and at minimum once per
milestone. Each review is recorded here as a dated note.

- **2026-08-28, plan `14C-08`.** The six adapter pins were reviewed at
  adoption in plan `14C-01` and are unchanged. KaTeX 0.18.4, the CodeMirror 6
  bundle, and the two font families were backfilled into the table above with
  their SHA-256 recomputed today, **without an upgrade**: this pass records
  what ships, it does not move any pin. The backfill section this file carried
  since 2026-08-27 is discharged, and the CI step it said was owed now exists
  (`scripts/check_vendored.py`, run by `.github/workflows/ci.yml`), so the
  sentence recording that the hashes were "recorded but not enforced" is no
  longer true and has been removed.

**One inconsistency found while writing this section, recorded rather than
quietly fixed.** `D-14C-3` records an agent choice under Weibao's delegation
to pin `pypdf` at **6.16.2** rather than the plan's 6.16.1, on the grounds
that 6.16.2 shipped four days before the approval. That choice was never
applied: `deps/source-adapter-pins.txt` line 69 and the row above both read
6.16.1, with 6.16.1's hash. Moving the pin means fetching 6.16.2's wheel and
recording its own hash, which is a supply-chain action and not a text edit, so
plan `14C-08` did not make it. `pypdf` is the recorded page-level fallback and
is wired into no code path yet, so nothing is running on either version today.
