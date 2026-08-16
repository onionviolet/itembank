---
phase: 16C-strategies-notes-prototype-convergence
plan: 08
type: execute
wave: 5
depends_on: ["16C-07"]
files_modified:
  - upgrade_audit.py
  - fixtures/legacy_pre135_bank.md
  - tests/legacy_upgrade_roundtrip.py
  - .agents/skills/legacy-upgrade/SKILL.md
  - .claude/skills/legacy-upgrade/SKILL.md
autonomous: true
requirements: [UPGRADE-01, UPGRADE-02]
estimate:
  tokens: 70000
  raw_tokens: 70000
  tasks: 3
  confidence: low
must_haves:
  truths:
    - "Every legacy-artifact upgrade begins with the eleven-item baseline audit in fixed order (current parse, identity, fingerprint, objectives, sources, rights, media, assessment boundaries, plain rendering, rich rendering, validation), and an item whose backing record is unavailable reads plan-text stand-in, never an invented pass."
    - "The upgrade presents a bounded diff before editing: each change carries before, after, and its stated learning-value reason; a change with no learning value is skipped with the locked sentence and never proposed for acceptance."
    - "Stable identity and source history are preserved: an accepted upgrade never changes the artifact's item IDs, and the audit records identity before and after."
    - "An artifact that cannot express an enhancement retains its form and links a derived enhancement with its portability cost, using a trio projection as the derived form."
    - "An upgrade touching keyed content, difficulty, or objective alignment halts for explicit assessment review with the locked sentence and exactly two affordances; no override control exists."
  prohibitions:
    - statement: "Keyed content, assessment meaning, difficulty, and objective alignment must never be silently changed by an upgrade; the halt is the contract, not a warning."
      status: kept
      verification: flagged-unverified
    - statement: "Cosmetic novelty is rejected: a change whose reason states no learning value never reaches the proposed-changes list."
      status: kept
      verification: flagged-unverified
    - statement: "The skill mirrors stay identical: .agents/skills and .claude/skills receive byte-identical SKILL.md updates or CI fails."
      status: kept
      verification: flagged-unverified
  artifacts:
    - "upgrade_audit.py with BASELINE_AUDIT_ITEMS, the locked copy constants, baseline_audit, bounded_diff, keyed_meaning_delta, run_upgrade"
    - "fixtures/legacy_pre135_bank.md, a synthetic pre-13.5 lesson artifact"
    - "tests/legacy_upgrade_roundtrip.py green"
    - "both legacy-upgrade SKILL.md mirrors updated from stub to reference the shipped functions"
  key_links:
    - "keyed_meaning_delta composes the shipped model.content_fingerprint and model._key_content_hash; a new hash scheme here would mask exactly the drift D-14A-2's carve-out exists to expose."
    - "run_upgrade calls baseline_audit first and refuses to diff before the audit list is complete; the audit-first ordering is enforced by code, not by skill prose."
    - "The cannot-express path links a note_outputs projection as the derived enhancement, which is why this plan depends on 16C-07."
    - "The skill text references upgrade_audit functions by name rather than restating rules, so the code and the playbook cannot drift."
---

<objective>
Land the legacy-upgrade contract: the eleven-item baseline audit, the
bounded diff with cosmetic rejection, the cannot-express derived-enhancement
link, the keyed-meaning halt, and the skill playbook that drives them.

Decisions already made, cited, and never re-derived here:

- **16C-DECISIONS.md `## D12` (UI-SPEC)**: audit-first ordering, the
  DiffApproval shape for the bounded diff, plan-text stand-in for
  unavailable audit rows, and the blocking halt with exactly two
  affordances and no override.
- **REQUIREMENTS.md UPGRADE-01 and UPGRADE-02** in full, including the
  degraded contracts: an artifact that cannot express an enhancement
  retains its form and links a derived enhancement with its portability
  cost; an upgrade touching keyed meaning halts for explicit assessment
  review.
- **16C-RESEARCH.md Open Question 6's recommendation**: both halves, split
  by authority; code in `upgrade_audit.py`, playbook in the skill, the
  skill referencing the shipped functions rather than restating rules.
