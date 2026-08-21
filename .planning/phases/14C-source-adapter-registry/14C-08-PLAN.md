---
phase: 14C-source-adapter-registry
plan: 08
type: execute
wave: 8
depends_on: ["14C-07"]
files_modified:
  - source_adapters.py
  - schemas/source_locator.schema.json
  - VENDORED.md
  - scripts/check_vendored.py
  - .github/workflows/ci.yml
  - README.md
  - tests/source_adapters_roundtrip.py
  - .planning/phases/14C-source-adapter-registry/14C-FREEZE.md
  - .planning/ROADMAP.md
  - .planning/REQUIREMENTS.md
autonomous: true
requirements: [D-01, D-02, D-03, D-04, D-05, OQ-1, OQ-2, OQ-3, OQ-4, OQ-5, ROSTER-5-ASR, FILE-01, FILE-03, RIGHTS-01, TREAT-02, PORT-02]
estimate:
  tokens: 150000
  raw_tokens: 75000
  tasks: 3
  confidence: low
must_haves:
  truths:
    - "The asr registry key exists and returns a typed source.backend_unconfigured result naming that no speech backend is configured, so roster item 5 is registered rather than absent and a caller learns why rather than getting an unknown-adapter error."
    - "The asr locator body reuses the transcript body's start_ms and end_ms shape, so when a real backend eventually lands it produces cues into an already-frozen and already-tested locator, not a new one."
    - "Adding the body_asr branch to the frozen schema does not bump schema_version, because a new oneOf branch invalidates no sidecar that already validates, which is the additive-format rule applied to a JSON schema."
    - "VENDORED.md carries a row for every third-party artifact this repository ships: the six adapter pins, KaTeX, CodeMirror, and the two font families, each with a pin, a source URL, a SHA-256, a license, a reviewer, and a review date."
    - "CI recomputes every recorded checksum and fails the build on a mismatch, so silent tampering or an accidental local edit of a vendored artifact is a visible failure rather than a promise in a policy document."
    - "The multi-source coverage audit shows every CONTEXT.md decision, every roster item, every open question, and every 14C-VALIDATION.md frozen behavior row covered by a plan and verified by a named command, with no item left unplanned and no item silently dropped."
    - "The full test suite is green, itembank guard is clean, and runtime.py, model.py, and auditor.py are byte-identical to their state before the phase began."
  prohibitions:
    - statement: "No second parser, scorer, or evidence store."
      status: flagged-unverified
      verification: "check_no_second_parser is re-run; git diff --stat runtime.py model.py auditor.py across the whole phase reports no change, recorded in 14C-FREEZE.md with the diff command and its empty output."
    - statement: "No rewrite of itembank in TypeScript and no plugin kernel reimplemented in Python."
      status: flagged-unverified
      verification: "the phase produced one new Python module, one new schema, five new fixture files, one new script, and no loader, kernel, or plugin-mount machinery; recorded in the freeze file's artifact inventory."
    - statement: "No hosted multi-tenant anything. Snapshots and evidence stay on disk."
      status: flagged-unverified
      verification: "check_write_containment and check_snapshot_containment are re-run; the freeze file records that every durable write in the phase goes through journal.commit_operation or a containment-checked atomic writer."
    - statement: "PyMuPDF and ebooklib are not adopted."
      status: flagged-unverified
      verification: "check_vendored.py fails if any VENDORED.md row or deps/source-adapter-pins.txt pin line names either package; the parking records D-14C-2 and IL-20260815-07 are cited in the freeze file."
    - statement: "An unresolved rights grant is never treated as permissive."
      status: flagged-unverified
      verification: "check_rights_refusal and check_no_rights_escalation are re-run and recorded in the freeze file with their check names."
  artifacts:
    - "_extract_asr in source_adapters.py and the asr key in ADAPTER_REGISTRY"
    - "the body_asr branch in schemas/source_locator.schema.json"
    - "the complete VENDORED.md table with the KaTeX, CodeMirror, and font backfill"
    - "scripts/check_vendored.py and its CI step"
    - "the source adapter section in README.md"
    - ".planning/phases/14C-source-adapter-registry/14C-FREEZE.md"
  key_links:
    - "The asr locator body must be structurally identical to the transcript body apart from its medium const and its segment_index field name. If a future ASR plan invents a different timing shape, every citation into a transcript and every citation into an ASR transcript become two different things that mean the same thing, and the sidecar schema stops being one contract."
    - "Adding a oneOf branch is additive; changing an existing branch is not. schema_version stays 1 here precisely because no sidecar that validated yesterday fails today. A future change that removes or retypes a field in an existing branch is a version bump plus a migrate operation, and the freeze file must say so."
    - "fonts/MANIFEST.json already records SHA-256 for both font families and tests/presentation_roundtrip.py already recomputes them. VENDORED.md's font rows must point at that manifest rather than duplicating the hashes, or two records of the same fact will drift."
---

<objective>
Close the phase. Register roster item 5 so it is a named, typed refusal rather
than an absence. Discharge the vendoring obligation
`SUPPLY-CHAIN-POLICY.md` section 2.2 assigned to the first plan that adds a
vendored artifact after the policy, which is this phase. Then record the freeze:
what is frozen, what breaks if it changes later, and the coverage audit showing
that every source item this phase owed is planned, built, and verified.

