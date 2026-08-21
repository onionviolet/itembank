---
phase: 14C-source-adapter-registry
plan: 06
type: execute
wave: 6
depends_on: ["14C-05"]
files_modified:
  - source_adapters.py
  - tests/source_adapters_roundtrip.py
  - .claude/skills/ocr/SKILL.md
autonomous: false
requirements: [D-05, ROSTER-6-OCR, RIGHTS-01, TREAT-02]
estimate:
  tokens: 105000
  raw_tokens: 52000
  tasks: 3
  confidence: low
must_haves:
  truths:
    - "A photographed or scanned page becomes a cited source through the one import path, so the ocr skill stops being a side tool with no binding path."
    - "There is exactly one OCR implementation in the repository. The adapter calls scripts/ocr_lib.ocr_image(path) and adds no second prompt, no second endpoint probe, and no second vision-model call."
    - "The OCR locator body reports bbox as null and confidence as null, because scripts/ocr_lib.py returns flat transcribed text with no coordinates and no confidence score. The frozen schema types both fields as null and nothing else, so a fabricated bounding box is rejected by schema validation rather than trusted not to appear."
    - "The sidecar envelope confidence for an OCR source is low, not high and not null, because a vision model transcribing an image is the least reliable extraction in the registry and a citation into it should carry that honestly."
    - "An unreachable Ollama server, a missing vision model, and an HTTP error from the endpoint each convert to a typed unsupported result with a named source.* code. The RuntimeError shapes scripts/ocr_lib.py raises never propagate to a caller."
    - "The whole test suite passes on a machine with no Ollama server running, because every automated OCR assertion injects a stub in place of ocr_lib.ocr_image and the one assertion that needs a real model is a human checkpoint."
    - "The ocr skill's own SKILL.md gains a section pointing at the adapter, so a future agent reading the skill learns that binding a page is now possible and does not rebuild it."
  prohibitions:
    - statement: "No second parser, scorer, or evidence store, and no second OCR path. The adapter wraps scripts/ocr_lib.ocr_image and reimplements nothing."
      status: flagged-unverified
      verification: "check_ocr_single_implementation asserts that source_adapters contains no base64 encoding call, no reference to an Ollama endpoint, and no transcription prompt string, and that _extract_ocr's source text names ocr_lib.ocr_image."
    - statement: "No rewrite of itembank in TypeScript and no plugin kernel reimplemented in Python."
      status: flagged-unverified
      verification: "files_modified contains two Python files and one Markdown skill file, none of them a loader or kernel module."
    - statement: "No hosted multi-tenant anything. The vision model is the learner's own local Ollama server."
      status: flagged-unverified
      verification: "grep source_adapters.py for any absolute URL; the adapter names no endpoint at all, because endpoint probing lives entirely inside scripts/ocr_lib.find_endpoint."
    - statement: "PyMuPDF and ebooklib are not adopted, and no OCR library is adopted."
      status: flagged-unverified
      verification: "deps/source-adapter-pins.txt is not edited by this plan; grep -i -E 'tesseract|pytesseract|easyocr|paddleocr|pymupdf|ebooklib' source_adapters.py returns 0."
    - statement: "An unresolved rights grant is never treated as permissive."
      status: flagged-unverified
      verification: "check_rights_refusal is re-run with an image input; a photographed page whose raw file carries unknown transform rights is refused with journal.rights_unknown."
  artifacts:
    - "_extract_ocr in source_adapters.py and the ocr key in ADAPTER_REGISTRY"
    - "check_ocr_stubbed_extraction, check_ocr_honest_degradation, check_ocr_backend_failures, and check_ocr_single_implementation in tests/source_adapters_roundtrip.py"
    - "the Binding a page as a cited source section in .claude/skills/ocr/SKILL.md"
  key_links:
    - "scripts/ocr_lib.ocr_image(path, model=None, endpoint=None) takes a filesystem path and reads the file itself. Every other adapter in the registry takes raw bytes. The OCR adapter is therefore the one that must materialize its bytes to a temporary file before calling the skill, and must remove that file in a finally, because leaving a decoded image in a temp directory is a copy of learner material nobody tracked."
    - "scripts/ocr_lib.py returns the exact string [no text] when the image contains no text, by its own prompt's instruction. That sentinel is the OCR adapter's unsupported signal and must be matched exactly; treating it as extracted text would put the literal string [no text] into a learner's source Markdown as if it were content."
    - "The frozen body_ocr schema types bbox and confidence as null and nothing else. This is not an oversight to be corrected later by loosening the type; it is the schema making an honest degradation enforceable. A structured-output OCR mode is a schema_version bump and a recorded migration."