- **Shipped change detectors**: `model.content_fingerprint` (model.py:1451)
  and `model._key_content_hash` (model.py:1532); the D-14A-2 carve-out the
  16C-01 precondition confirmed.
- **16C-UI-SPEC.md Legacy-Upgrade Review Surface Contract and Copywriting
  Contract**: every string transcribed below, verbatim.

Purpose: legacy artifacts can be improved without ever silently changing
what they test.
Output: one audit module, one legacy fixture, one green test, one usable
skill.
</objective>

<context>
@.planning/phases/16C-strategies-notes-prototype-convergence/16C-DECISIONS.md
@.planning/phases/16C-strategies-notes-prototype-convergence/16C-UI-SPEC.md
@.planning/phases/16C-strategies-notes-prototype-convergence/16C-RESEARCH.md
@.planning/REQUIREMENTS.md
@model.py
@note_outputs.py
@surfaces/migrate.py
@.agents/skills/legacy-upgrade/SKILL.md
@fixtures/sample_bank.md
</context>

## Artifacts this phase produces (plan 16C-08 share)

New symbols introduced by this plan, and by nothing earlier:

- `upgrade_audit.py`: `BASELINE_AUDIT_ITEMS`, `PLAN_TEXT_STAND_IN`,
  `AUDIT_HEADING`, `AUDIT_COMPLETION_LINE`, `DIFF_HEADING`,
  `COSMETIC_SKIP_COPY`, `CANNOT_EXPRESS_COPY`, `KEYED_HALT_COPY`,
  `KEYED_HALT_AFFORDANCES`, `baseline_audit`, `bounded_diff`,
  `keyed_meaning_delta`, `run_upgrade`.
- `fixtures/legacy_pre135_bank.md`.
- `tests/legacy_upgrade_roundtrip.py` and its `check_*` functions.
- The updated `legacy-upgrade` SKILL.md pair.

The phase-wide symbol union is repeated in `16C-01-PLAN.md`.

<tasks>

<task type="auto">
  <name>Task 1: the fixture and the eleven-item baseline audit</name>
  <files>fixtures/legacy_pre135_bank.md, upgrade_audit.py, tests/legacy_upgrade_roundtrip.py</files>
  <read_first>
- `16C-UI-SPEC.md`, Legacy-Upgrade Review Surface Contract item 1 and the
  Copywriting Contract rows for the audit heading, completion line, and
  stand-in cell.
- `fixtures/sample_bank.md`, the shipped bank shape; the legacy fixture is
  a reduced version of it.
- `model.py`: `load`, `parse_lesson`, `lint`, `content_fingerprint`.
- `surfaces/migrate.py` lines 1 to 46: read-legacy-read-only and
  dry-run-by-default, the posture this module copies.
  </read_first>
  <action>
1. Create `fixtures/legacy_pre135_bank.md`: a synthetic pre-13.5 lesson
   artifact with invented content: a title naming it fictional, a
   `## LESSON` section with three headings of plain prose (no 13.5-era
   callouts, no `[[term]]` refs, no `## TERMS` section), and two `mc`
   items with `[ID:]` lines and invented stems. Every string is invented;
   no em dashes; the file must parse (`model.load` returns 2 items) and is
   guard-exempt by living under `fixtures/`.

2. Create `upgrade_audit.py` at the repository root, importing `model` and
   the standard library only (no `runtime`, no `evidence`, no `surfaces`
   imports; it reads legacy artifacts read-only and mutates nothing, the
   migrate.py posture, stated in the docstring). Define, transcribed
   verbatim from the UI-SPEC:

```
BASELINE_AUDIT_ITEMS = ("current_parse", "identity", "fingerprint",
                        "objectives", "sources", "rights", "media",
                        "assessment_boundaries", "plain_rendering",
                        "rich_rendering", "validation")
PLAN_TEXT_STAND_IN = "plan-text stand-in"
AUDIT_HEADING = "Baseline audit"
AUDIT_COMPLETION_LINE = "All 11 baseline checks recorded."
```