Roster item 5 is registered rather than built for the reason
`14C-CONTEXT.md` states: ASR needs whisper.cpp or a hosted call, and the 7900
XTX build does not exist, so this would be CPU or hosted at first. Registering
it now is not a stub for its own sake. It does two real things: a caller asking
for `adapter="asr"` gets a message telling them why it is unavailable rather
than an unknown-adapter error, and the `body_asr` locator shape is frozen and
schema-checked now, so the plan that eventually builds a backend produces cues
into an already-tested locator instead of inventing a second timing shape.

Decisions already made, cited, and never re-litigated here:

- **`14C-CONTEXT.md` roster item 5**: registered, planned last.
- **D-14C-1** (`14C-DECISIONS.md`): the frozen sidecar contract.
- **D-14C-2** (`14C-DECISIONS.md`, plan `14C-07`): `ebooklib` parked on AGPL.
- **`SUPPLY-CHAIN-POLICY.md` sections 2.2, 2.3, and 2.4**: `VENDORED.md` is
  created by the first plan that adds a vendored artifact after the policy,
  KaTeX and CodeMirror rows are backfilled by that same plan, CI recomputes and
  compares the checksums, and each row names its license, reviewer, and review
  date.
- **`PLANNING-DIRECTIVES.md` section 4** non-negotiable 4: format changes are
  additive.

Purpose: leave the phase in a state a later session can trust without rereading
eight plans.
Output: the last registry entry, the discharged vendoring obligation, the
README's account of the new surface, and the freeze record.
</objective>

<execution_context>
@$HOME/.claude/gsd-core/workflows/execute-plan.md
@$HOME/.claude/gsd-core/templates/summary.md
</execution_context>

<context>
@.planning/phases/14C-source-adapter-registry/14C-CONTEXT.md
@.planning/phases/14C-source-adapter-registry/14C-RESEARCH.md
@.planning/phases/14C-source-adapter-registry/14C-VALIDATION.md
@.planning/phases/14C-source-adapter-registry/14C-DECISIONS.md
@.planning/phases/14C-source-adapter-registry/COVERAGE.md
@.planning/phases/14C-source-adapter-registry/14C-01-PLAN.md
@.planning/SUPPLY-CHAIN-POLICY.md
@.planning/phases/14A-identity-lifecycle-operation/14A-FREEZE.md
@deps/source-adapter-pins.txt
@VENDORED.md
@fonts/MANIFEST.json
@.github/workflows/ci.yml
@README.md
</context>

## Artifacts this phase produces (plan 14C-08 share)

- `source_adapters.py`
  - New function `_extract_asr(raw_bytes, options)`.
  - `ADAPTER_REGISTRY` gains `"asr"`; `ADAPTER_VERSIONS` gains
    `"asr": "0.0.0"`, deliberately a zero version because no backend produces
    anything yet.
  - New constant `ASR_BACKENDS = ()`, the empty registered-backend tuple, whose
    emptiness is what `_extract_asr` refuses on.
- `schemas/source_locator.schema.json`
  - New `$defs.body_asr` branch, added to the `$defs.locator.body` `oneOf`.
    `x-itembank-version` and the `schema_version` const stay 1.
- `VENDORED.md`
  - Rows backfilled for KaTeX (`vendor/katex`), CodeMirror
    (`assets/vendor/codemirror/codemirror.bundle.js`), and the two font families
    by reference to `fonts/MANIFEST.json`. The `## Backfill owed` section from
    plan `14C-01` is removed because it is discharged.
- `scripts/check_vendored.py`
  - A stdlib-only script that parses `VENDORED.md`'s table, recomputes each
    on-disk artifact's SHA-256, and exits non-zero on a mismatch, a missing
    file, or a row naming a parked package.
- `.github/workflows/ci.yml`
  - One new step, `Vendored artifacts match their recorded checksums`.
- `README.md`
  - A section documenting `itembank source import` and `itembank source recheck`.
- `.planning/phases/14C-source-adapter-registry/14C-FREEZE.md`
- `.planning/ROADMAP.md` and `.planning/REQUIREMENTS.md`
  - Status updates only: the Phase 14C entry is marked complete with its plan
    list, and the requirement rows this phase advanced are updated in the
    traceability table. No requirement text is rewritten.

New refusal codes introduced by this plan: none.

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: register the ASR adapter as a named refusal with a frozen locator shape</name>
  <files>source_adapters.py, schemas/source_locator.schema.json, tests/source_adapters_roundtrip.py</files>
  <read_first>
- `.planning/phases/14C-source-adapter-registry/14C-CONTEXT.md` roster item 5,
  and `14C-RESEARCH.md`'s State of the Art row for ASR, which names the
  landscape (`faster-whisper` on CTranslate2 versus whisper.cpp bindings) and
  deliberately picks neither.
- `source_adapters.py` as landed by plans `14C-01` through `14C-07`, in
  particular `_extract_transcript` and its locator body shape, which
  `_extract_asr` mirrors, and the `"markdown"` and `"transcript"` registry
  entries whose comments record that they have no lazy-import guard.
- `schemas/source_locator.schema.json` as frozen by plan `14C-01`, in particular
  the `$defs.locator.body` `oneOf` list and the `$defs.body_transcript` branch
  it copies.
