---
phase: 16B-ia-modes-recovery-contract
plan: 06
type: execute
wave: 6
depends_on: ["16B-05"]
files_modified:
  - schemas/settings.schema.json
  - surfaces/settings.py
  - tests/config_roundtrip.py
  - .planning/phases/16B-ia-modes-recovery-contract/16B-DECISIONS.md
autonomous: true
requirements: [APP-03]
estimate:
  tokens: 70000
  raw_tokens: 70000
  tasks: 3
  confidence: low
must_haves:
  truths:
    - "Settings expose approved roots, model backends, network and egress policy, accessibility, theme, storage, backups, and update policy: the shipped DEL-04 subset grows to that list by adding exactly four additive top-level keys (approved_roots, network_egress, accessibility, storage) beside the unchanged model_backend, theme, and update_policy (APP-03 clause C137)."
    - "The growth is provably additive rather than promised: a settings file written before this phase, carrying none of the four new keys, loads and validates exactly as it does today, asserted by comparing every pre-existing key of the merged document against the baseline recorded in 16B-PRECONDITION.md before any 16B change existed (non-negotiable number 4)."
    - "A settings file missing any or all of the four new keys is the default case and not an error: merge_over_defaults fills each from the schema and validation passes, so partial input is the normal input (SettingsPanel partial consideration)."
    - "Unknown or unset values stay restrictive and display as unset, with no invented default: approved_roots defaults to the empty list, network_egress.hosted_operations defaults to off, storage.backups_enabled defaults to false, and no default names a real path (APP-03 boundary edge, SettingsPanel empty consideration)."
    - "An invalid value in any of the four new groups is rejected with one of the six existing dotted settings codes, reusing the shipped classifier rather than adding a seventh code or a second validator (SettingsPanel error consideration)."
    - "There is exactly one settings file and exactly one validator: no second settings document is created, schema_validate.validate remains the only checker, and surfaces/settings.py gains no hand-rolled type, range, or enum check."
    - "The four new keys are declared and displayed but nothing gates on them in this phase: settings.THIS_PHASE is unchanged at 10, so each new key reports as declared rather than as read, and no 16B code path branches on approved_roots, network_egress, accessibility, or storage."
    - "An unrecognized top-level key still round-trips untouched, because load_settings validates one known key at a time and deliberately does not enforce the schema's top-level additionalProperties, and the four additions do not change that."
    - statement: "A slow settings read renders a stated loading state; today the read is synchronous, so no loading state is reachable, and asserting that by construction needs a held-out timing test."
      verification: backstop
    - statement: "Many approved roots in one group scroll or collapse rather than clipping; which of the two is a Phase 17A rendering decision confirmed by a held-out visual test."
      verification: backstop
    - statement: "A long root path wraps at a point that keeps its drive or root visible and is never hidden behind a mid-path ellipsis; the exact wrap treatment is confirmed at Phase 17A rather than asserted here."
      verification: backstop
  prohibitions:
    - statement: "A settings file written before this phase must not become invalid, and no pre-existing key's effective value may change; a format addition that breaks an existing file is not additive whatever it is called."
      status: kept
      verification: flagged-unverified
    - statement: "A second settings file or a second validator must not be created; one contract, one document, one checker."
      status: kept
      verification: flagged-unverified
    - statement: "An unknown or unset rights, root, or egress value must not be treated as permissive; unknown stays restrictive, and a default must never name a real filesystem path the learner did not choose."
      status: kept
      verification: flagged-unverified
    - statement: "A settings toggle must not be presented for a value nothing enforces without saying so; declaring a preference the runtime ignores, and implying it takes effect, is a false statement about authority."
      status: kept
      verification: flagged-unverified
  artifacts:
    - "schemas/settings.schema.json gains the top-level properties approved_roots, network_egress, accessibility, and storage, with its required array unchanged"
    - "surfaces/settings.py gains NETWORK_EGRESS_SETTINGS_DEFAULTS, ACCESSIBILITY_SETTINGS_DEFAULTS, and STORAGE_SETTINGS_DEFAULTS"
    - "tests/config_roundtrip.py gains check_16b_groups_additive, check_16b_defaults_are_restrictive, and check_16b_invalid_values_are_coded"
    - "16B-DECISIONS.md gains the dated D-16B-11 phase-marker rule"
  key_links:
    - "The four keys must NOT join the schema's top-level required array. load_settings merges over defaults before validating, so required would appear to pass, but cmd_config's whole-document paths and any future strict validation would then reject a hand-written file that predates the keys. The shipped update and audio keys are already in properties and not in required, and that is the precedent being followed."
    - "The additivity proof has to compare against 16B-PRECONDITION.md's recorded baseline rather than against a value computed in the same run. A hash taken after the edit and compared to itself proves nothing, which is why plan 16B-01 ran before any file outside .planning was touched."
    - "x-itembank-phase must be 16.2 rather than 10 or 16, and THIS_PHASE must stay 10, or the four keys would report as read by a phase that does not read them. The float ordering is what lets a subphase sit strictly between 16 and 17, which is what the shipped comment above THIS_PHASE describes."
    - "network_egress.hosted_operations is a three-value enum rather than a boolean because off, ask, and on are three genuinely different postures and a boolean would force ask to be encoded somewhere else later, which is how a second policy vocabulary starts."