---

<objective>
Give a photographed page a binding path. `14C-CONTEXT.md` roster item 6 states
the problem exactly: the local-Ollama `ocr` skill exists but is a side tool with
no binding path, so a photographed page cannot become a cited objective today.
The instruction is equally exact: wrap the existing skill, do not write a second
OCR path.

This is the adapter where honesty matters more than capability.
`14C-CONTEXT.md`'s locator table asks OCR for a source page plus a bounding box
plus a confidence score, and the shipped skill returns none of those: it sends
one fixed transcription prompt to a local vision model and returns flat text.
`14C-RESEARCH.md` Pitfall 2 records this. The resolution is to report the gap
rather than to fabricate geometry, and plan `14C-01` already made that
enforceable by typing `body_ocr.bbox` and `body_ocr.confidence` as `null` in the
frozen schema.

Decisions already made, cited, and never re-litigated here:

- **`14C-CONTEXT.md` roster item 6**: wrap the existing skill; do not write a
  second OCR path.
- **D-05**: the adapter never touches the scorer.
- **D-14C-1** (`14C-DECISIONS.md`): the frozen `body_ocr` row, required
  `medium` const `"ocr"`, `page` integer minimum 1, `bbox` typed `null`,
  `confidence` typed `null`, with the reconsideration condition already recorded
  in `14C-01-PLAN.md`.
- **RESEARCH Pitfall 2**: the skill's actual output shape, read from
  `scripts/ocr_lib.py` in full during the research pass.
- **`.claude/CLAUDE.md` Network constraint**: the core loop degrades, never
  blocks. An unreachable Ollama server is a reported state, not a crash.

Purpose: make a scan citable without inventing data about it.
Output: one more registry entry, its failure conversions, its honest sidecar,
and a pointer back from the skill that now has a binding path.
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
@scripts/ocr_lib.py
@scripts/ocr.py
@.claude/skills/ocr/SKILL.md
@source_adapters.py
</context>

## Artifacts this phase produces (plan 14C-06 share)

- `source_adapters.py`
  - New function `_extract_ocr(raw_bytes, options)`.
  - New constants `OCR_NO_TEXT_SENTINEL = "[no text]"` and
    `OCR_IMAGE_SUFFIXES`, the tuple of accepted image extensions used to pick a
    temporary filename suffix.
  - `ADAPTER_REGISTRY` gains `"ocr"`; `ADAPTER_VERSIONS` gains
    `"ocr": "1.0.0"`.
- `tests/source_adapters_roundtrip.py`
  - `check_ocr_stubbed_extraction`, `check_ocr_honest_degradation`,
    `check_ocr_backend_failures`, `check_ocr_single_implementation`.
- `.claude/skills/ocr/SKILL.md`
  - A new section headed `## Binding a page as a cited source`.

New refusal codes introduced by this plan: none.
`source.backend_unconfigured`, `source.fetch_failed`, `source.unsupported`, and
`source.malformed_input` are already in `SOURCE_ADAPTER_CODES` from plan
`14C-01`.

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: the OCR adapter, wrapping the one implementation that exists</name>
  <files>source_adapters.py, tests/source_adapters_roundtrip.py</files>
  <read_first>
- `scripts/ocr_lib.py` in full, 107 lines. Read every line. The three facts this
  task depends on: `ocr_image(path, model=None, endpoint=None)` takes a
  filesystem path and returns a string; `find_endpoint()` raises a
  `RuntimeError` whose message begins with `no Ollama server reachable` when no
  endpoint answers; and `ocr_image` itself raises a `RuntimeError` on an HTTP
  error, with a distinct message when the model is not present on the endpoint.
  Also note that the module's own transcription prompt instructs the model to
  output the exact string `[no text]` when the image contains no text, which is
  the sentinel this adapter matches.
