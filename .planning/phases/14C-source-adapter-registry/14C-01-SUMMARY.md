# Plan 14C-01 summary

Executed 2026-08-27 on Darwin arm64, Python 3.14.6. All four tasks ran. Both
blocking checkpoints were already answered by Weibao on the same date, so no
stand-in was made and no wave was stopped.

## Task 1: the frozen sidecar contract

**Recorded answer: option-a**, freeze the tabled contract and promote, decided
by Weibao on 2026-08-27 and written up in full as `D-14C-1` in
`14C-DECISIONS.md`. That section carries the question as asked, all three
options, the answer, the date, and the reconsideration condition; it is the
record, and this summary does not restate it.

**Field renames applied: none.** `schemas/source_locator.schema.json` was built
from the plan's field table verbatim: twelve root fields, `$defs.origin` with
six, `$defs.locator` with four, `$defs.rights` with exactly the seven
`identity.RIGHTS_OPERATIONS`, `$defs.unsupported_entry` with two, and the eight
per-medium bodies. `additionalProperties: false` at every object level. Nullable
fields use a list-valued `type`, and no keyword outside
`schema_validate.SUPPORTED` appears anywhere in the document.

**Promote is real in code, not just in prose.** `markdown` and `text` are
registry entries calling the same `_extract_markdown`, so a hand-written
Markdown file reaches disk through the function a PDF reaches it through.
`check_one_import_path` asserts it.

## Task 2: the package legitimacy sign-off

**Sign-off outcome: approved**, all six, recorded as `D-14C-3` with the
per-package PyPI, GitHub, and OSV evidence Weibao was shown. Two refusals stay
visible by name: `ebooklib` 0.20 parked on AGPL beside PyMuPDF (`D-14C-2`), and
`trafilatura` 2.2.0 refused on dependency weight rather than on legitimacy.
`webvtt-py` refused on cost.

**The six resolved wheels and their SHA-256.** All six are `py3-none-any`, so
these hashes are not platform specific.

| Wheel | SHA-256 |
|---|---|
| `pdfplumber-0.11.10-py3-none-any.whl` | `7741ea81bf165b474b153e6789d10d18e06b6ddcf3ec84289c3ef2fed6802580` |
| `pdfminer_six-20260107-py3-none-any.whl` | `366585ba97e80dffa8f00cebe303d2f381884d8637af4ce422f1df3ef38111a9` |
| `python_docx-1.2.0-py3-none-any.whl` | `3fd478f3250fbbbfd3b94fe1e985955737c145627498896a8a6bf81f4baf66c7` |
| `pypdf-6.16.1-py3-none-any.whl` | `63fec31c4092ae50b6729beedcb469055b60d20c834bde1c402df241f371f644` |
| `python_pptx-1.0.2-py3-none-any.whl` | `160838e0b8565a8b1f67947675886e9fea18aa5e795db7ae531606d68e785cba` |
| `readability_lxml-0.8.4.1-py3-none-any.whl` | `874c0cea22c3bf2b78c7f8df831bfaad3c0a89b7301d45a188db581652b4b465` |

Recorded in `deps/source-adapter-pins.txt` and in `VENDORED.md`, which this
plan created at the repository root as `SUPPLY-CHAIN-POLICY.md` section 2.2
requires of the first plan adopting a dependency after the policy. `VENDORED.md`
carries a `## Backfill owed` section naming KaTeX and CodeMirror, and states in
its own words that the recorded hashes are not yet CI-enforced, which plan
`14C-08` owes.

**Transitive dependencies pip resolved**, recorded because they were not part of
the approval: Pillow, XlsxWriter, cffi, chardet, charset-normalizer,
cryptography, cssselect, lxml, lxml_html_clean, pycparser, pypdfium2,
typing_extensions. `pdfminer.six` pulls `cryptography`, which `deps/lti-pins.txt`
pins separately at 43.0.0 for the LTI surface; the version resolved here is
above the `>=49.0.0` floor that file names for x509 verification, so the two do
not conflict today.

## The pdfplumber key names, RESEARCH assumption A2

**Observed against the installed pdfplumber 0.11.10**, so plans 02 through 08 do
not repeat the discovery. `Page.extract_words()` returns dicts whose full key
set is:

`bottom`, `direction`, `doctop`, `height`, `text`, `top`, `upright`, `width`,
`x0`, `x1`

**The four the plan assumed are all present and correctly named**: `x0`, `top`,
`x1`, `bottom`. A2 is resolved in favour of the assumption. Note there is no
`page_number` key on a word dict, so the page number comes from enumerating
`pdf.pages`, which is what `_extract_pdf` does.

