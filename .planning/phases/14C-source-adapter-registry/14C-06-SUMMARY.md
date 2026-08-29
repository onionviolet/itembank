# Plan 14C-06 summary

Executed 2026-08-28 on Darwin arm64, Python 3.14.6. Tasks 1 and 2 ran and
passed. Task 3 is a blocking human-verify checkpoint and **did not run**; it is
recorded below as unrun, with its date and its reason, and is not marked
passed.

## What landed

- `_extract_ocr`, `_ocr_bridge`, `_image_suffix`, `OCR_NO_TEXT_SENTINEL`, and
  `OCR_IMAGE_SUFFIXES` in `source_adapters.py`. `ocr` is registered at
  `1.0.0`.
- Six checks in `tests/source_adapters_roundtrip.py`, every one of which stubs
  `ocr_lib.ocr_image`, so the whole suite passes on a machine that has never
  installed Ollama. It passed on exactly such a machine here.
- A `## Binding a page as a cited source` section in
  `.claude/skills/ocr/SKILL.md`. Nothing else in that file changed, and
  `scripts/ocr_lib.py`, `scripts/ocr.py`, and `scripts/ocr_mcp.py` are
  untouched.

## The import form that actually resolves

The plan told Task 1 to verify this once rather than assume it. `scripts/`
carries **no `__init__.py`**, so `import scripts.ocr_lib` does not resolve.
The working form, and the one `_ocr_bridge` uses, is to insert the repository's
`scripts` directory on `sys.path` and then `import ocr_lib` flat.

`_ocr_bridge` returns the **module object**, not the function. That is
deliberate and is stated in its docstring: the adapter looks `ocr_image` up on
the module at call time, so a test that swaps the attribute is seen. A function
captured at import time would not be.

## Manual OCR verification

**UNRUN, 2026-08-28.** No Ollama server was reachable on this machine.
`scripts.ocr_lib.find_endpoint()` probed `http://localhost:11434` (the only
candidate, since `OLLAMA_HOST` is unset and this is macOS, so the WSL2
default-gateway candidate does not apply) and raised
`no Ollama server reachable`.

The checkpoint needs three things this session did not have: a running Ollama
with a vision model, a real photographed page of study material, and a human
looking at the result. It is recorded here as unrun rather than assumed. **It
is not marked passed, and no quality judgement is recorded**, because the
one-sentence transcription-quality judgement is the actual output of this
checkpoint and inventing it would defeat the reason the checkpoint exists.

What is still owed, when Ollama is next running:

1. `python3 itembank.py source import --base <course-root> --file <image> --adapter ocr --grant read,quote,transform`, against a base **outside this repository**.
2. Four eye checks: the derived `.md` carries the page's text in reading order
   with nothing invented and no dropped heading; every sidecar locator has
   `"bbox": null` and `"confidence": null` with an envelope `"confidence"` of
   `"low"`; exactly one applied journal entry for the new source; and a second
   run against the same image mints a second source rather than conflicting.
3. Stop Ollama, re-run, and confirm the unreachable-server refusal by name with
   nothing written, while a PDF import in the same session still works.
4. One sentence on transcription quality: good enough to cite, usable with
   corrections, or not usable.

The automated half of what the checkpoint covers is already proven with stubs:
the sidecar shape, the three backend failures and their copy, the sentinel, and
the temp-file cleanup. What remains is the part no stub can reach.

## Which truth was verified by which command and which check

| Truth | Command | `check_*` |
|---|---|---|
| A photographed page imports through the one path with a schema-valid sidecar, three locators, and one applied import entry | `python3 tests/source_adapters_roundtrip.py` | `check_ocr_stubbed_extraction` |
| Null bbox and null confidence on every locator, low envelope confidence, and **the schema itself refuses a fabricated bbox** | same | `check_ocr_honest_degradation` |
| An unreachable server, a missing model, and an HTTP error each become typed results whose copy says what to do, writing nothing and journaling nothing | same | `check_ocr_backend_failures` |
| An image with no text is a named refusal and the sentinel never reaches disk | same | `check_ocr_no_text_sentinel` |
| The decoded image is gone on the success path and on the failure path | same | `check_ocr_temp_file_removed` |
| One OCR path in the repository: no base64, no port, no endpoint path, no prompt, and `_extract_ocr` calls `ocr_image` | same | `check_ocr_single_implementation` |
| Unknown rights still refuse | same | `check_rights_refusal` |
| The whole suite passes with no Ollama server running | `for t in tests/*.py; do python3 "$t" || exit 1; done` | 88 of 88 pass, on a machine where `find_endpoint()` raises |
| `ocr` is registered and the sentinel is exact | `python3 -c "import source_adapters as s; ..."` | prints `ocr registered` |
| The adapter wraps the skill | `python3 -c "import inspect ..."` | prints `wraps the skill` |
| No second OCR path | same | prints `no second ocr path` |
| The two refusal strings are in source | `grep -c` for each | 1, 2 |
| The skill gained its section and names the command | `grep -c` for each | 1, 1 |
| The skill's implementation is wrapped, not edited | `git diff --stat scripts/ocr_lib.py scripts/ocr.py scripts/ocr_mcp.py` | empty |
| `runtime.py`, `model.py`, `auditor.py`, `journal.py` untouched | `git diff --stat` on the four | empty |
| No repository-authored em dash | `python3 itembank.py guard .` | exit 0 |

## Deviations from the plan, each with its reason

1. **Task 3 is unrun, not passed.** Recorded above in full, under the plan's
   own documented outcome for "no Ollama available on this machine".

2. **The plan's em-dash one-liner for Task 2 over-reads, and the section is
   clean.** The criterion splits `SKILL.md` on the new heading and checks
   everything after it, which is the whole rest of the file. `SKILL.md` carries
   seven pre-existing em dashes in sections the same plan explicitly forbids
   rewriting, so that one-liner cannot pass wherever the new section is placed
   except last. Bounded to the new section alone (split again on the next
   `## `), it contains **no em dash**, which is what the criterion is for.
   `python3 itembank.py guard .` exits 0 either way, because `guard` skips the
   `.claude` tree.

3. **`shutil` is now imported at the top of `source_adapters.py`.** The temp
   directory cleanup needs it on every path including every refusal. `tempfile`
   is imported inside `_extract_ocr`, following the lazy per-adapter import
   discipline; `shutil` is stdlib and cheap, and putting it in the `finally`'s
   scope was not worth a second lazy import.

4. **A bare `except Exception` sits after the `RuntimeError` handlers, and it
   is inside the `try` whose `finally` removes the temp directory.** The plan
   asks for the safety net; placing it inside rather than around the cleanup is
   what makes `check_ocr_temp_file_removed` true for the failure path as well
   as the success path.

## What this plan did not do

It did not open plan `14C-07`. It wrote no second OCR path, named no endpoint,
encoded nothing, and carried no transcription prompt: all three live in
`scripts/ocr_lib.py` and stay there, asserted mechanically. It adopted no OCR
library and edited no pin file. It read no multi-page scan and joined no
images. `epub` and `asr` remain plans 07 and 08.