3. Define `baseline_audit(bank_path, available=None)`:
   - `available` is a mapping from audit item to a boolean saying whether
     its backing record exists (default: `rights`, `sources`, and `media`
     False, everything else True; the docstring cites D12 and Assumption
     A11: an unavailable row reads the stand-in, never an invented pass).
   - Returns a list of exactly eleven `{"item": ..., "result": ...}` rows
     in `BASELINE_AUDIT_ITEMS` order:
     - `current_parse`: item count and heading count from `model.load` and
       `model.parse_lesson`.
     - `identity`: the sorted `[ID:]` values found.
     - `fingerprint`: `model.content_fingerprint` per item, joined.
     - `objectives`: the objective strings found (may be empty; report the
       count honestly).
     - `sources`, `rights`, `media`: `PLAN_TEXT_STAND_IN` when unavailable.
     - `assessment_boundaries`: the count of keyed structures (items with
       `correct` sets).
     - `plain_rendering`: whether the raw Markdown is non-empty coherent
       text (length and first heading).
     - `rich_rendering`: whether `parse_lesson` returned headings the
       reader can render.
     - `validation`: the `model.lint` error and warning counts.
   - Pure and read-only: it opens the bank for reading and writes nothing.

4. Create `tests/legacy_upgrade_roundtrip.py` in the shipped shape with a
   local `fail(msg)`. First checks:
   - `check_fixture_parses`: the legacy fixture loads with 2 items and 3
     headings and `python itembank.py guard .` stays green (subprocess).
   - `check_audit_first_and_complete`: `baseline_audit` returns exactly
     eleven rows in the locked order; the `rights` row reads exactly
     `plan-text stand-in`; no row is empty; the completion line constant
     equals the UI-SPEC string verbatim.
   - `main()` prints `LEGACY UPGRADE: 2 passed, 0 failed`.

5. Run:

```
python tests/legacy_upgrade_roundtrip.py
python itembank.py guard .
```

   Expected: `LEGACY UPGRADE: 2 passed, 0 failed`, exit 0; `0 offending
   files`.

   No em dash characters in any file this task writes.
  </action>
  <verify>
  <automated>python tests/legacy_upgrade_roundtrip.py && python itembank.py guard .</automated>
Expected: `LEGACY UPGRADE: 2 passed, 0 failed` then `0 offending files`.
The degraded state this task proves is the honest audit row: an unavailable
backing record reads the stand-in sentence, never an invented pass.
  </verify>
  <acceptance_criteria>
- The fixture parses with 2 items and 3 headings; guard stays green.
- `baseline_audit` returns eleven rows in the locked order with the
  stand-in for unavailable records.
- `upgrade_audit.py` writes no file, asserted via ast (no `open(` with a
  write mode).
- No file this task writes contains an em dash character, verified with the
  `chr(0x2014)` form.
  </acceptance_criteria>
  <reversibility rating="reversible">A read-only audit over a fixture.</reversibility>
  <done>The eleven-item audit runs first, completely, and honestly over a
  synthetic legacy artifact.</done>
</task>

<task type="auto">
  <name>Task 2: the bounded diff, cosmetic rejection, and the cannot-express link</name>
  <files>upgrade_audit.py, tests/legacy_upgrade_roundtrip.py</files>
  <read_first>
- `16C-UI-SPEC.md`, Legacy-Upgrade Review Surface Contract items 2, 3, 4,
  and 6, and the Copywriting Contract rows for the diff heading, cosmetic
  skip, and cannot-express state.
- `16C-DECISIONS.md` `## D12`.
- `note_outputs.py` `render_mode`, the derived-enhancement form the
  cannot-express path links.
  </read_first>
  <action>
1. Add to `upgrade_audit.py`, transcribed verbatim:

```
DIFF_HEADING = "Proposed changes ({N})"
COSMETIC_SKIP_COPY = "Skipped: no learning value added."
CANNOT_EXPRESS_COPY = "This artifact can't express {enhancement} in its own form. It keeps its form; a derived enhancement is linked, with its portability cost stated."
```

2. Define `bounded_diff(bank_path, proposed_changes)`:
   - `proposed_changes` is a list of dicts each carrying `before`, `after`,
     and `reason` (a stated learning-value reason string).
   - A change whose `reason` is empty or reads exactly `"cosmetic"` is
     returned in a `skipped` list with `COSMETIC_SKIP_COPY`, never in the
     proposed list (UPGRADE-01: cosmetic novelty rejected).
   - Returns `{"heading": DIFF_HEADING with {N} replaced by the proposed
     count, "proposed": [...], "skipped": [...]}`; every proposed entry
     keeps before, after, and reason together (never a diff without its
     reason).
   - The function proposes; it never writes. Mutation stays with the 14A
     journal operations, named in the docstring as the write path this
     module does not own.