- `schema_validate.py` lines 120 to 242, in particular the `oneOf` branch at the
  end, so it is concrete that a new branch cannot make an existing document
  ambiguous: each body carries a `medium` `const`, so exactly one branch matches
  any valid body.
  </read_first>
  <behavior>
Write these assertions first, watch them fail, then implement.

- `check_asr_registered_not_built`: `import_source` with `adapter="asr"` returns
  status `unsupported` with code `source.backend_unconfigured` and a message
  containing the literal `no speech recognition backend is configured`. It
  writes no Markdown, no sidecar, and no journal entry. Crucially,
  `"asr"` is a key of `ADAPTER_REGISTRY`, so the result is a named refusal and
  not `source.adapter_unknown`.
- `check_asr_locator_shape_frozen`: hand-build a sidecar carrying one
  `body_asr` locator with `medium` `"asr"`, `segment_index`, `start_ms`, and
  `end_ms`, and assert `schema_validate.validate` returns an empty error list.
  Then hand-build one with a `cue_index` field instead of `segment_index` and
  assert the error list is non-empty. The shape is frozen and tested before any
  backend exists, which is the whole point of registering now.
- `check_schema_addition_is_additive`: every sidecar produced by every other
  adapter in the suite still validates against the amended schema, and
  `schema_version` is still `1`. Assert this by re-running the existing gold-case
  end-to-end checks after the schema edit rather than by inspection.
- `check_asr_body_matches_transcript_body`: the `body_asr` and
  `body_transcript` `$defs` in `schemas/source_locator.schema.json` have
  identical `required` field sets apart from the index field name, and identical
  types and minimums for `start_ms` and `end_ms`. A structural comparison, not a
  reading.
  </behavior>
  <action>
1. Add `$defs.body_asr` to `schemas/source_locator.schema.json`:
   `additionalProperties: false`, required
   `["medium", "segment_index", "start_ms", "end_ms"]`, with `medium` a
   `const` of `"asr"`, `segment_index` an integer with `minimum: 0`, and
   `start_ms` and `end_ms` integers with `minimum: 0`. Add
   `{"$ref": "#/$defs/body_asr"}` to the `$defs.locator.body` `oneOf` list. Add
   a `description` to `body_asr` recording, in one sentence, that it is
   deliberately the transcript body's shape with a different index field name
   because ASR produces segments rather than authored cues, and that any future
   ASR backend produces into this shape rather than inventing a second timing
   locator.

2. Leave `x-itembank-version` and the `schema_version` `const` at 1, and record
   why in a comment inside the schema's own top-level `description`: adding a
   `oneOf` branch invalidates no document that already validates, so it is an
   additive change under `PLANNING-DIRECTIVES.md` section 4 non-negotiable 4,
   proven by re-running every existing gold-case end-to-end check against the
   amended schema. Removing or retyping a field inside an existing branch would
   not be additive and would need a version bump plus an explicit migrate
   operation.

3. Add `ASR_BACKENDS = ()` to `source_adapters.py` with a comment recording that
   the tuple is empty on purpose: `14C-CONTEXT.md` roster item 5 registers ASR
   and plans it last, because it needs whisper.cpp or a hosted call and the
   target hardware does not exist. The plan that adds the first backend adds a
   member here and a resolution function beside it; until then the emptiness is
   what `_extract_asr` refuses on, so the refusal cannot rot into a stale
   hard-coded message.

4. Implement `_extract_asr(raw_bytes, options)` conforming to the four-tuple
   extraction contract. It returns, immediately and unconditionally while
   `ASR_BACKENDS` is empty, the refusal `source.backend_unconfigured` with the
   message
   `no speech recognition backend is configured. Roster item 5 is registered and not yet built (14C-CONTEXT.md). Supply a transcript file and use the transcript adapter instead, which needs no backend.`
   That last sentence matters: a learner with a lecture recording usually also
   has captions, and pointing at the adapter that already works is more useful
   than reporting an absence.

5. Register `"asr"` in `ADAPTER_REGISTRY` and add `"asr": "0.0.0"` to
   `ADAPTER_VERSIONS`. The zero version is deliberate and stated in a comment:
   no backend produces anything, so claiming `1.0.0` would put a version into a
   sidecar that nothing ever wrote.

6. Add the four checks named in the `behavior` block to
   `tests/source_adapters_roundtrip.py` and to its `__main__` sequence.
  </action>
  <verify>
  <automated>python3 tests/source_adapters_roundtrip.py &amp;&amp; python3 schema_validate.py --all</automated>
Expected: both exit 0. The degraded state this task must prove is the whole
task: `adapter="asr"` is a named, actionable refusal that writes nothing, and
every other adapter's sidecar still validates against the amended schema.
  </verify>
  <acceptance_criteria>