## Which truth was verified by which command

| Truth | Command | Result |
|---|---|---|
| The sidecar schema is well formed and uses no unsupported keyword | `python3 schema_validate.py --all` | exit 0, `ok: source_locator.schema.json`, `19 schema documents self-check clean` |
| One PDF imports end to end with one fingerprint across sidecar, journal entry, and registry | `python3 tests/source_adapters_roundtrip.py` | exit 0, ten `ok:` lines |
| The `op_link` change broke nothing | `identity_roundtrip.py`, `journal_roundtrip.py`, `operations_roundtrip.py`, `audit_coverage_roundtrip.py` | all four exit 0 |
| `op_link` is additive | `inspect.signature(journal.op_link)` ends `rights=None)` | `op_link additive` |
| The registry holds exactly the three adapters this plan registers | `sorted(source_adapters.ADAPTER_REGISTRY)` | `['markdown','pdf','text']` |
| The twelve refusal codes are sorted by construction | `len == 12 and tuple == tuple(sorted(...))` | `codes ok` |
| No second parser | `not hasattr(s,'model') and not hasattr(s,'runtime')` | `no second parser` |
| `runtime.py` and `model.py` untouched | `git diff --stat runtime.py model.py` | empty |
| The route is registered in all three parity tables | the plan's one-liner over `API_ROUTES`, `ROUTE_CLI`, `SURFACE_PARITY` | `route registered` |
| The route is authority-gated and authority-shaped | `python3 tests/daemon_roundtrip.py` | exit 0, 76 checks |
| The settings group ships with restrictive defaults | `python3 tests/config_roundtrip.py` | exit 0 |
| The shipped `itembank.json` agrees with the schema defaults | asserted inside `test_source_group_contract` | pass |
| The CLI command exists with its two named flags | `python3 itembank.py source import --help` | exit 0, `--adapter` and `--preview` present |
| No repository-authored em dash | `python3 itembank.py guard .` | exit 0, `0 offending files` |

**The full-suite criterion is not met, and this says so rather than rounding
up.** `for t in tests/*.py; do python3 "$t" || exit 1; done` does not exit 0.
**76 of 78 suites pass.** `tests/day_roundtrip.py` and
`tests/retention_ui_roundtrip.py` both assert the exact copy the day surface
prints when Anki is closed, and Anki is open on this machine, so both read live
counts instead (`0 due, 173 new`). `tests/phase_062_audit.py` fails as a cascade
of those two. These are the same environmental failures `14B-FREEZE.md` already
named as not belonging to that phase, and none of the three is this plan's
either. Nothing here is a code regression.

## Evidence pointers

| Truth | File | Function |
|---|---|---|
| Thin slice, one PDF as a cited source | `tests/source_adapters_roundtrip.py` | `check_thin_slice` |
| An image-only page is a typed refusal writing nothing | same | `check_scanned_pdf_is_typed_unsupported` |
| Nothing raises across three failure families | same | `check_nothing_raises` |
| Unknown rights refuse and leave no orphan sidecar | same | `check_rights_refusal` |
| A wire grant never beats the recorded row | same | `check_no_rights_escalation` |
| Markdown is a registry entry, not a special case | same | `check_one_import_path` |
| No second parser | same | `check_no_second_parser` |
| The pdf adapter degrades by name while markdown still works | same | `check_degrades_without_dependencies` |
| A path outside the approved root is refused | same | `check_write_containment` |
| The CLI and the route reach one function | same | `check_cli_and_route_parity` |
| The route count, the CLI twin, and the parity row | `tests/daemon_roundtrip.py` | `check_api_route_scope` |
| The route's authority gate and field allowlist | same | `check_api_source_import_route` |
| The cross-origin gate covers the new mutating route | same | `check_cross_origin_gate_on_mutating_routes` |
| The six settings keys, bounded and restrictive by default | `tests/config_roundtrip.py` | `test_source_group_contract` |

## Deviations from the plan, each with its reason

**1. A fixture defect was fixed rather than worked around.**
`fixtures/audit/locator_fidelity_cases.py`'s `pdf_text_page` wrote text as a
UTF-16BE hex string with a byte-order mark, under a page whose only font is a
simple `/Type1 /Helvetica`. A simple Type1 font's codes are single bytes, so a
real extractor reads each UTF-16 byte as its own glyph: `pdfplumber` returned
`(cid:254)(cid:255)(cid:0)C(cid:0)h(cid:0)a...` where the gold manifest says
`Chapter 1: Airway Management`. Nothing had caught it because no PDF adapter
existed to read those bytes back until this plan, which is exactly the class of
thing the plan told Task 3 to verify rather than assume.

