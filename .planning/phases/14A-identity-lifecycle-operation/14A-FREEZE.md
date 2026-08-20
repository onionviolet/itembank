# 14A freeze record

## 2026-08-18: reflow-normalization decision (D-14A-2's deferred half)

**Decision: option-a. Keep the first cut. No reflow normalization.**

`identity.normalize_for_fingerprint` is unchanged: line endings are
normalized to `\n` for every kind, and trailing whitespace is stripped for
every kind except `bank` and `lesson`. No further collapsing of mid-content
whitespace or line-wrap position is added.

### Decision provenance

Weibao's verbatim answer, when the reflow corpus check's evidence and the
two options were put to him: "do whats best and keep things open in case
another option is better." This is a delegation with a keep-options-open
condition, not a direct pick of option-a or option-b.

The orchestrating agent resolved the delegation to **option-a** under that
condition. Option-a is the reversibility-preserving choice: the rule can be
added later as a recorded migration with its own corpus evidence, while
option-b's absorbed changes (a rewrap that stops being recorded as a
revision) could never be recovered retroactively once adopted, because the
information about what changed would simply never have been written to the
journal. Option-a keeps the later door open; option-b would close it. The
plan's own recommended default was also option-a, for the matching reason
stated there: "every change [the candidate rule] absorbs is a change a
compare-and-swap write will pass without noticing."

### Evidence: the four reflow counts

From `tests/file_fault_tracer.py:reflow_corpus_check()`, run over a 2000-file
mutation sample of the 10k synthetic corpus (`.planning/phases/14A-identity-lifecycle-operation/14A-TRACER-REPORT.md`,
"Reflow corpus check" section):

- Total mutations: 2000
- Meaningful changes noticed by the first cut: 500
- Reflow-only changes noticed by the first cut: 500
- Changes the first cut already absorbs (trailing whitespace, line
  endings): 1000
- False-absorption count (candidate rule would absorb a change that is
  NOT reflow-only): 0
- Mutation class proportions used: content=0.25, line_ending=0.25,
  reflow=0.25, trailing_ws=0.25