- `python3 tests/source_adapters_roundtrip.py` exits 0.
- `python3 schema_validate.py --all` exits 0.
- `python3 -c "import source_adapters as s; assert sorted(s.ADAPTER_REGISTRY)==['asr','docx','epub','markdown','ocr','pdf','pptx','text','transcript','web']; assert s.ASR_BACKENDS==(); assert s.ADAPTER_VERSIONS['asr']=='0.0.0'; print('ten adapters registered')"` prints `ten adapters registered`.
- `python3 -c "import json; d=json.load(open('schemas/source_locator.schema.json')); assert d['x-itembank-version']==1; assert d['properties']['schema_version']['const']==1; assert 'body_asr' in d['\$defs']; print('schema additive')"` prints `schema additive`.
- `grep -c "no speech recognition backend is configured" source_adapters.py` returns at least 1.
- `for t in tests/*.py; do python3 "$t" || exit 1; done` exits 0.
- `python3 itembank.py guard .` exits 0.
- No file changed by this task contains an em dash character.
  </acceptance_criteria>
  <precondition>Plans 14C-01 through 14C-07 landed, so nine registry keys already exist and the schema is frozen.</precondition>
  <reversibility rating="reversible">The registry entry and the schema branch are additive; removing them restores the plan 14C-07 state and invalidates nothing, because nothing has written a body_asr locator.</reversibility>
  <done>Roster item 5 is a named refusal with a frozen, tested locator shape, and the schema addition is proven additive rather than asserted to be.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: discharge the vendoring obligation with a real CI checksum gate</name>
  <files>VENDORED.md, scripts/check_vendored.py, .github/workflows/ci.yml, README.md</files>
  <read_first>
- `.planning/SUPPLY-CHAIN-POLICY.md` sections 2.2, 2.3, 2.4, and 4 in full.
  Section 2.2 assigns `VENDORED.md` and the KaTeX and CodeMirror backfill to the
  first plan that adds a vendored artifact after the policy, which is this
  phase. Section 2.3 requires CI to recompute and compare. Section 5 states that
  a threat table may no longer accept supply-chain risk on the grounds that no
  dependency is installed, which is why this task is not optional.
- `VENDORED.md` as created by plan `14C-01` Task 2, including its
  `## Backfill owed` section, which this task discharges and removes.
- `fonts/MANIFEST.json` in full. It already records SHA-256 for every font file
  and `tests/presentation_roundtrip.py` already recomputes them. The font rows
  in `VENDORED.md` point at that manifest and do not duplicate the hashes, or
  two records of the same fact will drift.
- `.github/workflows/ci.yml` lines 140 to 160, the two existing script-driven
  gates (`scripts/check_readme_commands.py` and
  `python schema_validate.py --all schemas`), whose step shape the new step
  copies.
- `scripts/check_readme_commands.py` in full. It is the closest precedent for a
  small stdlib-only CI gate script in this repository, including its exit-code
  convention and its output style.
- `README.md`, wherever the command index lives, since
  `scripts/check_readme_commands.py` asserts that every bare command token in a
  README code block is a registered subcommand. Adding `source` to the README
  is therefore checked automatically.
  </read_first>
  <behavior>
Write the script's own self-test first, as a `check_vendored_manifest` function
in `tests/source_adapters_roundtrip.py`, watch it fail, then implement.

- `check_vendored_manifest`: `scripts/check_vendored.py` exits 0 against the
  repository as committed. Then, in a temporary copy of the tree, append one
  byte to a vendored artifact and assert the script exits non-zero and names the
  file. Then, in another temporary copy, delete a vendored artifact and assert
  the script exits non-zero and names the missing file. Then, in a third,
  add a `VENDORED.md` row naming `ebooklib` and assert the script exits non-zero
  and names the parked package. A checksum gate that has never been seen to fail
  is not a gate.
  </behavior>
  <action>
1. Complete the `VENDORED.md` table. It already carries the six adapter pin rows
   from plan `14C-01`. Add:
   - **KaTeX**: artifact `vendor/katex`, the pinned version read from
     `vendor/katex/katex.min.js`'s own version banner, the upstream project URL,
     the release URL, the SHA-256 of `katex.min.js` and of `katex.min.css`
     recomputed now, license MIT read from `vendor/katex/LICENSE`, reviewer and
     review date of today.
   - **CodeMirror 6**: artifact
     `assets/vendor/codemirror/codemirror.bundle.js`, its pinned version read
     from wherever the bundle or its build record names it, the upstream project
     URL, the SHA-256 recomputed now, its license, reviewer and review date of
     today. If the bundle carries no discoverable version string, record that
     fact in the row rather than inventing a version, and note in the row that
     recording the exact pin is owed by the next plan that touches the check
     editor.
   - **Fonts**: two rows, Source Serif 4 and iA Writer Quattro, whose SHA-256
     column reads `see fonts/MANIFEST.json` and whose reviewer and review date
     are copied from that manifest's own `reviewer_date`. Add a note under the
     table stating that the font hashes live in `fonts/MANIFEST.json` and are
     recomputed by `tests/presentation_roundtrip.py`, so `VENDORED.md` points at
     one record rather than creating a second.
   Remove the `## Backfill owed` section; it is discharged.

2. Add a `## Update cadence` section to `VENDORED.md` per
   `SUPPLY-CHAIN-POLICY.md` section 4: vendored artifacts are reviewed at each
   phase that touches their surface and at minimum once per milestone, and each
   review is recorded as a dated note in this file. Add today's dated note
   recording that the six adapter pins were reviewed at adoption in plan
   `14C-01` and that KaTeX, CodeMirror, and the fonts were backfilled without an
   upgrade.