---

<objective>
Grow the shipped settings subset to the list APP-03 names, additively, and prove
the addition did not move anything that already existed.

`REQUIREMENTS.md` APP-03 states that "Settings expose approved roots, model
backends, network and egress policy, accessibility, theme, storage, backups, and
update policy; the shipped DEL-04 subset grows to this list at 16B (lands clause
C137, 2026-08-14)". Three of the eight already ship as `model_backend`, `theme`,
and `update_policy`. This plan adds the other five as four keys, with backups
living inside `storage`.

The load-bearing half is the proof, not the addition. Non-negotiable number 4
requires format changes to be additive "proven by a byte-identical fixture, not
promised", and plan 16B-01 recorded the pre-phase baseline before any file
outside `.planning/` was touched precisely so this plan could compare rather than
claim.

Nothing in this phase gates on the four new values. They are declared and
displayed; enforcement is deferred by name, exactly as Phase 16A's `D-16A-8`
deferred media-rights enforcement rather than inventing a mechanism against a
vocabulary it did not own.

Decisions already made, cited, and never re-derived here:

- **`16B-DECISIONS.md` `## D-16B-4`**: exactly four new top-level keys,
  `approved_roots`, `network_egress`, `accessibility`, and `storage`; backups
  are properties inside `storage` and not a fifth key; none of the four joins
  the schema's top-level `required` array, matching the shipped `update` and
  `audio` keys.
- **`16B-UI-SPEC.md` "Settings Expansion Contract"**, the whole table, including
  each group's exact Chrome-voice panel label.
- **`16B-PATTERNS.md`**, the `schemas/settings.schema.json` and
  `surfaces/settings.py` pattern assignments: extend the shipped file rather
  than fork it, stay inside `schema_validate.py`'s closed keyword set, keep
  `additionalProperties: false` on every new object group, and add one
  `..._SETTINGS_DEFAULTS` accessor per group rather than one catch-all dict.
- **`surfaces/settings.py`'s module docstring**, quoted: "There is exactly one
  validator here, `schema_validate.validate()`". No 16B code hand-rolls a second
  type, range, or enum check.
- **`PLANNING-DIRECTIVES.md` section 4**, non-negotiable number 4, and section
  4a's clarification that additive growth is permitted and is section 4.4's
  subject.

One decision this plan locks and Task 1 appends to `16B-DECISIONS.md` as
`## D-16B-11. The subphase marker on new settings keys`:

Every new top-level key added by this phase carries `"x-itembank-phase": 16.2`,
and `settings.THIS_PHASE` stays at `10`, unchanged. The rationale is that the
shipped comment above `THIS_PHASE` describes the float precisely: "a sub-phase
(2.1) can sit strictly between its parent (2) and the next whole phase (3)
without renumbering anything". Phase 16A is 16.1, 16B is 16.2, 16C is 16.3. A
key marked 16.2 while `THIS_PHASE` is 10 reports as declared rather than as
read, which is the honest state of a key nothing gates on yet.

Purpose: give the settings surface the eight groups APP-03 names, without
moving a single existing value.
Output: four schema keys, three defaults accessors, three tests, and one
recorded additivity comparison.
</objective>

<context>
@.planning/phases/16B-ia-modes-recovery-contract/16B-DECISIONS.md
@.planning/phases/16B-ia-modes-recovery-contract/16B-PRECONDITION.md
@.planning/phases/16B-ia-modes-recovery-contract/16B-UI-SPEC.md
@.planning/phases/16B-ia-modes-recovery-contract/16B-PATTERNS.md
@.planning/REQUIREMENTS.md
@.planning/PLANNING-DIRECTIVES.md
@schemas/settings.schema.json
@surfaces/settings.py
@schema_validate.py
@tests/config_roundtrip.py
</context>