The false-absorption count is 0 on this corpus: the candidate rule would
not have discarded any of the synthetic content mutations. This does not
by itself justify adopting the rule (a synthetic corpus of generated
filler prose is not the same evidentiary weight as behavior on the
learner's own material over time), but it does confirm the rule is not
obviously unsafe. The decision to stay with option-a rests on the
asymmetry of recoverability described above, not on this count alone.

This amends `DECISIONS-PRE-14A-2026-08-14.md`'s D-14A-2 deferred item: the
reflow half of D-14A-2 is now resolved as option-a, recorded here with its
evidence.

### Reconsideration condition

This decision stays open, per Weibao's own keep-options-open instruction.
If rewrap-only revisions become a real annoyance in a later history view, a
later phase may:

- add reflow normalization as a recorded migration with its own corpus
  evidence (re-running a check of this same shape against real learner
  material, not only synthetic filler), or
- handle rewrap noise in the presentation layer instead of the fingerprint
  layer (for example, collapsing adjacent whitespace-only revisions in a
  history view without changing what the journal records).

Both routes stay available under option-a; neither route is available,
after the fact, under option-b.

### What the executor did with this answer

Per the plan's Task 3 action list for option-a: nothing was changed in
`identity.normalize_for_fingerprint`. The decision and the counts are
recorded here. Task 4 proceeds on this basis.

## Frozen at 14A

### Frozen

- The object id shape: 16 lowercase hex characters, minted with
  `uuid4().hex[:16]` (`identity.new_object_id()`), never derived from
  content, path, or name.
- The eleven revision record keys, in their fixed order
  (`identity.REVISION_KEYS`): `object_id`, `kind`, `revision`,
  `parent_revision`, `fingerprint`, `timestamp`, `origin`,
  `profile_version`, `source_version`, `generator_version`, `rights`.
- The twenty-three journal entry keys, in their fixed order
  (`journal.ENTRY_KEYS`): `schema_version`, `entry_id`, `timestamp`,
  `operation`, `state`, `resolves_entry`, `object_id`, `kind`, `revision`,
  `parent_revision`, `path`, `expected_fingerprint`, `before_fingerprint`,
  `after_fingerprint`, `before_image`, `undo`, `source_object_id`,
  `source_revision`, `restores_revision`, `origin`, `code`, `message`,
  `rights`.
- The two-line prepared-then-applied protocol and the append-only
  resolution rule: every durable write appends a `prepared` entry, then
  either an `applied` or a `refused` entry that names the `prepared`
  entry it resolves via `resolves_entry`; no entry already written is
  ever rewritten or deleted.
- The six operation names (`journal.OPERATION_TYPES`): `link`, `import`,
  `copy`, `move`, `edit_in_place`, `supersede`.
- The object kinds (`identity.OBJECT_KINDS`): `course`, `objective`,
  `source`, `lesson`, `bank`, `component`.
- The seven rights operation names (`identity.RIGHTS_OPERATIONS`): `read`,
  `quote`, `transform`, `remote_process`, `package`, `export`, `share`;
  and the three rights states (`identity.RIGHTS_STATES`): `granted`,
  `denied`, `unknown`.
- The fingerprint normalization rule, as decided in Task 3 above: line
  endings (`\r\n` and bare `\r`) normalized to `\n` for every kind;
  trailing whitespace stripped from every line for every kind except
  `bank` and `lesson`; no reflow, mid-content whitespace collapsing, or
  Unicode normalization added. The `bank`/`lesson` carve-out
  (`identity.TRAILING_WS_EXEMPT_KINDS`) holds regardless of the reflow
  answer and stays exempt from trailing-whitespace normalization under
  both options.

### Not frozen, and deliberately so

- The `_journal/` directory name and its internal file names
  (`journal.jsonl`, `objects.json`, `journal.lock`, the `before/` image
  directory): local layout a later phase may change with a migration.
- The disposable `objects.json` registry projection shape: rebuildable
  from the journal log alone via `journal.rebuild_registry`, never a
  second source of truth.
- The refusal message wording (the human-readable `message` string on a
  `journal.JournalError` or a refused entry): copy, not contract. The
  refusal `code` strings (for example `journal.conflict`,
  `journal.stale_preflight`, `journal.rights_unknown`) are the stable,
  machine-readable part.
- Everything routed to 14B in the three plans' out-of-scope sections:
  the graph kernel, the sidecar, the outline projection, course
  packaging, the clean-machine restore check, and the 100k corpus run
  (this plan's own "The 100k corpus" section).

### The evidence

Tracer's final line, quoted verbatim:

```
TRACER: 8 passed, 0 skipped, 0 failed
```

Full suite result: `for t in tests/*.py; do python3 "$t" || exit 1; done`
exited 0 across all 68 files in `tests/` (0 failures).

Guard result: `python3 itembank.py guard .` printed `0 offending files`
and exited 0.

Full report: `.planning/phases/14A-identity-lifecycle-operation/14A-TRACER-REPORT.md`.

### What breaks if this is changed later

- Changing the object id shape forces a migration of every id already
  minted into `_journal/journal.jsonl` and every reference to it from
  13.9's walking-skeleton slice forward, since ids are opaque and never
  recomputed from content.
- Changing the eleven revision record keys or their order forces a
  migration of every stored revision record and every reader that
  destructures a revision positionally or by `list(record.keys())`
  equality (asserted directly in `tests/identity_roundtrip.py`).
- Changing the twenty-three journal entry keys or their order forces a
  rewrite of every line already appended to `journal.jsonl`, breaking the
  append-only guarantee this format exists to provide, and breaks
  `journal.entries()`'s `list(entry.keys()) == ENTRY_KEYS` conformance
  used throughout `tests/journal_roundtrip.py` and
  `tests/operations_roundtrip.py`.
- Changing the prepared-then-applied protocol forces a re-derivation of
  `journal.replay()`'s interrupted/recoverable classification, since that
  classification depends on re-reading the target's actual bytes against
  exactly two possible prior states.
- Adding, removing, or renaming an operation name forces every existing
  journal entry carrying the old name to be reinterpreted or migrated,
  and breaks the closed-vocabulary membership tests in
  `tests/operations_roundtrip.py`.
- Adding or removing an object kind forces a review of every
  kind-conditional rule that already exists (the `bank`/`lesson`
  trailing-whitespace carve-out, the `source`-only default rights record)
  for whether the new or removed kind needs the same treatment.
- Changing the rights operation names or states forces a migration of
  every stored `rights` dict and breaks `identity.rights_state`'s exact
  lowercase ASCII string comparison, which the RIGHTS-01 refusal path
  depends on to stay restrictive rather than permissive on an
  unrecognized value.
- Changing the fingerprint normalization rule (including reversing this
  freeze's reflow decision) changes what counts as a change for every
  object fingerprinted from that point forward: every fingerprint
  recorded before the change would read as stale under a new rule, or,
  the more dangerous direction, adopting a broader normalization after
  the fact would mean changes it newly absorbs were never recorded as
  having happened at all. This is exactly the one-way-door reasoning this
  freeze record exists to make visible.
