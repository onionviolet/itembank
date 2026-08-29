# 16B-06 summary

Plan `16B-06`, wave 6, three tasks, all complete. The settings contract gained
the four groups APP-03 names, and the additivity claim is proven by comparison
against the baseline taken before any 16B change existed, not by promise.

## The additivity proof

```
pre-existing keys now:  22
baseline recorded:      22
pre-existing hash now:  3d9a94c70270413b29390317660b37dc198fc6ae1530c4d5dd3041710c4a1235
baseline recorded:      3d9a94c70270413b29390317660b37dc198fc6ae1530c4d5dd3041710c4a1235
```

**Byte-identical.** Every key that existed before this phase has exactly the
effective value `16B-PRECONDITION.md` recorded on 2026-08-28, before
`surfaces/ia.py` existed. `test_16b_groups_additive` reads that section out of
the precondition file at run time and fails by name if the section is missing,
so the claim cannot silently degrade into an unchecked assertion.

```
git diff --stat schemas/settings.schema.json
 schemas/settings.schema.json | 104 +++++++++++++++++++++++++++++++++++++++++++
 1 file changed, 104 insertions(+)
```

**Zero deletions.** No existing line was rewritten. The top-level `required`
array, `additionalProperties`, `$schema`, `$id`, `title`, `description`, and
`x-itembank-version` are untouched.

## Command output, final line of every verify block

| Command | Final line |
|---|---|
| `python3 -c "... sv.check_schema(s); print('schema ok', ...)"` | `schema ok 26 19 False` |
| `python3 -c "... print(sorted(new & set(s['required'])), sorted(new - set(s['properties'])))"` | `[] []` |
| `python3 tests/config_roundtrip.py` | `config contract: ok (...)`, exit 0 |
| `python3 -c "... print(settings.THIS_PHASE, len(settings.SETTINGS_CODES))"` | `10 6` |
| `python3 itembank.py config` | all four keys, all four labels, exit 0 |
| `python3 itembank.py guard .` | `0 offending files` |
| the whole suite, 85 files | `0 failing` |

## Codes produced by each malformed document

| Document | Code |
|---|---|
| `{"approved_roots": "not-a-list"}` | `settings.invalid_type` |
| `{"approved_roots": [""]}` | `settings.invalid_value` |
| `{"network_egress": {"hosted_operations": "maybe", "last_disclosure": ""}}` | `settings.invalid_value` |
| `{"accessibility": {"reduced_motion": true, "high_contrast": "system"}}` | `settings.invalid_type` |
| `{"storage": {"data_dir": "", "backups_enabled": "yes", "backup_dir": ""}}` | `settings.invalid_type` |
| `{"storage": {..., "extra": 1}}` | `settings.unknown_key` |

All six are members of the existing `SETTINGS_CODES`. No seventh code was added,
no validation function was written, and the one validator is still
`schema_validate.validate()`.

## Deviations from this plan, with reasons

**1. The expected counts are `26` properties and `19` required, not the plan's
`24` and `18`.** The plan's numbers assume the pre-16B tree had 20 properties and
18 required. `16B-PRECONDITION.md` recorded the landed tree at 22 and 19, drifted
by `14C-01`, `17A-05`, and `17A-08`. Four additive properties and zero additive
required entries take that to 26 and 19, which is arithmetically the same
change the plan described. `additionalProperties` is still `False` and none of
the four new keys joined `required`, which are the two facts that make a pre-16B
`itembank.json` validate unchanged.

**2. `{"network_egress": {"hosted_operations": "off"}}` is not malformed and was
moved out of the rejection list.** The plan listed it as a document that should
exit with a code. It loads cleanly, and correctly: `merge_over_defaults` fills a
missing nested member from the group's own complete schema `default`, which is
exactly the shipped contract `test_missing_schema_key_reads_as_default` asserts.
Forcing a rejection would have required giving the group an incomplete `default`,
which contradicts this plan's own Task 1 spec.

The case is now asserted positively instead: a partial group keeps the member it
carried and fills the one it omitted from the schema default. That is the
stronger assertion, because a group whose schema default were incomplete would
fail it. Six documents remain in the rejection list and all six reject.