## Artifacts this phase produces (plan 16B-06 share)

New symbols introduced by this plan, and by nothing earlier:

- `schemas/settings.schema.json`: the top-level properties `approved_roots`,
  `network_egress`, `accessibility`, `storage`, and the nested property names
  `hosted_operations`, `last_disclosure`, `reduced_motion`, `high_contrast`,
  `data_dir`, `backups_enabled`, `backup_dir`.
- `surfaces/settings.py`: `NETWORK_EGRESS_SETTINGS_DEFAULTS`,
  `ACCESSIBILITY_SETTINGS_DEFAULTS`, `STORAGE_SETTINGS_DEFAULTS`.
- `tests/config_roundtrip.py`: `check_16b_groups_additive`,
  `check_16b_defaults_are_restrictive`, `check_16b_invalid_values_are_coded`.
- `16B-DECISIONS.md`: the heading `## D-16B-11. The subphase marker on new
  settings keys`.

The phase-wide symbol union is repeated in `16B-01-PLAN.md`.

<tasks>

<task type="auto">
  <name>Task 1: the four additive schema keys</name>
  <files>schemas/settings.schema.json, .planning/phases/16B-ia-modes-recovery-contract/16B-DECISIONS.md</files>
  <read_first>
- `schemas/settings.schema.json` in full, in particular its top-level
  `additionalProperties`, its `required` array, and the `reader` and `style`
  property groups as the exact shape a new object group copies.
- `schema_validate.py` lines 27 to 38, the `SUPPORTED` and `ANNOTATIONS` frozen
  sets. Every keyword written below must be a member of one of them; `default`,
  `description`, and `x-itembank-phase` are annotations and are permitted.
- `surfaces/settings.py` lines 26 to 32, `THIS_PHASE` and the comment above it
  explaining the float, which D-16B-11 quotes.
- `.planning/phases/16B-ia-modes-recovery-contract/16B-DECISIONS.md`,
  `## D-16B-4`.
- `.planning/phases/16B-ia-modes-recovery-contract/16B-UI-SPEC.md`, the Settings
  Expansion Contract table.
  </read_first>
  <action>
1. Add exactly four new entries to `schemas/settings.schema.json`'s top-level
   `properties` object, appended after `subject_profiles` so the file's existing
   key order is otherwise untouched. Do **not** modify the top-level `required`
   array, `additionalProperties`, `$schema`, `$id`, `title`, `description`, or
   `x-itembank-version`.

   `approved_roots`:
   - `type` `array`
   - `description`
     `Source, vault, bank, and note directory roots this install may read (the declare-read-roots step of Loop A). Declared by this phase (16.2); no code path gates on it yet.`
   - `items` an object with `type` `string` and `minLength` `1`
   - `uniqueItems` `true`
   - `default` `[]`
   - `x-itembank-phase` `16.2`

   `network_egress`:
   - `type` `object`, `additionalProperties` `false`
   - `description`
     `Whether hosted operations are permitted, and a read-only record of what was last sent. Declared by this phase (16.2); no code path gates on it yet.`
   - `required` `["hosted_operations", "last_disclosure"]`
   - `properties`: `hosted_operations` with `type` `string`, `enum`
     `["off", "ask", "on"]`, `default` `"off"`; `last_disclosure` with `type`
     `string`, `default` `""`
   - `default` `{"hosted_operations": "off", "last_disclosure": ""}`
   - `x-itembank-phase` `16.2`

   `accessibility`:
   - `type` `object`, `additionalProperties` `false`
   - `description`
     `Learner-controlled accommodation preferences (the accommodation-override layer of the mode-layer contract). Declared by this phase (16.2); no code path gates on it yet.`
   - `required` `["reduced_motion", "high_contrast"]`
   - `properties`: `reduced_motion` and `high_contrast`, each with `type`
     `string`, `enum` `["system", "on", "off"]`, `default` `"system"`
   - `default` `{"reduced_motion": "system", "high_contrast": "system"}`
   - `x-itembank-phase` `16.2`

   `storage`:
   - `type` `object`, `additionalProperties` `false`
   - `description`
     `Where evidence and course data live on disk, and the backup and export controls of Loop G. Declared by this phase (16.2); no code path gates on it yet.`
   - `required` `["data_dir", "backups_enabled", "backup_dir"]`
   - `properties`: `data_dir` with `type` `string` and `default` `""`;
     `backups_enabled` with `type` `boolean` and `default` `false`;
     `backup_dir` with `type` `string` and `default` `""`
   - `default` `{"data_dir": "", "backups_enabled": false, "backup_dir": ""}`
   - `x-itembank-phase` `16.2`

   Every default above is the restrictive value: no root is approved, hosted
   operations are off, nothing was disclosed, both accommodations follow the
   system, backups are off, and neither directory names a real path. Write a
   `description` sentence on each of the three object groups saying so is
   deliberate.