3. Define `cannot_express(bank_path, enhancement_name, instance,
   headings)`: renders the enhancement as a derived trio projection via
   `note_outputs.render_mode` (the concept map for a structure enhancement)
   and returns `{"copy": CANNOT_EXPRESS_COPY with {enhancement}
   substituted, "derived": <the projection text>, "portability_cost":
   <one sentence naming that the derived form lives beside, not inside, the
   artifact and does not travel with the original file>}`. The original
   artifact is never mutated.

4. Extend `tests/legacy_upgrade_roundtrip.py`:
   - `check_bounded_diff`: three proposed changes (one with a real
     learning-value reason, one with reason `"cosmetic"`, one with an empty
     reason) yield a proposed list of one and a skipped list of two, each
     skipped entry carrying the exact sentence; the heading reads
     `Proposed changes (1)`.
   - `check_cannot_express`: the legacy fixture (which has no terms and no
     relations) cannot express a concept map; the cannot-express result
     carries the exact sentence with `{enhancement}` substituted, a
     non-empty derived text, a non-empty portability cost, and the fixture
     file's bytes are unchanged (hash before and after).
   - `check_identity_preserved`: run `bounded_diff` and `cannot_express`
     and assert the fixture's `[ID:]` lines are byte-identical before and
     after (stable identity preserved).
   - Update `main()` to run five checks and print
     `LEGACY UPGRADE: 5 passed, 0 failed`.

5. Run:

```
python tests/legacy_upgrade_roundtrip.py
```

   Expected: `LEGACY UPGRADE: 5 passed, 0 failed`, exit 0.

   No em dash characters in any file this task writes.
  </action>
  <verify>
  <automated>python tests/legacy_upgrade_roundtrip.py</automated>
Expected: final line `LEGACY UPGRADE: 5 passed, 0 failed`, exit 0. The
degraded state this task proves is the cannot-express path: an artifact
that cannot carry an enhancement keeps its form untouched while a derived
projection is linked with its portability cost stated.
  </verify>
  <acceptance_criteria>
- `python tests/legacy_upgrade_roundtrip.py` exits 0 with final line
  `LEGACY UPGRADE: 5 passed, 0 failed`.
- Cosmetic and reasonless changes are skipped with the exact sentence and
  never proposed.
- The cannot-express result carries the exact sentence, a derived
  projection, and a stated portability cost, with the original bytes
  unchanged.
- No file this task writes contains an em dash character, verified with the
  `chr(0x2014)` form.
  </acceptance_criteria>
  <reversibility rating="reversible">Propose-only functions; nothing
  mutates.</reversibility>
  <done>Upgrades are bounded, reasoned, cosmetic-free proposals, and an
  inexpressible enhancement lands beside the artifact, never inside it.</done>
</task>

<task type="auto">
  <name>Task 3: the keyed-meaning halt and the usable skill</name>
  <files>upgrade_audit.py, tests/legacy_upgrade_roundtrip.py, .agents/skills/legacy-upgrade/SKILL.md, .claude/skills/legacy-upgrade/SKILL.md</files>
  <read_first>
- `16C-UI-SPEC.md`, Legacy-Upgrade Review Surface Contract item 5, and the
  Copywriting Contract keyed-meaning halt row.
- `model.py` `content_fingerprint` (line 1451) and `_key_content_hash`
  (line 1532), the shipped detectors this task composes.
- `.agents/skills/legacy-upgrade/SKILL.md`, the stub as it stands.
- `.github/workflows/ci.yml`, the "Skill mirrors stay identical" step.
  </read_first>
  <action>
1. Add to `upgrade_audit.py`, transcribed verbatim:

```
KEYED_HALT_COPY = "Halted: this change would alter keyed assessment meaning ({what}). Assessment changes are reviewed separately and are never part of an upgrade."
KEYED_HALT_AFFORDANCES = ("Open assessment review", "Cancel upgrade")
```