- `scripts/ocr.py`, the CLI wrapper, to confirm no other entry point exists that
  would be a better wrap target.
- `source_adapters.py` as landed by plans `14C-01` through `14C-05`: the
  four-tuple extraction contract comment above `ADAPTER_REGISTRY`, the lazy
  per-adapter import discipline, and `unsupported_result`.
- The frozen `body_ocr` row in `14C-01-PLAN.md`'s "The frozen sidecar contract"
  section, including the paragraph explaining why `bbox` and `confidence` are
  typed `null`.
- `.planning/phases/14C-source-adapter-registry/14C-RESEARCH.md`, Pitfall 2 in
  full, and the Environment Availability row for the local Ollama server.
  </read_first>
  <behavior>
Write these assertions first, watch them fail, then implement. Every automated
assertion injects a stub in place of `ocr_lib.ocr_image`, so the suite passes
with no Ollama server running anywhere.

- `check_ocr_stubbed_extraction`: with `ocr_image` stubbed to return a
  three-line transcription, importing a small PNG through
  `adapter="ocr"` produces a schema-valid sidecar with three locators, derived
  Markdown containing all three lines, one applied journal entry, and a
  `reading_order` of `["o1.0", "o1.1", "o1.2"]`.
- `check_ocr_honest_degradation`: every locator body from that same run has
  `body["bbox"] is None` and `body["confidence"] is None`, `body["page"] == 1`,
  and the sidecar envelope `confidence` is exactly `"low"`. Additionally,
  hand-build a sidecar identical to the produced one except that one locator
  body carries a four-number `bbox`, run `schema_validate.validate` against it,
  and assert the error list is non-empty. That second half is the assertion that
  matters: it proves the schema itself rejects fabricated geometry rather than
  the adapter merely declining to produce it.
- `check_ocr_backend_failures`, three scenarios, each stubbing `ocr_image` to
  raise: a `RuntimeError` whose message begins `no Ollama server reachable`
  returns `source.backend_unconfigured`; a `RuntimeError` whose message contains
  `not found on` returns `source.backend_unconfigured` with a distinct message
  naming the missing model; any other `RuntimeError` returns
  `source.fetch_failed`. In all three, no Markdown, no sidecar, and no journal
  entry is written, and no exception escapes.
- `check_ocr_no_text_sentinel`: with `ocr_image` stubbed to return exactly
  `[no text]`, the adapter returns `source.unsupported` with the message
  `no text found in the image`, and the literal string `[no text]` appears
  nowhere in any file on disk.
- `check_ocr_single_implementation`: the source text of `source_adapters.py`
  contains no `base64` call, no `11434`, no `/api/chat`, and no string
  containing `OCR engine`, and `inspect.getsource(source_adapters._extract_ocr)`
  contains `ocr_image`. This is the mechanical form of roster item 6's
  instruction.
- `check_ocr_temp_file_removed`: after any of the runs above, including every
  failure scenario, the temporary directory the adapter used contains no file.
  A decoded image left behind is an untracked copy of learner material.
- Extend `check_degrades_without_dependencies` with the ocr case: OCR failing
  for any reason leaves every other adapter working in the same process.
  </behavior>
  <action>
1. Implement `_extract_ocr(raw_bytes, options)` in `source_adapters.py`.
   Import the skill lazily inside the function body, adding the repository root
   to `sys.path` only if needed and importing `scripts.ocr_lib as ocr_lib`, or
   whichever import form actually resolves given how `scripts/` sits in the
   tree; verify the working form once and record it in the summary. On
   `ImportError` return `source.backend_unconfigured` with a message naming
   `scripts/ocr_lib.py` as the missing bridge.