2. Append `## D-16B-11. The subphase marker on new settings keys` to
   `16B-DECISIONS.md`, carrying the locked answer and the rationale from this
   plan's objective verbatim, under today's date.

3. Verify the schema itself before touching any settings file. Run:

```
python -c "import json, schema_validate as sv; s=json.load(open('schemas/settings.schema.json')); sv.check_schema(s); print('schema ok', len(s['properties']), len(s['required']), s['additionalProperties'])"
```

   Expected stdout exactly: `schema ok 24 18 False`.

   A `SchemaError` here means a keyword outside `SUPPORTED` and `ANNOTATIONS`
   was written; fix the keyword rather than widening the validator.

4. Confirm the four keys are absent from `required` and that no existing
   property changed. Run:

```
python -c "import json; s=json.load(open('schemas/settings.schema.json')); new={'approved_roots','network_egress','accessibility','storage'}; print(sorted(new & set(s['required'])), sorted(new - set(s['properties'])))"
```

   Expected stdout exactly: `[] []`.

   No em dash characters in any file this task writes.
  </action>
  <verify>
  <automated>python -c "import json, schema_validate as sv; s=json.load(open('schemas/settings.schema.json')); sv.check_schema(s); new={'approved_roots','network_egress','accessibility','storage'}; assert len(s['properties'])==24; assert len(s['required'])==18; assert s['additionalProperties'] is False; assert not (new & set(s['required'])); assert not (new - set(s['properties'])); assert s['properties']['approved_roots']['default']==[]; assert s['properties']['network_egress']['default']['hosted_operations']=='off'; assert s['properties']['storage']['default']['backups_enabled'] is False; assert all(s['properties'][k]['x-itembank-phase']==16.2 for k in new); print('16B settings schema ok')"</automated>
Expected: prints `16B settings schema ok` and exits 0. The degraded state this
task proves is the restrictive-default rule: every one of the four defaults is
the closed, unset, off value, and none names a real path.
  </verify>
  <acceptance_criteria>
- `schema_validate.check_schema` on the whole document raises nothing.
- `len(properties)` is `24`, `len(required)` is `18`, and
  `additionalProperties` is `False`, all unchanged except the property count.
- None of the four new keys appears in `required`.
- `approved_roots` default is `[]`; `network_egress.hosted_operations` default
  is `"off"`; `accessibility.reduced_motion` and `high_contrast` defaults are
  `"system"`; `storage.backups_enabled` default is `false`; `storage.data_dir`
  and `storage.backup_dir` defaults are the empty string.
- Every one of the four carries `"x-itembank-phase": 16.2`.
- `surfaces/settings.py`'s `THIS_PHASE` is still `10`, asserted with a one-line
  `python -c`.
- `16B-DECISIONS.md` contains the literal heading
  `## D-16B-11. The subphase marker on new settings keys`.
- `git diff --stat schemas/settings.schema.json` shows insertions and zero
  deletions, recorded verbatim in the summary; any deletion means an existing
  line was rewritten and must be restored.
- No file this task writes contains an em dash character, verified with the
  `chr(0x2014)` form.
  </acceptance_criteria>
  <reversibility rating="costly">`schemas/settings.schema.json` is a published
  contract: `itembank config` prints it, `itembank schema` publishes it, and any
  external install validates against it. Renaming a key after a settings file
  carries it is a migration across every install rather than an edit. That
  one-way door was confirmed before this task rather than by it: the exact key
  set was settled by the checker-approved UI-SPEC's Settings Expansion Contract
  on 2026-08-15 and by `16B-DECISIONS.md` D-16B-4, transcribed by plan 16B-01
  Task 1 in the same plan as its blocking checkpoint. This task transcribes, and
  the additions are `properties`-only with `required` untouched, so a pre-phase
  file is unaffected either way.</reversibility>
  <done>Four groups exist in the one settings contract, every default is
  restrictive, and nothing that already existed moved.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: the three defaults accessors and the additivity proof</name>
  <files>surfaces/settings.py, tests/config_roundtrip.py</files>
  <behavior>
    - `settings.load_settings(<a directory with no itembank.json>)` returns a
      dict containing all four new keys at their schema defaults.
    - `settings.load_settings(<a directory whose itembank.json predates this
      phase>)` returns, for every key that existed before this phase, exactly
      the value recorded in `16B-PRECONDITION.md`'s baseline.
    - An `itembank.json` carrying only `{"theme": "dark"}` loads without error
      and its `approved_roots` reads as `[]`.
    - An `itembank.json` carrying `{"network_egress": {"hosted_operations":
      "maybe"}}` exits with a message classified as
      `settings.invalid_value`.
    - An `itembank.json` carrying an unrecognized top-level key round-trips that
      key untouched.
  </behavior>
  <read_first>