2. Define `keyed_meaning_delta(before_qs, after_qs)`:
   - Pairs items by id and compares, per pair: `model.content_fingerprint`
     (any delta names `keyed content`), the `difficulty` field (delta names
     `difficulty`), and the `objective` field (delta names
     `objective alignment`).
   - Returns a list of `{"item_id": ..., "what": ...}` deltas; empty when
     nothing keyed moved.

3. Define `run_upgrade(bank_path, proposed_changes, available=None)`:
   - Step 1: `baseline_audit` runs first, always; its rows ride in the
     result. A diff requested before the audit is structurally impossible:
     there is no public function that diffs without auditing.
   - Step 2: apply `proposed_changes` to an in-memory copy only, parse both
     versions, and run `keyed_meaning_delta`.
   - Step 3: on any delta, return `{"halted": True, "copy": KEYED_HALT_COPY
     with {what} substituted by the comma-joined delta names,
     "affordances": KEYED_HALT_AFFORDANCES, "audit": rows}` and nothing
     else: no diff, no proposal list, no override field exists on the
     halted result (D12: the halt is the contract, not a warning).
   - Step 4: with no delta, return `{"halted": False, "audit": rows,
     "diff": bounded_diff(...)}`. The function still writes nothing.

4. Extend `tests/legacy_upgrade_roundtrip.py`:
   - `check_keyed_halt` (the UPGRADE-02 fixture): a scripted change to the
     legacy fixture's first item flipping its `CORRECT:` letter yields
     `halted` True, copy exactly
     `Halted: this change would alter keyed assessment meaning (keyed content). Assessment changes are reviewed separately and are never part of an upgrade.`,
     affordances exactly the two strings, no `diff` key on the result, and
     the fixture file's bytes unchanged.
   - `check_prose_change_passes`: a lesson-prose-only change (reworded
     sentence in a heading body with a stated reason) yields `halted`
     False with the audit rows present and the diff proposing one change:
     keyed meaning is compared through the fingerprints, which exclude
     rationale and prose.
   - Update `main()` to run seven checks and print
     `LEGACY UPGRADE: 7 passed, 0 failed`.

5. Update both skill mirrors, byte-identically:
   `.agents/skills/legacy-upgrade/SKILL.md` and
   `.claude/skills/legacy-upgrade/SKILL.md`. Frontmatter `description`
   drops the stub sentence and reads:
   `"Upgrade legacy lessons and question artifacts safely: run the eleven-item baseline audit, propose a bounded reviewable diff, reject cosmetic novelty, link derived enhancements the artifact cannot express, and halt on any keyed-meaning change (upgrade_audit.py, Phase 16C)."`
   Body: keep the provenance line, replace the stub notice with a short
   usage playbook that references the shipped functions by name
   (`upgrade_audit.baseline_audit`, `upgrade_audit.run_upgrade`,
   `upgrade_audit.keyed_meaning_delta`, the halt copy constant) and states:
   audit before editing, present the bounded diff for human review, never
   apply a change yourself (mutation goes through the 14A journal
   operations under the operation contract), and a keyed-meaning halt ends
   the upgrade with only the two affordances. State that rights, sources,
   and media rows read `plan-text stand-in` until their records ship. No em
   dashes. Verify the mirror:

```
diff -rq .agents/skills .claude/skills
```

   Expected: no output, exit 0.

6. Run:

```
python tests/legacy_upgrade_roundtrip.py
python itembank.py guard .
diff -rq .agents/skills .claude/skills
```

   Expected: `LEGACY UPGRADE: 7 passed, 0 failed`, exit 0; `0 offending
   files`; no diff output, exit 0.
  </action>
  <verify>
  <automated>python tests/legacy_upgrade_roundtrip.py && diff -rq .agents/skills .claude/skills</automated>
Expected: `LEGACY UPGRADE: 7 passed, 0 failed`, exit 0, and an empty diff.
The degraded state this task proves is the halt: a keyed change ends the
upgrade with the locked sentence, two affordances, no diff, no override,
and untouched bytes.
  </verify>
  <acceptance_criteria>
- `python tests/legacy_upgrade_roundtrip.py` exits 0 with final line
  `LEGACY UPGRADE: 7 passed, 0 failed`.