**3. The declared-not-enforced note prints nine times, not four.** The plan's
criterion says exactly four, while its own step 3 requires the note be driven by
`x-itembank-phase > THIS_PHASE` "rather than by a hard-coded key list, so the
line disappears by itself when a later phase raises `THIS_PHASE`". Those two
cannot both hold: nine top-level keys already sit above `THIS_PHASE`, which is
`10`. They are `auditor_autonomy` (11), `teaching` (13.5), `source` (14), `home`
(17.1), `lti` (999.4), and this phase's four.

Resolved in favor of the rule. Restricting the note to four would have required
the hard-coded list the plan forbids, and would have been dishonest: the five
shipped keys are declared-but-unenforced by `THIS_PHASE`'s own definition, and
`status_text` already reports each of them as `inert`. The substantive criterion
is met and asserted: each of the four new groups carries the note prefixed by its
own label, and `theme`, `model_backend`, and `update_policy` carry it zero times.

**4. `tests/config_roundtrip.py`'s `test_schema_names_every_project_key` gained
the four key names.** That shipped test carries a hard-coded expected key set, so
any additive schema key must be added to it or it fails. The addition is four
strings and a comment; nothing else in the test changed.

**5. `cmd_config` needed no change to list the four groups.** Task 3 step 1 asked
this to be confirmed rather than assumed. `print_table` iterates
`schema["properties"]` and already rendered all four with their nested rows. The
only change to that function is the two-line note emission.

**6. `python3` for `python`, and the full-suite criterion run with
`ANKI_CONNECT_URL=http://127.0.0.1:1/`.** Carried forward from
`16B-02-SUMMARY.md`.

## Which truth was verified by which command

| Truth | Command | Actual result |
|---|---|---|
| The schema stays inside the validator's closed keyword set | `schema_validate.check_schema` | raised nothing |
| Four keys added, `required` untouched, `additionalProperties` unchanged | the counts command | `26 19 False`, `[] []` |
| Every pre-existing key is unmoved | `test_16b_groups_additive` | identical count and SHA-256 |
| A pre-phase file still loads | same test | `{"theme": "dark"}` loads, four keys default |
| The unknown-key contract is unbroken | same test | `not_a_real_group` preserved |
| Every default is restrictive | `test_16b_defaults_are_restrictive` | `[]`, `off`, `system`, `false`, no `os.sep` in any default |
| `backups_enabled` is a real bool | same test | `isinstance(..., bool)` and `is False` |
| A bad value gets one of the six existing codes | `test_16b_invalid_values_are_coded` | six documents, six codes, all existing |
| A partial group fills from its default | same test | `hosted_operations` kept, `last_disclosure` defaulted |
| The four groups are labelled and flagged | `test_16b_groups_labelled_and_flagged` | four keys, four labels, four labelled notes |
| An enforced key never carries the note | same test | zero for `theme`, `model_backend`, `update_policy` |
| No label names a nonexistent key | same test | empty difference |
| `THIS_PHASE` and the code count are unmoved | the settings command | `10 6` |

## Artifacts changed

- `schemas/settings.schema.json`: `approved_roots`, `network_egress`,
  `accessibility`, `storage`, each with `x-itembank-phase: 16.2`, a restrictive
  `default`, and `additionalProperties: false` on the three object groups.
  104 insertions, 0 deletions.
- `surfaces/settings.py`: `NETWORK_EGRESS_SETTINGS_DEFAULTS`,
  `ACCESSIBILITY_SETTINGS_DEFAULTS`, `STORAGE_SETTINGS_DEFAULTS`,
  `SETTINGS_GROUP_LABELS`, `SETTINGS_DECLARED_NOT_ENFORCED_NOTE`, and two lines
  in `print_table`. No function added. `THIS_PHASE` and `SETTINGS_CODES`
  unchanged.
- `tests/config_roundtrip.py`: `_read_additivity_baseline`,
  `test_16b_groups_additive`, `test_16b_defaults_are_restrictive`,
  `test_16b_invalid_values_are_coded`,
  `test_16b_groups_labelled_and_flagged`, four key names in the shipped
  completeness set, and four `main()` calls.
- `16B-DECISIONS.md`: `## D-16B-11. The subphase marker on new settings keys`.