- `surfaces/settings.py` in full: the module docstring, `SETTINGS_CODES`,
  `STYLE_SETTINGS_DEFAULTS` and `PARAPHRASE_SETTINGS_DEFAULTS` as the accessor
  shape to copy, `defaults_from_schema`, `merge_over_defaults`,
  `load_settings`, and `classify_error`.
- `.planning/phases/16B-ia-modes-recovery-contract/16B-PRECONDITION.md`, the
  Additivity baseline section, all four recorded lines.
- `tests/config_roundtrip.py` in full, for its existing check names, its local
  `fail` helper, and the `test_unknown_key_preserved` behavior `load_settings`'s
  docstring names.
  </read_first>
  <action>
1. Add three module-level accessors to `surfaces/settings.py`, each in the exact
   `..._SETTINGS_DEFAULTS` shape the shipped `STYLE_SETTINGS_DEFAULTS` uses,
   each with a one-paragraph comment above it stating that the schema remains
   the source of truth, that `defaults_from_schema()` mirrors it, and that the
   accessor exists so callers and tests can read the shipped defaults without a
   settings load:

```
NETWORK_EGRESS_SETTINGS_DEFAULTS = {"hosted_operations": "off", "last_disclosure": ""}
ACCESSIBILITY_SETTINGS_DEFAULTS = {"reduced_motion": "system", "high_contrast": "system"}
STORAGE_SETTINGS_DEFAULTS = {"data_dir": "", "backups_enabled": False, "backup_dir": ""}
```

   Add no accessor for `approved_roots`, whose default is the empty list and
   needs no dict. Add no new member to `SETTINGS_CODES`: the existing six
   already cover type, value, range, unknown, missing, and malformed for any new
   key, and adding a seventh would be a new published code for no new failure
   class.

   Add no validation function, no type check, and no range check. The one
   validator stays `schema_validate.validate()`.

2. Add `check_16b_groups_additive()` to `tests/config_roundtrip.py`. It:

   - Reads the four baseline lines out of
     `.planning/phases/16B-ia-modes-recovery-contract/16B-PRECONDITION.md` by
     locating the `## Additivity baseline` heading and parsing the
     `path sha256` lines and the two lines from the effective-document command.
     If that file or that section is missing, `fail` with
     `"16B-PRECONDITION.md's Additivity baseline section is missing; the additivity claim cannot be proven"`
     rather than skipping.
   - Recomputes today's effective settings document with
     `settings.load_settings(<repo root>)`, drops the four new keys from it, and
     asserts the remaining document's key count and its
     `sha256(json.dumps(doc, sort_keys=True))` equal the recorded baseline
     count and hash. A mismatch means a pre-existing key's effective value
     moved, which is the failure the whole plan exists to prevent.
   - Writes a temporary directory containing an `itembank.json` holding exactly
     `{"theme": "dark"}` and asserts `load_settings` on it succeeds, that
     `theme` reads `dark`, and that all four new keys read their defaults.
   - Writes a temporary `itembank.json` carrying an unrecognized top-level key
     `{"not_a_real_group": 1}` alongside `{"theme": "dark"}` and asserts the
     unknown key is preserved on round-trip, so this phase's four additions did
     not change the unknown-key contract `load_settings`'s docstring states.

3. Add `check_16b_defaults_are_restrictive()`. Against a directory with no
   `itembank.json`, assert:
   - `approved_roots` equals `[]`.
   - `network_egress` equals `settings.NETWORK_EGRESS_SETTINGS_DEFAULTS`.
   - `accessibility` equals `settings.ACCESSIBILITY_SETTINGS_DEFAULTS`.
   - `storage` equals `settings.STORAGE_SETTINGS_DEFAULTS`.
   - No value anywhere in those four is a non-empty filesystem path, asserted by
     checking no string value contains `os.sep`.
   - `storage["backups_enabled"]` is exactly `False` and is a `bool`, not a
     truthy integer.