3. Write `scripts/check_vendored.py`, stdlib only, following
   `scripts/check_readme_commands.py`'s shape. It parses `VENDORED.md`'s pipe
   table, and for each row: skips rows whose SHA-256 column is a pointer rather
   than a hash, resolving those to their pointed-at manifest and checking the
   hashes there instead; resolves the artifact path relative to the repository
   root; exits non-zero naming the file when it is missing; recomputes its
   SHA-256 and exits non-zero naming the file, the recorded hash, and the
   computed hash when they differ; and exits non-zero when any row's artifact
   name matches `pymupdf`, `fitz`, or `ebooklib`, because those are parked and a
   row for one of them means the parking was bypassed. For a directory-valued
   artifact such as `vendor/katex`, hash the specific files the row names rather
   than the directory, since a directory has no canonical hash and inventing one
   would make the gate order-dependent. On success it prints one line per
   verified artifact and a final count, matching the existing gate scripts'
   output style.

4. Add one CI step to `.github/workflows/ci.yml`, placed immediately after the
   existing `Every published schema self-checks` step, named
   `Vendored artifacts match their recorded checksums`, running
   `python scripts/check_vendored.py`. Give it a comment block in the register
   of its neighbors explaining what it closes:
   `SUPPLY-CHAIN-POLICY.md` section 2.3 requires CI to recompute and compare
   every recorded checksum, and section 5 states that a threat table may no
   longer accept supply-chain risk on the grounds that no dependency is
   installed. This step is the mitigation that replaces the stale one.

5. Add a `source` section to `README.md` documenting the new surface, in the
   register of the existing command documentation: `itembank source import`
   with `--file` or `--url`, `--adapter` naming the ten registered adapters,
   `--grant`, `--preview`, `--snapshot-storage`, and `--confirm`; and
   `itembank source recheck` with its three reported states and its exit-code
   rule. State in one sentence that the adapter dependencies are optional and
   pinned in `deps/source-adapter-pins.txt`, that an adapter with a missing
   library refuses by name with its install command, and that the markdown,
   text, transcript, and epub adapters need no third-party package at all.
   `scripts/check_readme_commands.py` asserts that every bare command token in a
   README code block is a registered subcommand, so this section is checked by
   the existing CI gate.

6. Add `check_vendored_manifest` to `tests/source_adapters_roundtrip.py` and to
   its `__main__` sequence.
  </action>
  <verify>
  <automated>python3 scripts/check_vendored.py &amp;&amp; python3 scripts/check_readme_commands.py &amp;&amp; python3 tests/source_adapters_roundtrip.py</automated>
Expected: all three exit 0. The degraded state this task must prove is the gate
failing: `check_vendored_manifest` mutates a copy of the tree three ways and
asserts a non-zero exit and a named file each time. A checksum gate that has
never been observed to fail is a comment, not a gate.
  </verify>
  <acceptance_criteria>
- `python3 scripts/check_vendored.py` exits 0 and its final line reports a count
  of at least nine verified artifacts.
- `python3 scripts/check_readme_commands.py` exits 0.
- `python3 tests/source_adapters_roundtrip.py` exits 0.
- `grep -c "Backfill owed" VENDORED.md` returns 0.
- `grep -c "Update cadence" VENDORED.md` returns 1.
- `grep -c "check_vendored.py" .github/workflows/ci.yml` returns at least 1.
- `python3 -c "import sys; t=open('VENDORED.md',encoding='utf-8').read(); import re; rows=[l for l in t.splitlines() if l.startswith('|') and 'sha256' not in l.lower()]; assert len(rows)>=10; print('table rows', len(rows))"` prints a row count of at least 10.
- `grep -c -i -E 'pymupdf|fitz|ebooklib' VENDORED.md` finds those strings only
  inside a prose note recording the parking, never inside a table row.
- `for t in tests/*.py; do python3 "$t" || exit 1; done` exits 0.
- `python3 itembank.py guard .` exits 0.
- No file changed by this task contains an em dash character.
  </acceptance_criteria>
  <precondition>VENDORED.md exists from plan 14C-01 Task 2 with its six adapter rows and its Backfill owed section.</precondition>
  <reversibility rating="reversible">A documentation table, a stdlib script, and one CI step; all three are removable without touching runtime behavior.</reversibility>
  <done>Every third-party artifact this repository ships has a row with a recomputed checksum, and CI fails on a mismatch, observed failing three ways before being trusted.</done>
</task>

<task type="auto">
  <name>Task 3: the phase freeze and the multi-source coverage audit</name>
  <files>.planning/phases/14C-source-adapter-registry/14C-FREEZE.md, .planning/ROADMAP.md, .planning/REQUIREMENTS.md</files>
  <read_first>
- `.planning/phases/14A-identity-lifecycle-operation/14A-FREEZE.md` in full. It
  is the exact precedent: what is frozen, what breaks if it changes later, the
  measured evidence, and the recorded reconsideration conditions. Copy its
  structure, not its content.
- `.planning/phases/14C-source-adapter-registry/14C-VALIDATION.md`, the
  per-task verification map in full. Every row's `Task ID` column is filled in
  by this task from the eight plans' actual task names, and every `Status`
  column becomes green or is honestly marked otherwise.
- `.planning/phases/14C-source-adapter-registry/14C-CONTEXT.md` in full again:
  the five decisions, the seven roster items, the two build-both items, the five
  out-of-scope refusals, and the five open questions. Every one of those
  twenty-four items is a row in the coverage audit.