2. Materialize the bytes to a temporary file, because `ocr_image` takes a path
   and every other adapter in the registry takes bytes. Use
   `tempfile.mkdtemp()`, write the bytes with a suffix chosen from the input's
   magic bytes against `OCR_IMAGE_SUFFIXES` (`.png`, `.jpg`, `.webp`, `.gif`,
   `.bmp`, `.tif`), and remove the whole directory in a `finally` that runs on
   every path including every failure path. A decoded image left in a temp
   directory is an untracked copy of learner material, and
   `check_ocr_temp_file_removed` asserts it is gone. Bytes whose magic signature
   matches no entry in `OCR_IMAGE_SUFFIXES` return `source.malformed_input`
   with a message naming the accepted image formats, and never reach the vision
   model.

3. Call `ocr_lib.ocr_image(path)` with no model and no endpoint argument, so
   the skill's own defaults and its own endpoint probing stay the single source
   of that behavior. Wrap the call in `try` and `except RuntimeError as exc`
   and convert by inspecting the message, in this order: a message starting
   with `no Ollama server reachable` becomes `source.backend_unconfigured` with
   the message
   `the local OCR bridge could not reach an Ollama server. Start Ollama, or set OLLAMA_HOST, then run the import again. Every other source adapter is unaffected.`;
   a message containing `not found on` becomes `source.backend_unconfigured`
   with the message
   `the local OCR bridge reached Ollama but the vision model is not installed. Pull the model named in the error, then run the import again.`;
   anything else becomes `source.fetch_failed` carrying the original message
   text. Add a bare `except Exception` after them returning
   `source.internal_error`, so a future change to the skill that raises a
   different class still cannot propagate.

4. Handle the sentinel. When the returned text, stripped, equals
   `OCR_NO_TEXT_SENTINEL`, return `source.unsupported` with the message
   `no text found in the image`. Do not emit the sentinel as content; the
   skill's own prompt promises that exact string and treating it as a
   transcription would put it into a learner's source Markdown as if a human
   had written it.

5. Emit one locator per non-empty line of the returned text, in order, with id
   `"o1.%d" % index`, `kind` `"image_region"`, and body
   `{"medium": "ocr", "page": 1, "bbox": None, "confidence": None}`. The page
   number is always 1 because one image is one page; a multi-page scan is
   imported one image at a time and joining them is a later phase's concern.
   State in the function docstring, in plain sentences, that `bbox` and
   `confidence` are `None` because `scripts/ocr_lib.py` measures neither, that
   the frozen schema types both as `null` so a later change cannot quietly start
   inventing them, and that a structured-output OCR mode would be a
   `schema_version` bump with a recorded migration rather than a loosened type.

6. Set the sidecar envelope `confidence` to `"low"` for every OCR source. A
   vision model transcribing an image is the least reliable extraction in the
   registry, and a citation into it should carry that honestly. This is the
   third distinct use of the envelope `confidence` field in the phase, after
   PDF footnote heuristics (`"medium"`) and inferred transcript end times
   (`"medium"`); the field is doing real work and is not decoration.

7. Register `"ocr"` in `ADAPTER_REGISTRY` and add `"ocr": "1.0.0"` to
   `ADAPTER_VERSIONS`.

8. Add every check named in the `behavior` block to
   `tests/source_adapters_roundtrip.py` and to its `__main__` sequence, and
   extend `check_degrades_without_dependencies` with the ocr case. Every
   automated OCR check stubs `ocr_lib.ocr_image`; none of them requires a
   running Ollama server, and the suite must pass on a machine that has never
   installed one.
  </action>
  <verify>
  <automated>python3 tests/source_adapters_roundtrip.py</automated>
Expected: exit 0 on a machine with no Ollama server running. The degraded states
this task must prove are the three in `check_ocr_backend_failures`: an
unreachable server, a missing model, and an HTTP error each become a typed
result with copy that tells the learner what to do, while every other adapter in
the same process keeps working.
  </verify>
  <acceptance_criteria>
- `python3 tests/source_adapters_roundtrip.py` exits 0 with no Ollama server
  running.