4. Add `check_16b_invalid_values_are_coded()`. For each of these malformed
   documents, assert `load_settings` exits and the exit message begins with one
   of the six existing `SETTINGS_CODES`, and record which code each produced:
   - `{"approved_roots": "not-a-list"}`
   - `{"approved_roots": [""]}`
   - `{"network_egress": {"hosted_operations": "maybe", "last_disclosure": ""}}`
   - `{"network_egress": {"hosted_operations": "off"}}`
   - `{"accessibility": {"reduced_motion": true, "high_contrast": "system"}}`
   - `{"storage": {"data_dir": "", "backups_enabled": "yes", "backup_dir": ""}}`
   - `{"storage": {"data_dir": "", "backups_enabled": false, "backup_dir": "", "extra": 1}}`

   Assert also that `len(settings.SETTINGS_CODES)` is still exactly `6`.

5. Wire all three checks into `tests/config_roundtrip.py`'s existing `main()`
   alongside its current checks, following that file's existing pattern. Run:

```
python tests/config_roundtrip.py
python -c "import sys; sys.path.insert(0,'.'); from surfaces import settings; print(settings.THIS_PHASE, len(settings.SETTINGS_CODES))"
```

   Expected: exit 0, then exactly `10 6`.

   No em dash characters in any file this task writes.
  </action>
  <verify>
  <automated>python tests/config_roundtrip.py</automated>
Expected: exit 0. The degraded state this task proves is the pre-phase settings
file: a document carrying only `{"theme": "dark"}`, and a document carrying an
unrecognized key, both load unchanged with the four new keys filled from
defaults.
  </verify>
  <acceptance_criteria>
- `python tests/config_roundtrip.py` exits 0 with all three new checks running.
- The effective settings document, with the four new keys removed, has the same
  key count and the same sorted-JSON SHA-256 as the baseline recorded in
  `16B-PRECONDITION.md`.
- A directory with no `itembank.json` yields `approved_roots == []`,
  `network_egress == NETWORK_EGRESS_SETTINGS_DEFAULTS`,
  `accessibility == ACCESSIBILITY_SETTINGS_DEFAULTS`, and
  `storage == STORAGE_SETTINGS_DEFAULTS`.
- No default value contains `os.sep`, and `storage["backups_enabled"]` is a
  `bool` equal to `False`.
- All seven malformed documents exit with a message beginning with a member of
  `settings.SETTINGS_CODES`, and each produced code is recorded in the summary.
- `len(settings.SETTINGS_CODES)` is `6` and `settings.THIS_PHASE` is `10`.
- `surfaces/settings.py` gained no function; `git diff surfaces/settings.py`
  shows only the three constant additions and their comments.
- No file this task writes contains an em dash character, verified with the
  `chr(0x2014)` form.
  </acceptance_criteria>
  <reversibility rating="reversible">Three constants and three tests. The
  published surface was set in Task 1.</reversibility>
  <done>The four groups load from defaults, a pre-phase file is unchanged in
  every existing key, and a bad value gets one of the six existing codes.</done>
</task>

<task type="auto">
  <name>Task 3: the settings panel shows the four groups and says what is not enforced</name>
  <files>surfaces/settings.py, tests/config_roundtrip.py</files>
  <read_first>
- `surfaces/settings.py`, `cmd_config` and the `status_text` call around line
  370, which classifies a key by `x-itembank-phase` against `THIS_PHASE`.
- `.planning/phases/16B-ia-modes-recovery-contract/16B-UI-SPEC.md`, the Settings
  Expansion Contract table's four panel labels: `Approved roots`,
  `Network & sharing`, `Accessibility`, `Storage & backups`.
- `tests/config_roundtrip.py` as it stands after Task 2.
  </read_first>
  <action>
1. Confirm, and assert rather than assume, that `cmd_config` already renders
   every top-level key it finds in the schema, so the four new groups appear in
   `itembank config` with no code change. Run:

```
python itembank.py config
```

   and confirm all four key names appear in its output. If they do not, add the
   smallest change to `cmd_config` that lists a schema property it currently
   skips, and record in the summary exactly what was changed and why. Do not
   restructure `cmd_config`.

2. Add the four exact panel labels as a module-level mapping in
   `surfaces/settings.py` so one file owns the label text and a later surface
   reads it rather than restating it:

```
SETTINGS_GROUP_LABELS = {
    "approved_roots": "Approved roots",
    "network_egress": "Network & sharing",
    "accessibility": "Accessibility",
    "storage": "Storage & backups",
    "model_backend": "Model backends",
    "update_policy": "Updates",
}
```

   With a comment stating that the two existing keys are listed for label
   completeness and that neither key's schema, default, or behavior changes.