- `.planning/phases/14C-source-adapter-registry/COVERAGE.md`, whose
  `INTEGRATE` and `OPT-OUT` rows the freeze file confirms were honored, using
  plan `14C-04`'s summary as the evidence.
- Every `14C-0N-SUMMARY.md` written by plans 01 through 07, for the recorded
  deviations, the discovered API shapes, and any gold case that could not be
  reproduced.
- `.planning/ROADMAP.md`, the Phase 14C entry at line 107, and
  `.planning/REQUIREMENTS.md`'s traceability table near line 1276, for the
  status rows this task updates.
  </read_first>
  <action>
1. Create `.planning/phases/14C-source-adapter-registry/14C-FREEZE.md` with
   these sections, in this order.

   **`## Frozen at 14C`.** The exact surface later phases may build against:
   the ten `ADAPTER_REGISTRY` keys; the twelve `SOURCE_ADAPTER_CODES` members;
   `schemas/source_locator.schema.json` at `x-itembank-version` 1 with its
   envelope fields, its `$defs.locator` shape, and its nine per-medium bodies;
   the `import_source`, `preview_source`, `capture_url`, and `recheck_origin`
   public function signatures; the two route literals
   `POST /api/source/import` and `POST /api/source/recheck`; the two CLI
   commands `itembank source import` and `itembank source recheck`; the six
   `source` settings keys; the `_sources` and `_sources/cache` directory names;
   the derived-path rule (`<raw path>.md` and `<raw path>.locator.json` for a
   local file, `_sources/<source_id>.md` for a capture); and the `span_id` join
   rule. State the `journal.op_link` `rights=None` parameter addition, the one
   line of `journal.py` this phase changed.

   **`## What breaks if this is changed later`.** One paragraph per frozen
   item, in the register of `14A-FREEZE.md`'s own section of that name. At
   minimum: renaming a sidecar field breaks every sidecar written and every
   citation that names a span in one; changing the `span_id` join breaks the
   link between an origin locator and the one parser's spans; renaming a route
   literal or a CLI command breaks any external harness, including a
   Cordis-based one, which D-02 explicitly invites; removing or retyping a field
   inside an existing `oneOf` branch is not additive and needs a
   `schema_version` bump plus a migrate operation; and changing the two-file
   write ordering reintroduces the applied-source-with-no-sidecar state that
   `check_two_file_pair_atomicity` exists to prevent.

   **`## Multi-source coverage audit`.** One table with the columns: source,
   item, covered by, verified by, status. One row per item from all four
   sources, none omitted:
   - GOAL: the ROADMAP Phase 14C goal line, one row.
   - REQ: `FILE-01`, `FILE-03`, `RIGHTS-01`, `TREAT-02`, `PORT-02`, one row
     each. These are the `REQUIREMENTS.md` families this phase advanced; ROADMAP
     assigns no requirement IDs to 14C, which is itself recorded as a row with
     status `no IDs assigned in ROADMAP; coverage derived from CONTEXT.md per
     the phase description's own instruction`.
   - RESEARCH: the five pitfalls, the six assumptions A1 through A6, the AGPL
     finding, the RIGHTS-01 no-new-code finding, the OCR flat-text finding, and
     the eight-package legitimacy batch, one row each.
   - CONTEXT: D-01 through D-05, roster items 1 through 7, the two build-both
     items, and the five out-of-scope refusals, one row each.
   - VALIDATION: every frozen behavior row in `14C-VALIDATION.md`'s per-task
     verification map, one row each.
   Every row's `verified by` cell names a specific `check_*` function or a
   specific command, never a plan number alone. A row with no verification is
   marked `flagged-unverified` with the reason, and is never quietly marked
   covered.

   **`## Spec-less probe fallback`.** Record, visibly, that Phase 14C had no
   `SPEC.md` and no requirement IDs in ROADMAP, that the spec-less probe
   fallback was therefore skipped on purpose during planning, that no
   probe-derived predicates were generated, and that `must_haves` were derived
   instead from CONTEXT.md's decisions and `14C-VALIDATION.md`'s frozen behavior
   rows. This is a recorded choice, not a silent gap.

   **`## Recorded deviations`.** Every deviation from the eight plans, lifted
   from the seven summaries, with its reason. At minimum, record: that roster
   item 1 was split across plans `14C-01` and `14C-02` for tracer discipline;
   the real `pdfplumber.Page.extract_words()` and `find_tables()` key names, if
   they differed from the plan's assumption A2 description; whether
   `surfaces.update._origin_of` was imported or duplicated; and any gold case
   whose recorded reading order the adapter could not reproduce.

   **`## Open reconsideration conditions`.** The conditions recorded across the
   phase that a later session must be able to find: D-14C-2's `ebooklib` AGPL
   parking and its trigger; PyMuPDF's parking; `trafilatura`'s dependency-weight
   refusal and its trigger; `webvtt-py`'s cost refusal and its trigger; the
   `body_ocr` null-typed geometry and the structured-OCR trigger; the
   `_parse_xml_safely` DOCTYPE refusal and whether a legitimate XHTML doctype
   forced it to become format-specific; the DNS-rebinding limit in
   `_host_is_private`; and the unread EPUB navigation document.

   **`## Evidence`.** The verbatim final output line of
   `for t in tests/*.py; do python3 "$t" || exit 1; done`, the output of
   `python3 schema_validate.py --all`, the output of
   `python3 scripts/check_vendored.py`, the output of
   `python3 itembank.py guard .`, and the output of
   `git diff --stat runtime.py model.py auditor.py`, which must be empty. Record
   each command and its output, not a claim about it.