- `python3 -c "import source_adapters as s; assert 'ocr' in s.ADAPTER_REGISTRY and s.ADAPTER_VERSIONS['ocr']=='1.0.0'; assert s.OCR_NO_TEXT_SENTINEL=='[no text]'; print('ocr registered')"` prints `ocr registered`.
- `python3 -c "import inspect, source_adapters as s; src=inspect.getsource(s._extract_ocr); assert 'ocr_image' in src; print('wraps the skill')"` prints `wraps the skill`.
- `python3 -c "import inspect, source_adapters as s; src=inspect.getsource(s); assert 'base64' not in src and '11434' not in src and '/api/chat' not in src; print('no second ocr path')"` prints `no second ocr path`.
- `grep -c "the local OCR bridge could not reach an Ollama server" source_adapters.py` returns at least 1.
- `grep -c "no text found in the image" source_adapters.py` returns at least 1.
- `python3 schema_validate.py --all` exits 0.
- `for t in tests/*.py; do python3 "$t" || exit 1; done` exits 0.
- `python3 itembank.py guard .` exits 0.
- `git diff --stat runtime.py model.py auditor.py journal.py scripts/ocr_lib.py scripts/ocr.py` reports no change. The skill's implementation is wrapped, not edited.
- No file changed by this task contains an em dash character.
  </acceptance_criteria>
  <precondition>scripts/ocr_lib.py exists at the repository root with ocr_image(path, model=None, endpoint=None) unchanged. No Ollama server is required for this task.</precondition>
  <reversibility rating="reversible">One registry entry and one private extraction function that call an already-shipped module.</reversibility>
  <done>A photographed page imports through the one path with an honest sidecar, and every backend failure is a typed result with actionable copy.</done>
</task>

<task type="auto">
  <name>Task 2: point the skill at the binding path it now has</name>
  <files>.claude/skills/ocr/SKILL.md</files>
  <read_first>
- `.claude/skills/ocr/SKILL.md` in full. It currently describes the skill as a
  vision bridge for text-only models and says nothing about sources, citations,
  or binding, because none of that existed when it was written.
- `.claude/skills/OPERATION-CONTRACT.md`, so the new section's language matches
  the operation vocabulary the other skills use.
- `.claude/CLAUDE.md`, the "Course artifact workflow" section, in particular
  step 4 (reuse or link an adequate existing artifact) and step 5 (create only
  genuinely missing treatments), which is what the new section tells a future
  agent to do instead of rebuilding OCR intake.
  </read_first>
  <action>
1. Add one new section to `.claude/skills/ocr/SKILL.md`, headed
   `## Binding a page as a cited source`, placed after the existing
   `## When to use` section. It says, in plain sentences and with no em dash
   character:
   - Reading an image for your own use is what the rest of this skill covers,
     and it is unchanged.
   - Turning a photographed or scanned page into a durable, citable course
     source is a different operation and it now exists:
     `itembank source import --file <image> --adapter ocr`, or
     `POST /api/source/import` with `adapter` set to `ocr`.
   - That path runs this same bridge, writes derived Markdown plus a locator
     sidecar, records one operation journal entry, and produces a source an
     objective can cite. Do not build a second way to do it.
   - The sidecar honestly records `bbox` and `confidence` as null, because this
     bridge transcribes text and does not measure where on the page it sat. A
     citation into an OCR source names the page, not a region. If you need
     region-level citation, that is a change to this skill's output contract and
     a locator schema version bump, not something to work around by guessing
     coordinates.
   - The envelope confidence for an OCR source is `low` by design. Treat an OCR
     transcription as the least reliable source in the course and prefer a
     text-bearing original when one exists.

2. Change nothing else in the file. Do not reword the existing sections, do not
   touch the front matter, and do not alter the transcription prompt or any
   other implementation detail; `scripts/ocr_lib.py` is not edited by this plan
   at all.
  </action>
  <verify>
  <automated>grep -c "Binding a page as a cited source" .claude/skills/ocr/SKILL.md</automated>
Expected: returns 1. Also `python3 itembank.py guard .` exits 0, which matters
because `guard` deliberately skips the `.claude` tree but the run confirms
nothing else drifted.
  </verify>
  <acceptance_criteria>