3. Add one honesty line to the settings surface. Define

```
SETTINGS_DECLARED_NOT_ENFORCED_NOTE = "Declared for a later release. itembank records this preference and nothing acts on it yet."
```

   and require `cmd_config`'s human summary to print it once beside each of the
   four new groups, driven by the group's `x-itembank-phase` being greater than
   `THIS_PHASE` rather than by a hard-coded key list, so the line disappears by
   itself when a later phase raises `THIS_PHASE`. Print it nowhere else.

4. Add `check_16b_groups_labelled_and_flagged()` to `tests/config_roundtrip.py`
   asserting:
   - `python itembank.py config` output contains all four key names and all four
     label strings.
   - It contains `SETTINGS_DECLARED_NOT_ENFORCED_NOTE` exactly four times, once
     per new group.
   - It contains that note zero times for `theme`, `model_backend`, and
     `update_policy`, asserted by checking the note does not appear on those
     three lines.
   - `set(settings.SETTINGS_GROUP_LABELS) - set(schema properties)` is empty, so
     no label names a key that does not exist.

5. Run the full suite and the guard:

```
python tests/config_roundtrip.py
for t in tests/*.py; do python "$t" || exit 1; done
python itembank.py guard .
```

   Expected: exit 0; exit 0; `0 offending files`.

   No em dash characters in any file this task writes.
  </action>
  <verify>
  <automated>python tests/config_roundtrip.py && python itembank.py config</automated>
Expected: exit 0, and the `config` output listing all four new keys with their
four labels and the declared-not-enforced note four times. The degraded state
this task proves is the honesty case: a preference the runtime does not act on
says so on the same screen it is offered, rather than implying an effect.
  </verify>
  <acceptance_criteria>
- `python itembank.py config` output contains `approved_roots`,
  `network_egress`, `accessibility`, and `storage`, and the four labels
  `Approved roots`, `Network & sharing`, `Accessibility`, and
  `Storage & backups`.
- The exact string
  `Declared for a later release. itembank records this preference and nothing acts on it yet.`
  appears exactly four times in that output and appears on no line naming
  `theme`, `model_backend`, or `update_policy`.
- The note is emitted from an `x-itembank-phase` comparison against
  `THIS_PHASE`, not from a hard-coded key list, asserted by reading the source
  for the comparison and by the absence of the four key names in the emitting
  branch.
- `set(settings.SETTINGS_GROUP_LABELS) - set(schema properties)` is empty.
- `for t in tests/*.py; do python "$t" || exit 1; done` exits 0 and
  `python itembank.py guard .` reports `0 offending files`.
- If `cmd_config` needed a change in step 1, the summary records the exact diff
  and the reason.
- No file this task writes contains an em dash character, verified with the
  `chr(0x2014)` form.
  </acceptance_criteria>
  <reversibility rating="reversible">A label map, one note constant, and one
  print branch.</reversibility>
  <done>All eight APP-03 settings groups are visible in one panel, and the four
  that nothing enforces yet say so where they are offered.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| settings file on disk to running process | `itembank.json` is user-editable and hand-editable and its values reach every surface that reads settings. |
