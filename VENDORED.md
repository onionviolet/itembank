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

Release URLs are the PyPI project pages of the same names
(`https://pypi.org/project/<name>/<version>/`); the release artifact column
names the exact wheel each hash was computed over. All six wheels are
`py3-none-any`, so the hashes are not platform specific.

The pin lines these six rows correspond to live in `deps/source-adapter-pins.txt`,
which also carries the CVE disposition, the transitive-dependency note, and the
four packages refused by name (PyMuPDF and `ebooklib` parked on AGPL,
`trafilatura` refused on dependency weight, `webvtt-py` refused on cost). The
adoption decision is `D-14C-3` in
`.planning/phases/14C-source-adapter-registry/14C-DECISIONS.md`.

## Backfill owed

Two artifacts were vendored before `SUPPLY-CHAIN-POLICY.md` existed and have no
row above yet. Policy section 2.2 makes them this file's debt, and plan `14C-08`
owns paying it:

| Artifact | Vendored by | What is owed |
|---|---|---|
| KaTeX | phase 09, plan `09-03` | a row with pin, upstream URL, release URL, SHA-256, license, reviewer, and review date |
| CodeMirror | the code-editor item type, phase 05 | the same row |

Also owed by plan `14C-08`, per policy section 2.3: a CI step that recomputes
every SHA-256 in this file and fails the build on a mismatch. Until that step
exists, the hashes above are recorded but not enforced, and this sentence is the
record that they are not.