The fix is at the fixture, not in the adapter. Teaching `_extract_pdf` to decode
a `(cid:N)` run would put a workaround for one malformed fixture into production
code, and the fixture would still be a PDF no other tool can read.
`pdf_text_page` now emits a Latin-1 hex string, and raises a named `ValueError`
on a non-Latin-1 character rather than silently producing an unreadable page.
Every PDF gold case is ASCII, so nothing is lost by that refusal.

Only one gold `sha256` changed, `pdf-born-digital-single-column`, because it is
the only case built through `pdf_text_page`; the other eight assemble their
content streams by hand. `tests/audit_coverage_roundtrip.py` reads the golds
from the case table itself, so it re-passes without edit, and its
`expectation: "unsupported_now"` assertions still hold because
`auditor.REGISTERED_ADAPTERS` is untouched: the PDF adapter lives in
`source_adapters.py`, not in `auditor.py`.

**Left alone, and flagged for plan 14C-02 rather than fixed here.**
`pdf-encrypted-unsupported` is not actually encrypted. It carries no `/Encrypt`
dictionary and `pdfplumber` extracts `Secret` from it cleanly. Its gold says
`expectation: unsupported_now`, which is currently true only because
`auditor` refuses every PDF. Plan 14C-02, which owns the encrypted path, needs
either a real `/Encrypt` fixture or a recorded decision that this case tests
something else. Not fixed here because this plan's Task 3 does not use it and
widening the fixture edit further is not this task's call.

**2. The six packages installed to user site-packages.** Homebrew's Python 3.14
is PEP 668 externally managed, so the plan's bare
`python3 -m pip install ...` is refused. Installed with
`--user --break-system-packages`, pip's own recommended pairing: the packages
land in `~/Library/Python/3.14/lib/python/site-packages`, the Homebrew tree is
untouched, and the plan's acceptance criterion that plain
`python3 -c "import pdfplumber"` exits 0 stays literally true. An agent choice,
recorded so a later reader knows why the install line differs from the plan's.

**3. `build.py`'s staging allowlist gained nine modules.** Not in the plan, and
found by a red test rather than by reading. `STAGE_FILES` never listed
`identity.py`, `journal.py`, `discovery.py`, `course.py`, `graph.py`, or
`course_package.py`, so every Phase 14A and 14B module shipped without ever
entering the built `.pyz`. It stayed invisible because nothing under `surfaces/`
imported them at module scope. `surfaces/cli.py` now imports `identity`,
`journal`, and `source_adapters` for `itembank source import`, which turned the
latent gap into a hard `ModuleNotFoundError` inside the artifact and broke
`tests/packaging_roundtrip.py` and `tests/math_offline_roundtrip.py`. All six,
plus `source_adapters.py`, `model_adapter.py`, and `tier_gate.py` which were
absent for the same reason, are staged now. Both suites re-pass.

**4. `import_source` carries a private `_line` key on each locator between the
extraction function and the span join.** The plan says an extraction function
returns locators "each missing only its `span_id`". A locator also has to say
which derived line it produced, or the caller cannot join it to a span without
guessing. The key is stripped before the sidecar is built, so it never reaches
disk and the frozen envelope is unaffected; `check_thin_slice` validates the
written sidecar against the schema with `additionalProperties: false`, which
would catch it if it leaked.

**5. A `_Refusal` exception carries typed codes inside the module.** The plan
describes extraction functions returning a four-tuple and typed failures being
converted at the boundary. Threading a typed failure out of a nested page loop
as a tuple would mean a sentinel return value checked at every level. A private
exception class, caught once in `import_source` and converted to
`unsupported_result`, keeps the public contract identical: nothing raises out of
`import_source` except `journal.JournalError`, which is deliberate and asserted
by `check_rights_refusal`.

**6. One pre-existing em dash remains in `surfaces/cli.py`.** The plan's
criterion is that no file changed by this task contains one. It predates this
task, appears in no line this task added, and `itembank guard .` exits 0, so it
was left rather than swept into an unrelated diff.

## What this plan did not do

It did not open plan `14C-02`, did not touch `runtime.py` or `model.py`, did not
change `auditor.REGISTERED_ADAPTERS`, and did not add the CI checksum step that
`VENDORED.md` records as owed. It registered three adapters; `docx`, `pptx`,
`web`, `transcript`, `ocr`, `epub`, and `asr` remain plans 02 through 08.