| schema to validator | The schema is the only contract; a keyword the validator does not implement would silently impose nothing. |
| declared preference to actual behavior | A displayed toggle implies an effect. |
| new key to pre-existing key | An addition can move an existing effective value without anyone noticing. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-16B-06-01 | Tampering | a pre-phase settings file becoming invalid or changing an effective value | high | mitigate | The four keys are added to `properties` only and never to `required`; `check_16b_groups_additive` compares the effective document minus the four new keys against the SHA-256 recorded in `16B-PRECONDITION.md` before any 16B change existed. |
| T-16B-06-02 | Elevation of Privilege | an unset or unknown egress or roots value read as permissive | high | mitigate | Every default is the restrictive value: no approved root, `hosted_operations` off, nothing disclosed, backups off; `check_16b_defaults_are_restrictive` asserts each and asserts no default contains a path separator. |
| T-16B-06-03 | Tampering | a schema keyword the shipped validator does not implement | high | mitigate | Task 1 step 3 runs `schema_validate.check_schema` over the whole document before any settings file is loaded, and every keyword written is a member of the shipped `SUPPORTED` or `ANNOTATIONS` frozen sets. |
| T-16B-06-04 | Tampering | a second validator or a second settings document | high | mitigate | No validation function is added; `surfaces/settings.py` gains three constants and one label map only, asserted by `git diff` showing no function added, and the one-validator sentence in the module docstring is unchanged. |
| T-16B-06-05 | Repudiation | a preference presented as effective when nothing enforces it | high | mitigate | `SETTINGS_DECLARED_NOT_ENFORCED_NOTE` is printed beside each of the four groups, driven by the `x-itembank-phase` comparison so it disappears on its own when a phase actually reads the key. |
| T-16B-06-06 | Information Disclosure | a default naming a real filesystem path | medium | mitigate | `storage.data_dir` and `storage.backup_dir` default to the empty string and `approved_roots` to the empty list; the check asserts no default string contains `os.sep`. |
| T-16B-06-07 | Denial of Service | a malformed settings file crashing a surface with a traceback | medium | mitigate | `load_settings` already exits with a coded message rather than raising; the seven malformed documents in `check_16b_invalid_values_are_coded` each assert a message beginning with one of the six shipped codes. |
| T-16B-06-08 | Tampering | supply chain: a third-party dependency introduced by this plan | high | mitigate | None is added; the schema is JSON and the module gains constants only. Per `PLANNING-DIRECTIVES.md` section 4a the absence of dependencies is explicitly not the mitigation: the mitigation is that any dependency ever added here is vendored at a pinned version with a recorded checksum and a named license review, following the KaTeX precedent in `09-03-PLAN.md`. |
</threat_model>

<out_of_scope>
Refused by this plan, by name:

- **No enforcement of any of the four new values.** No code path gates on
  `approved_roots`, `network_egress`, `accessibility`, or `storage` in this
  phase. Discovery does not read approved roots, no surface refuses a hosted
  operation, no renderer honors `reduced_motion`, and nothing writes a backup.
  Each is deferred by name to the phase that owns the capability, and the 16B
  freeze record says so.
- No fifth top-level key. Backups live inside `storage` per D-16B-4.
- No new settings code. `SETTINGS_CODES` stays at six members.
- No change to `THIS_PHASE`. Raising it would claim this phase reads keys it
  does not.
- No change to any existing property, default, or the `required` array.
- No second settings file, no per-course settings, no profile layering.
- No browser settings page change. `GET /settings` renders through
  `theme.theme_page` today; the read-only mode-layer rows the UI-SPEC's Settings
  Expansion Contract also names are plan 16B-07's, because they need the
  mode-layer table that plan builds.
- No migration of an existing `itembank.json`. The additions are read from
  defaults, so no file needs rewriting and none is rewritten.
</out_of_scope>

<flagged_assumptions>
- **Whether `cmd_config` already lists every schema property is verified at
  execution, not assumed.** Task 3 step 1 requires running `itembank config` and
  looking, and requires recording the smallest change if one was needed. A plan
  that assumed the answer would either add dead code or miss a gap.

- **The expected schema property count `24` and required count `18` assume the
  shipped file had 20 and 18 when plan 16B-01 recorded its baseline.** If plan
  16B-01's step 6 recorded a different property count as a deviation, the
  expected value here shifts by the same amount and the summary records both.

- **`x-itembank-phase: 16.2` maps 16A, 16B, and 16C to 16.1, 16.2, and 16.3.**
  That mapping is this plan's own, recorded as `D-16B-11` with the shipped
  comment above `THIS_PHASE` as its justification. No prior artifact assigns
  subphase floats, so if a later phase adopts a different mapping, `D-16B-11` is
  the record to amend and the four keys are the only ones affected.

- **The SettingsPanel loading, overflow, and long-text rows are carried as
  backstop markers**, because all three are Phase 17A rendering outcomes. At
  verification time, no explicit evidence for a backstop row is
  `insufficient_spec` and needs a human, never a silent pass.
</flagged_assumptions>

<summary_obligations>
`16B-06-SUMMARY.md` records: the verbatim output of Task 1 steps 3 and 4; the
`git diff --stat schemas/settings.schema.json` line proving insertions and zero
deletions; the baseline key count and hash from `16B-PRECONDITION.md` beside the
recomputed values, side by side; which of the six settings codes each of the
seven malformed documents produced; whether `cmd_config` needed any change in
Task 3 step 1 and the exact diff if so; the final values of
`settings.THIS_PHASE` and `len(settings.SETTINGS_CODES)`; which truth was
verified by which command with its actual stdout; and any deviation from this
plan with its reason.
</summary_obligations>

<output>
Create
`.planning/phases/16B-ia-modes-recovery-contract/16B-06-SUMMARY.md`
when done.
</output>