- The keyed halt carries the exact sentence and exactly two affordances,
  with no diff key and no override field on the halted result.
- A prose-only change passes with the audit rows present.
- Both SKILL.md mirrors are byte-identical and reference the shipped
  function names.
- No file this task writes contains an em dash character, verified with the
  `chr(0x2014)` form.
  </acceptance_criteria>
  <reversibility rating="reversible">Propose-and-halt logic plus skill
  text; nothing durable mutates.</reversibility>
  <done>An upgrade can never silently change what an item tests, and the
  skill that drives upgrades points at the code that enforces it.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| upgrade diff to keyed content | The diff is where a keyed change would smuggle past review; the fingerprint comparison guards it. |
| audit claim to reality | An invented pass for an unavailable record would launder unknowns into assurances. |
| skill prose to code behavior | A skill that restates rules drifts; referencing functions keeps one truth. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-16C-08-01 | Tampering | an upgrade diff smuggling a keyed change past review | critical | mitigate | keyed_meaning_delta composes content_fingerprint plus the difficulty and objective fields; any delta halts with no diff, no override, and untouched bytes, asserted by hash comparison. |
| T-16C-08-02 | Repudiation | an unavailable audit record reported as a pass | high | mitigate | The stand-in sentence is the locked result for unavailable rows and the test asserts it verbatim. |
| T-16C-08-03 | Tampering | the upgrade module mutating artifacts directly | high | mitigate | Every function proposes over in-memory copies; the ast scan asserts no write-mode open; mutation is named as the 14A journal's. |
| T-16C-08-04 | Spoofing | cosmetic novelty riding in as improvement | medium | mitigate | Empty and cosmetic reasons route to the skipped list with the locked sentence, never to the proposed list. |
| T-16C-08-05 | Tampering | skill mirrors drifting | medium | mitigate | Both files are written byte-identically and `diff -rq` runs in the verify plus CI. |
| T-16C-08-06 | Tampering | supply chain: a third-party dependency introduced by this plan | high | mitigate | None is added; stdlib only. Per PLANNING-DIRECTIVES section 4a, any future dependency is vendored at a pinned version with a recorded checksum and a named license review. |
</threat_model>

<out_of_scope>
Refused by this plan, by name:

- No mutation path: applying an accepted upgrade goes through the 14A
  journal operations (link, import, copy, move, edit-in-place, supersede)
  under the operation contract; this plan proposes and halts only.
- No review UI, route, or CLI command; the surface contract is 16C-UI-SPEC
  D12's and renders at 17A.
- No difficulty recalibration, no objective remapping, no key correction:
  every one of those is a separate reviewed assessment revision.
- No rights, sources, or media records: their audit rows read the stand-in
  until their owning phases ship them.
- No second hash scheme and no fingerprint normalization change.
</out_of_scope>

<flagged_assumptions>
- **The default availability map (rights, sources, media unavailable) is
  this plan's honest reading of what exists at 16C time.** If 14B or 15A
  shipped usable records by execution time (the 16C-01 precondition's
  Deviations section will say), the executor flips those defaults to True,
  audits them for real, and records the deviation.
- **`_key_content_hash` targets KEY blocks; the legacy fixture carries
  none**, so the keyed comparison rides on content_fingerprint and the two
  named fields; a KEY-block legacy case joins the fixture set when a real
  pre-13.5 artifact with KEY blocks exists.
- **The skill update keeps the "command surface has not shipped" reality
  honest**: the playbook names Python functions, not CLI commands, because
  no upgrade CLI exists; adding one is future work under the Surfaces
  constraint.
</flagged_assumptions>

<summary_obligations>
`16C-08-SUMMARY.md` records: the final line of every verify command with
actual stdout; the eleven audit rows as produced over the fixture; the
bounded-diff result (proposed and skipped counts with sentences); the
cannot-express result with its portability cost sentence; the keyed-halt
result quoted in full with the before and after hashes proving untouched
bytes; the mirror diff result; and any deviation from this plan with its
reason.
</summary_obligations>

<output>
Create
`.planning/phases/16C-strategies-notes-prototype-convergence/16C-08-SUMMARY.md`
when done.
</output>