- `grep -c "Binding a page as a cited source" .claude/skills/ocr/SKILL.md` returns 1.
- `grep -c "adapter ocr" .claude/skills/ocr/SKILL.md` returns at least 1.
- `git diff --stat scripts/ocr_lib.py scripts/ocr.py scripts/ocr_mcp.py` reports no change.
- The new section contains no em dash character, verified with
  `python3 -c "import sys; t=open('.claude/skills/ocr/SKILL.md',encoding='utf-8').read(); s=t.split('## Binding a page as a cited source')[1]; sys.exit(1 if chr(8212) in s else 0)"` exiting 0. The existing sections of the file predate the prose rule and are not rewritten by this plan.
- `python3 itembank.py guard .` exits 0.
  </acceptance_criteria>
  <precondition>Task 1 landed the ocr registry entry, so the command the new section names actually works.</precondition>
  <reversibility rating="reversible">One additive documentation section.</reversibility>
  <done>A future agent reading the ocr skill learns that a page can now be bound as a source, and is told not to build a second way.</done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <name>Task 3: one real photographed page against a real vision model</name>
  <files>.planning/phases/14C-source-adapter-registry/14C-06-SUMMARY.md</files>
  <read_first>
- `.planning/phases/14C-source-adapter-registry/14C-VALIDATION.md`, the
  "OCR adapter against a photographed page" row of the Manual-Only
  Verifications table. That row is why this checkpoint exists: the assertion
  needs a running local Ollama vision model, which is not present in CI.
- `scripts/ocr_lib.py` lines 33 to 68 (`candidate_endpoints`, `find_endpoint`),
  so you know which endpoints the bridge probes and in what order before
  concluding it is unreachable.
  </read_first>
  <what-built>
Task 1 built the OCR adapter and proved every code path with a stubbed
`ocr_image`. Every automated assertion in the suite passes with no Ollama server
anywhere. What no stub can prove is that a real vision model, given a real
photograph of a real textbook page, produces text good enough to be worth citing,
and that the honest degraded sidecar reads correctly when a human looks at it.
  </what-built>
  <how-to-verify>
1. Start Ollama and confirm the vision model is present. `scripts/ocr_lib.py`
   defaults to `qwen2.5vl:7b` unless `OCR_MODEL` is set. Pull it if it is not
   installed.

2. Photograph or screenshot one page of real study material. Any page with a
   heading, a paragraph, and a list is a good test. Keep it outside this
   repository; `itembank guard` exists to catch real course material entering
   the tree, and this file must not enter it.

3. Run, against a base directory outside the repository:
   `python3 itembank.py source import --base <course-root> --file <image> --adapter ocr --grant read,quote,transform`

4. Confirm four things by eye:
   - The derived `.md` file beside the image contains the page's text in reading
     order, with no invented content and no dropped heading.
   - The `.locator.json` sidecar has one locator per line, every one with
     `"bbox": null` and `"confidence": null`, and an envelope `"confidence"` of
     `"low"`.
   - The journal recorded exactly one applied entry for the new source.
   - Running the same command a second time against the same image produces a
     second source object rather than a conflict, since each import mints a new
     id, and does not corrupt the first.

5. Then stop Ollama and run the same command again. Confirm it prints the
   unreachable-server message from Task 1 step 3, exits non-zero, and writes
   nothing. Confirm in the same session that
   `python3 itembank.py source import --file <a pdf> --adapter pdf ...` still
   works, which is the degrade-never-block property with a real backend down.

6. Report the transcription quality in one sentence: good enough to cite, usable
   with corrections, or not usable. That judgement is the actual output of this
   checkpoint and it belongs in the summary.
  </how-to-verify>
  <action>
1. Present the steps above and wait.

2. Record the outcome in
   `.planning/phases/14C-source-adapter-registry/14C-06-SUMMARY.md` under a
   heading `## Manual OCR verification`, capturing: the model used, the page
   described in general terms with no course content reproduced, the four eye
   checks each marked ok or failed, the degraded-run result, and the
   one-sentence quality judgement verbatim.