2. Fill in `14C-VALIDATION.md`'s per-task verification map: every `Task ID`
   column gets the real plan and task, every `Status` column becomes green or is
   honestly marked red or flagged, and set `nyquist_compliant: true` in its
   frontmatter only if every row has an automated verify or a recorded manual
   checkpoint. If any row does not, leave it `false` and say which row in the
   freeze file.

3. Update `.planning/ROADMAP.md`'s Phase 14C entry: mark the checkbox complete
   and add the plan list with each plan's one-line objective. Use a scoped edit;
   do not rewrite the file.

4. Update `.planning/REQUIREMENTS.md`'s traceability table rows for the
   requirement families this phase advanced, and nothing else. Do not rewrite
   any requirement text. `PORT-02` moves no further than its existing state,
   because this phase adds the EPUB import direction to a prototype-level
   adapter and does not complete the requirement.

5. Every file this task writes contains no em dash character.
  </action>
  <verify>
  <automated>for h in "Frozen at 14C" "What breaks if this is changed later" "Multi-source coverage audit" "Spec-less probe fallback" "Recorded deviations" "Open reconsideration conditions" "Evidence"; do grep -q "^## $h" .planning/phases/14C-source-adapter-registry/14C-FREEZE.md || { echo "missing section: $h"; exit 1; }; done; echo "freeze sections present"</automated>
Expected: prints `freeze sections present` and exits 0. The degraded state this
task must prove is an honest audit: a coverage row with no verification is
marked `flagged-unverified` with its reason and is not quietly marked covered,
and `nyquist_compliant` stays `false` when any behavior row lacks an automated
verify or a recorded manual checkpoint. A green audit that was made green by
lowering the bar is the one failure mode this task exists to avoid.
  </verify>
  <acceptance_criteria>
- `.planning/phases/14C-source-adapter-registry/14C-FREEZE.md` exists and
  contains all seven required section headings, verified by the command above.
- The `## Multi-source coverage audit` table contains at least 40 data rows,
  covering the ROADMAP goal, the five requirement families, every RESEARCH
  pitfall and assumption and finding, all five CONTEXT decisions, all seven
  roster items, both build-both items, all five out-of-scope refusals, and every
  `14C-VALIDATION.md` behavior row. Verified by
  `python3 -c "import sys; t=open('.planning/phases/14C-source-adapter-registry/14C-FREEZE.md',encoding='utf-8').read(); s=t.split('## Multi-source coverage audit')[1].split(chr(10)+'## ')[0]; rows=[l for l in s.splitlines() if l.startswith('|') and not set(l) <= set('|- ')]; assert len(rows)>=40, len(rows); print('audit rows', len(rows))"`.
- Every row of that table has a non-empty `verified by` cell, verified by
  eye during review and by the row-count command above not counting separator
  rows.
- `grep -c "D-14C-2" .planning/phases/14C-source-adapter-registry/14C-FREEZE.md`
  returns at least 1, confirming the `ebooklib` parking is carried into the
  freeze record and not left only in the decisions file.
- `grep -c "flagged-unverified" .planning/phases/14C-source-adapter-registry/14C-FREEZE.md`
  returns whatever the honest count is; a return of 0 is acceptable only if
  every single row genuinely has a named verification.
- `python3 -c "import sys; t=open('.planning/phases/14C-source-adapter-registry/14C-VALIDATION.md',encoding='utf-8').read(); assert 'TBD' not in t, 'a Task ID column was left as TBD'; print('validation map filled')"` prints `validation map filled`.
- `grep -c "14C-08-PLAN.md" .planning/ROADMAP.md` returns at least 1, confirming
  the plan list landed.
- `for t in tests/*.py; do python3 "$t" || exit 1; done` exits 0.
- `python3 schema_validate.py --all` exits 0.
- `python3 scripts/check_vendored.py` exits 0.
- `python3 itembank.py guard .` exits 0.
- `git diff --stat runtime.py model.py auditor.py` produces no output, across
  the whole phase and not only this plan.
- No file this task wrote contains an em dash character.
  </acceptance_criteria>
  <precondition>Plans 14C-01 through 14C-07 executed and wrote their SUMMARY files, because this task lifts recorded deviations from them rather than reconstructing them.</precondition>
  <reversibility rating="reversible">Documentation and status updates only; no runtime behavior is touched.</reversibility>
  <done>A later session can read one file and know exactly what is frozen, what breaks if it moves, what every source item resolved to, and what conditions would reopen a parked decision.</done>
</task>

</tasks>

<threat_model>
ASVS level 1. Block on `high`.

## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| Third-party artifact to the shipped product | Nine vendored or pinned artifacts ship with or build the product. |
| Registry to the developer machine | Six pinned packages are installed at checkout time. |
| Caller to an unbuilt adapter | A request naming `adapter="asr"` reaches a registry entry with no backend. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-14C-SC | Tampering | npm/pip/cargo installs and every vendored artifact | high | mitigate | `VENDORED.md` records a pin, a source URL, a SHA-256, a license, a reviewer, and a review date for all nine artifacts. `scripts/check_vendored.py` recomputes every hash and CI runs it, so silent tampering or an accidental local edit fails the build. `SUPPLY-CHAIN-POLICY.md` section 5's stale mitigation, that no dependency is installed, is replaced by an actually-running check. The gate is observed failing three ways in `check_vendored_manifest` before it is trusted. |
| T-14C-49 | Spoofing | a `VENDORED.md` row for a parked package | high | mitigate | `scripts/check_vendored.py` exits non-zero when any row names `pymupdf`, `fitz`, or `ebooklib`, so the AGPL parking cannot be bypassed by quietly adding a row. Asserted in `check_vendored_manifest`. |
| T-14C-50 | Denial of Service | a registered adapter with no backend | low | mitigate | `_extract_asr` returns immediately with a typed refusal and never attempts a network call, a subprocess, or a model load, because `ASR_BACKENDS` is empty. There is no code path from `adapter="asr"` to any external resource. |
| T-14C-51 | Repudiation | a coverage audit made green by lowering the bar | high | mitigate | Every audit row's `verified by` cell must name a specific `check_*` function or a specific command, and a row with no verification is marked `flagged-unverified` with its reason rather than marked covered. The `## Evidence` section records command output verbatim rather than a claim about it. |
| T-14C-52 | Tampering | a non-additive schema change presented as additive | high | mitigate | Task 1 proves the `body_asr` addition is additive by re-running every existing gold-case end-to-end check against the amended schema rather than by inspection, and the freeze file records that removing or retyping a field inside an existing branch would need a `schema_version` bump plus a migrate operation. |
</threat_model>

<out_of_scope>
- **Building an ASR backend.** `ASR_BACKENDS` stays empty. No whisper.cpp
  binding, no hosted speech endpoint, no model download, no request
  construction. `14C-RESEARCH.md`'s State of the Art row names the landscape and
  deliberately picks nothing; the plan that builds a backend makes that choice
  with its own adoption record.
- **Upgrading KaTeX, CodeMirror, or the fonts.** The backfill records what
  ships today. An upgrade is a normal compare-and-swap mutation with its own new
  pin, new checksum, reviewed diff, and revert path, per
  `SUPPLY-CHAIN-POLICY.md` section 4.
- **Vendoring the six adapter packages as bytes in the tree.** They follow the
  `deps/lti-pins.txt` precedent: optional, guarded, pinned with recorded
  hashes, degrading by name when absent. Copying wheels into the repository is a
  different decision with a different size cost.
- **Rewriting any requirement text in `REQUIREMENTS.md`.** Status rows only.
- **Any 14B binding work.** This phase produces `source` objects. Binding one to
  an objective is 14B's half.
- **Any change to `runtime.py`, `model.py`, `auditor.py`, or `journal.py`.**
  `journal.py`'s one additive `op_link` parameter landed in plan `14C-01` and
  nothing further is touched.
</out_of_scope>

<verification>
1. `python3 tests/source_adapters_roundtrip.py` (exit 0)
2. `python3 schema_validate.py --all` (exit 0)
3. `python3 scripts/check_vendored.py` (exit 0)
4. `python3 scripts/check_readme_commands.py` (exit 0)
5. `for t in tests/*.py; do python3 "$t" || exit 1; done` (exit 0)
6. `python3 itembank.py guard .` (exit 0)
7. `diff -rq .agents/skills .claude/skills` (no output; the skill mirrors stay
   identical, which matters because plan `14C-06` edited
   `.claude/skills/ocr/SKILL.md` and the mirror must be updated to match)
8. `git diff --stat runtime.py model.py auditor.py` (no output)
</verification>

<success_criteria>
- Ten adapters are registered, nine build something and one refuses by name.
- The frozen schema carries nine per-medium locator bodies at
  `schema_version` 1, and the last addition is proven additive.
- Every third-party artifact has a checksummed row and CI fails on a mismatch.
- The freeze file answers, in one place, what is frozen, what breaks if it
  moves, what every source item resolved to, and what would reopen each parked
  decision.
- Zero em dash characters in any file this plan created or changed.
</success_criteria>

<summary_obligations>
`.planning/phases/14C-source-adapter-registry/14C-08-SUMMARY.md` records:

- The discovered KaTeX and CodeMirror version strings, or the recorded fact that
  the CodeMirror bundle carries no discoverable version and the pin is owed by
  the next plan that touches the check editor.
- The three ways `check_vendored_manifest` made the gate fail, with the exit
  codes and messages observed, so the gate's failure behavior is on record and
  not assumed.
- Whether `diff -rq .agents/skills .claude/skills` needed the plan `14C-06`
  mirror update, and confirmation that it was made.
- Any coverage-audit row that ended `flagged-unverified`, with its reason. This
  is the phase's honest residue and it belongs in the summary as well as in the
  freeze file.
- Which truth was verified by which command and which `check_*` function.
</summary_obligations>

<output>
Create `.planning/phases/14C-source-adapter-registry/14C-08-SUMMARY.md` when done.
</output>