3. What the executor does with each answer:
   - **approved**: the phase continues to plan `14C-07`.
   - **transcription unusable**: this is not a defect in the adapter, which is a
     wrapper. Record it and continue; the finding belongs to the `ocr` skill's
     own model choice and is a separate decision. Note it in
     `.planning/IDEA-LEDGER.md` as a registered item rather than fixing it here.
   - **a sidecar field is wrong, or the degraded run wrote something**: that is a
     defect in Task 1. Stop, fix it, re-run the automated suite, and re-run this
     checkpoint.
   - **no Ollama available on this machine**: record that the checkpoint could
     not run, with the date, and continue. An honest unrun checkpoint is
     recorded as unrun; it is never marked passed.
  </action>
  <verify>
  <human-check>
A human ran one real photographed page through `itembank source import --adapter ocr`
against a live local vision model, confirmed the four eye checks, confirmed the
stopped-server run refused by name and wrote nothing while another adapter still
worked, and recorded a one-sentence quality judgement in the summary.
  </human-check>
  </verify>
  <acceptance_criteria>
- `.planning/phases/14C-source-adapter-registry/14C-06-SUMMARY.md` contains the
  heading `## Manual OCR verification`.
- That section records the model name, four eye checks each marked ok or failed,
  the degraded-run result, and a verbatim one-sentence quality judgement, or an
  explicit dated statement that no Ollama server was available and the
  checkpoint did not run.
- No image, no page text, and no course material from the verification appears
  anywhere in this repository. `python3 itembank.py guard .` exits 0.
  </acceptance_criteria>
  <precondition>A local Ollama server with a vision model is available on this machine. If it is not, record the checkpoint as unrun and continue; do not mark it passed.</precondition>
  <resume-signal>Type "approved" with the one-sentence quality judgement, or describe what failed.</resume-signal>
  <done>The one thing a stub cannot prove has been checked by a human, or is recorded as unrun with a date.</done>
</task>

</tasks>

<threat_model>
ASVS level 1. Block on `high`.

## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| Learner-supplied image bytes to a temporary file | Arbitrary bytes are written to disk so a path-taking bridge can read them. |
| Image bytes to a local vision model | Learner material leaves itembank's process for a local Ollama server. |
| Model output to the derived source | Text generated by a model becomes course source content. |
| Adapter to durable disk | Derived Markdown and a sidecar are written under the approved root. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-14C-36 | Information Disclosure | a decoded image left in a temp directory | high | mitigate | The temporary directory is created per call and removed in a `finally` that runs on every path, including every failure path and the sentinel path. `check_ocr_temp_file_removed` asserts the directory is empty after each of the failure scenarios, not only after the success one. An untracked copy of learner material on disk is exactly the residency problem `.claude/CLAUDE.md` names. |
| T-14C-37 | Tampering | fabricated locator geometry reaching a citation | high | mitigate | `body_ocr.bbox` and `body_ocr.confidence` are typed `null` and nothing else in the frozen schema, so a sidecar carrying invented coordinates fails `schema_validate.validate` before it is written. `check_ocr_honest_degradation` asserts this by hand-building an invalid sidecar and requiring a non-empty error list, rather than only asserting that the adapter happens not to produce one. |
| T-14C-38 | Tampering | the `[no text]` sentinel written as content | medium | mitigate | The sentinel is matched exactly and converted to `source.unsupported`; `check_ocr_no_text_sentinel` asserts the literal string appears in no file on disk after the run. |
| T-14C-39 | Spoofing | model-generated text presented with the authority of a source | medium | mitigate | The sidecar envelope `confidence` is `"low"` for every OCR source, the derived Markdown is labelled as an OCR transcription in the skill documentation, and `14C-CONTEXT.md`'s own contract makes an adapter a producer of sources and never of assessment truth (D-05). A model transcribing a page is synthesis and is labelled as such. |
| T-14C-40 | Denial of Service | a very large or malformed image | medium | mitigate | `import_source` caps the input at `options["max_input_bytes"]` before the adapter sees it. Bytes whose magic signature matches no accepted image format return `source.malformed_input` and never reach the vision model or the temp file. |
| T-14C-41 | Information Disclosure | learner material reaching a model | low | accept | The bridge targets a local Ollama server on the learner's own machine, probed by `scripts/ocr_lib.find_endpoint`, and this adapter names no endpoint of its own. The already-accepted risk that hosted models see item text is recorded in `.claude/CLAUDE.md` and is unchanged; nothing here sends anything to a hosted provider. |
| T-14C-42 | Elevation of Privilege | model output read as instructions | medium | mitigate | Transcribed text is data. The adapter constructs no prompt, no tool call, and no shell command from it. This is the same boundary the route docstring states in plan `14C-01`, and it matters more here than anywhere else in the phase, because the text was produced by a model reading an image a third party may have prepared. |
| T-14C-SC | Tampering | npm/pip/cargo installs | high | mitigate | No package is introduced. No OCR library is adopted; the shipped `scripts/ocr_lib.py` bridge is wrapped. `deps/source-adapter-pins.txt` is not edited here. |
</threat_model>

<out_of_scope>
- **A second OCR implementation of any kind.** No `pytesseract`, no `easyocr`,
  no `paddleocr`, no second vision-model call, no second prompt, and no second
  endpoint probe. `14C-CONTEXT.md` roster item 6 is explicit and
  `check_ocr_single_implementation` enforces it mechanically.
- **Changing `scripts/ocr_lib.py`.** The skill is wrapped, not edited. A
  structured-output mode that measures geometry would be a change to the skill's
  own contract plus a locator `schema_version` bump, and it is a separate
  decision with its own reconsideration condition already recorded in
  `14C-01-PLAN.md`.
- **Multi-page scans.** One image is one page. Joining a folder of page images
  into one source is a later phase's concern and needs a page-ordering decision
  this plan is not making.
- **PDF page rasterization.** Turning a scanned PDF's pages into images and
  running them through OCR is the obvious next step and is deliberately not
  taken here: it needs a rasterizer, and the only strong candidate is PyMuPDF,
  which is parked on an explicit Weibao AGPL decision. Recorded so the omission
  is a refusal and not an oversight.
- **Region-level or word-level citation into an OCR source.** Impossible with
  the bridge's current output and enforced impossible by the schema.
- **Any change to `runtime.py`, `model.py`, `auditor.py`, `journal.py`, or
  `surfaces/`.**
</out_of_scope>

<verification>
1. `python3 tests/source_adapters_roundtrip.py` (exit 0, with no Ollama running)
2. `python3 schema_validate.py --all` (exit 0)
3. `for t in tests/*.py; do python3 "$t" || exit 1; done` (exit 0)
4. `python3 itembank.py guard .` (exit 0)
5. `git diff --stat runtime.py model.py auditor.py journal.py scripts/` (no output)
</verification>

<success_criteria>
- A photographed page imports through the one path and becomes a citable source.
- Exactly one OCR implementation exists in the repository, proven by source
  inspection and not by claim.
- The sidecar reports what the bridge measures and nothing more, and the schema
  rejects anything more.
- The whole automated suite passes with no Ollama server anywhere.
- The manual checkpoint is recorded as passed or as unrun, never assumed.
- Zero em dash characters in any file or section this plan created.
</success_criteria>

<summary_obligations>
`.planning/phases/14C-source-adapter-registry/14C-06-SUMMARY.md` records:

- The working import form for `scripts/ocr_lib` from `source_adapters.py`, since
  the plan left it to be verified once against the real tree layout.
- The `## Manual OCR verification` section from Task 3 in full, including the
  verbatim quality judgement or the dated unrun statement.
- Whether the three `RuntimeError` message shapes matched what
  `scripts/ocr_lib.py` actually raises, since the conversion is done by message
  inspection and a wording change upstream would silently reroute a failure to
  `source.fetch_failed`. If the match is fragile, say so; that is a real finding
  for a later hardening.
- Which truth was verified by which command and which `check_*` function.
</summary_obligations>

<output>
Create `.planning/phases/14C-source-adapter-registry/14C-06-SUMMARY.md` when done.
</output>
