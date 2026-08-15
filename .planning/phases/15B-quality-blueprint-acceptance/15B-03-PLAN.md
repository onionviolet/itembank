---
phase: 15B-quality-blueprint-acceptance
plan: 03
type: execute
wave: 3
depends_on: ["15B-02"]
files_modified:
  - blueprint.py
  - fixtures/corpus_15b.py
  - tests/blueprint_roundtrip.py
autonomous: true
requirements: [RELIABILITY-03]
estimate:
  tokens: 62000
  raw_tokens: 62000
  tasks: 2
  confidence: low
must_haves:
  truths:
    - "Staleness is a comparison of two fingerprints supplied as arguments and is recomputed on every read; blueprint.classify_staleness stores nothing, caches nothing, reads no file, and no function in this phase writes a stale flag that a later read then trusts."
    - "blueprint.STALENESS_DISPOSITIONS equals exactly the four words REQUIREMENTS.md RELIABILITY-03 itself uses, in the requirement's own order: rebind, migrate, supersede, retain. The tuple is closed, comparison is exact ASCII with no case folding and no synonyms, and a fifth disposition is a change to the requirement, not to this module."
    - "An unprovable freshness is not freshness: classify_staleness returns True when either fingerprint is empty, None, or absent, so a dependent whose base fingerprint was never recorded reads stale and is blocked rather than silently trusted."
    - "Fingerprint comparison is exact ASCII with no case folding, no whitespace stripping, and no normalization, so two renderings of the same digest that differ in case read as stale, which fails safe rather than fails open."
    - "A stale dependent blocks acceptance: blueprint.acceptance_block returns a non-empty refusal list naming blueprint.stale_dependent for every stale row that has no matching recorded disposition, and returns an empty list only when every stale row is matched by a disposition record whose recorded current_fingerprint equals the live one."
    - "A disposition record names its reviewer, its disposition, its rationale, and both fingerprints; disposition_record raises rather than returning a record when the disposition is outside the closed four, when the reviewer role is not reviewer, or when the rationale is empty or whitespace only."
    - "A disposition recorded against one fingerprint pair does not clear a later change: once the dependency's live fingerprint moves again, the recorded disposition no longer matches and acceptance is blocked again, so reconciliation is per change rather than once and forever."
    - "staleness_report over an empty dependent list returns an empty list, over a single dependent returns exactly one row, and returns its rows sorted by (object_id, dependency_object_id) so two runs over the same input produce byte-identical output."
  prohibitions:
    - statement: "A stale dependent must not be accepted; an acceptance path that reads a staleness result, finds it stale, and proceeds because the content still passed the gates is the exact failure this plan exists to prevent."
      status: kept
      verification: flagged-unverified
    - statement: "A stale derivative must not be silently rebuilt in place of a recorded reviewer disposition; regenerating against the changed dependency and accepting the refreshed result removes the reviewer's chance to see that anything changed."
      status: kept
      verification: flagged-unverified
    - statement: "A staleness verdict must not be stored as a boolean that a later read trusts; the only durable values are the two fingerprints, and the verdict is derived again every time it is needed."
      status: kept
      verification: flagged-unverified
  artifacts:
    - "blueprint.py gains STALENESS_DISPOSITIONS, STALENESS_ROW_KEYS, DISPOSITION_KEYS, classify_staleness, staleness_row, staleness_report, disposition_record, and acceptance_block"
    - "blueprint.BLUEPRINT_CODES gains five members: blueprint.stale_dependent, blueprint.unknown_disposition, blueprint.disposition_reviewer_required, blueprint.disposition_rationale_required, blueprint.disposition_superseded"
    - "fixtures/corpus_15b.py gains build_staleness_fixture and edit_source"
    - "tests/blueprint_roundtrip.py gains check_staleness_classifier and check_staleness_blocks"
  key_links:
    - "classify_staleness takes both fingerprints as arguments and never computes either. The caller reads the live fingerprint through identity.object_fingerprint at the moment of the check. If this function ever computed the current fingerprint itself, blueprint.py would need a file read and the structural ban that it never touches disk would be gone, and the recomputed-on-read discipline would become a promise instead of a property."
    - "A disposition record carries the current_fingerprint it was recorded against, not only the base one. Matching a disposition to a stale row compares the recorded current_fingerprint to the live one, which is what makes reconciliation per change. Recording only the base fingerprint would let one reviewer decision clear every future change to the same dependency, forever."
    - "acceptance_block returns a list of refusals rather than raising, so a caller can report every blocked dependent at once. The acceptance functions plan 15B-04 adds are what turn a non-empty list into a raised refusal; this function decides what is blocked and nothing decides it twice."
---

<objective>
Make RELIABILITY-03's staleness rule real and make it a hard block.

RELIABILITY-03, quoted in full from `REQUIREMENTS.md`: "External, source, or
version changes mark affected bindings and proposals stale and require a
rebind, migrate, supersede, or retain review; a stale derivative is rebuilt,
never trusted silently. Owner: course builder plus UPGRADE. Durable object:
staleness and dependency state. Authority: reviewer for rebinding. Degraded: a
stale proposal is shown as stale and blocked from acceptance until reconciled."

Two things in that text decide this plan's shape. The four disposition words
are named in the requirement itself, so this phase transcribes them rather than
choosing them. And the Degraded clause says blocked, not rebuilt: the tempting
shortcut of re-running the drafting step against the changed dependency and
accepting the refreshed result looks helpful and removes the reviewer's chance
to see that anything changed.

Decisions already made, cited, and never re-derived here:

- **REQUIREMENTS.md RELIABILITY-03**, quoted above. The four dispositions are
  its own words in its own order.
- **D-15B-1** in `15B-DECISIONS.md`: where this code lives. This plan is
  written against `option-a`, which puts the classifier in `blueprint.py`.
- **15B-RESEARCH.md Pattern 3**, quoted: "A binding, proposal, or accepted
  revision that depends on another object is never marked stale at write time
  and trusted later; staleness is recomputed at read/accept time by comparing
  the dependency's live fingerprint against the base fingerprint recorded when
  the dependent was created or last reconciled."
- **schemas/audit_report.schema.json line 86 to 89**, the shipped prior art,
  quoted: `"stale": {"type": "boolean", "description": "True when either input
  fingerprint no longer matches the cited source/bank; a stale report is never
  treated as current (D-04)."` This phase follows the same derivation rule for
  a different object kind and invents no second staleness representation.
- **15B-RESEARCH.md Pitfall 4**: a stale dependent silently rebuilding instead
  of blocking acceptance, with the warning sign named as "any acceptance
  function that reads a staleness flag, finds it True, and proceeds to write
  anyway because the content still passed the gates".
- **15B-01 objective decision table**: no `DRAFT_STATES` tuple is minted
  anywhere in Phase 15B; each object kind keeps its own narrow closed state
  set.

Decisions this plan makes and locks, so the executor never guesses (the
`PLANNING-DIRECTIVES.md` section 5 bar):

| Open question | Locked answer | One-line rationale |
|---|---|---|
| What an absent or empty fingerprint means | Stale. `classify_staleness` returns `True` when either argument is `None`, an empty string, or absent | An unprovable freshness is not freshness. Reading an unknown as fresh would let a dependent with no recorded base fingerprint pass acceptance forever, which is the failure-open direction. |
| How two fingerprints are compared | Exact ASCII equality of the two strings, with no case folding, no stripping, and no Unicode normalization | The values are hex digests produced by one function, `identity.object_fingerprint`. Any transformation before comparison is an opportunity for two different digests to compare equal, and the fail-safe direction of a false negative on case is a spurious stale, not a spurious fresh. |
| What a disposition record must carry to clear a block | The disposition, the reviewer role and name, a non-empty rationale, the base fingerprint, and the current fingerprint it was recorded against | Recording only the base fingerprint would let one recorded decision clear every future change to the same dependency. Carrying the current one makes reconciliation per change. |
| Whether `retain` is weaker than the other three | No. `retain` is a recorded reviewer decision that the dependent stays as it is despite the change, and it clears the block exactly as the other three do | RELIABILITY-03 lists all four as review outcomes. A `retain` that did not clear the block would make the requirement's own fourth word unusable. |
| Whether `acceptance_block` raises or returns | Returns a list of refusal dicts | A caller reporting three blocked dependents should report three, not the first. Plan 15B-04's acceptance functions turn a non-empty list into a raised refusal, and nothing decides blocking twice. |
| Whether a stale dependent may be auto-rebuilt | Never, by any function in this phase | RELIABILITY-03's Degraded clause reads "blocked from acceptance until reconciled", not "rebuilt and accepted". |

Purpose: make a change to a dependency visible to a reviewer before anything
built on it becomes durable.
Output: the staleness classifier, the four-word disposition vocabulary, the
disposition record, and the acceptance block that plan 15B-04 raises on.
</objective>

<context>
@.planning/phases/15B-quality-blueprint-acceptance/15B-RESEARCH.md
@.planning/phases/15B-quality-blueprint-acceptance/15B-PATTERNS.md
@.planning/phases/15B-quality-blueprint-acceptance/15B-DECISIONS.md
@.planning/PLANNING-DIRECTIVES.md
@.planning/REQUIREMENTS.md
@blueprint.py
@schemas/audit_report.schema.json
@auditor.py
</context>

## Artifacts this phase produces (plan 15B-03 share)

Added to `blueprint.py`. Every symbol below is new in this phase.

- Constants: `STALENESS_DISPOSITIONS = ("rebind", "migrate", "supersede",
  "retain")`, `REVIEWER_ROLE = "reviewer"`,
  `STALENESS_ROW_KEYS = ("object_id", "object_kind", "dependency_object_id",
  "dependency_kind", "base_fingerprint", "current_fingerprint", "stale")`,
  `DISPOSITION_KEYS = ("schema_version", "object_id", "dependency_object_id",
  "disposition", "reviewer_role", "reviewer_name", "rationale",
  "base_fingerprint", "current_fingerprint")`.
- Functions: `classify_staleness(base_fingerprint, current_fingerprint)`,
  `staleness_row(object_id, object_kind, dependency_object_id, dependency_kind,
  base_fingerprint, current_fingerprint)`, `staleness_report(dependents)`,
  `disposition_record(object_id, dependency_object_id, disposition,
  reviewer_role, reviewer_name, rationale, base_fingerprint,
  current_fingerprint)`, `acceptance_block(rows, dispositions)`.
- `BLUEPRINT_CODES` gains five members: `blueprint.disposition_rationale_required`,
  `blueprint.disposition_reviewer_required`, `blueprint.disposition_superseded`,
  `blueprint.stale_dependent`, `blueprint.unknown_disposition`. The tuple grows
  from thirteen members to eighteen and stays sorted.

Added to `fixtures/corpus_15b.py`: `build_staleness_fixture(dest)` returning a
dict with the keys `course_root`, `source_path`, `source_object_id`,
`base_fingerprint`, `dependents`, and `bank_path`; and
`edit_source(fixture, marker)` which rewrites the synthetic source file's
content so its fingerprint changes and returns the new fingerprint.

New test functions in `tests/blueprint_roundtrip.py`:
`check_staleness_classifier()` and `check_staleness_blocks()`.

No CLI command, no daemon route, no schema file, and no journal record type is
produced by this plan. `blueprint.py`'s import list is unchanged: `model`,
`runtime`, `schema_validate`, `json`, `os`, `re`.

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: the fingerprint comparison, the four dispositions, and the report</name>
  <files>blueprint.py, fixtures/corpus_15b.py, tests/blueprint_roundtrip.py</files>
  <read_first>
- `.planning/REQUIREMENTS.md` RELIABILITY-03 in full, including its Fixture
  sentence, quoted in this plan's objective. The four disposition words come
  from that sentence and are transcribed, not chosen.
- `blueprint.py` in full as it stands after plan 15B-02:
  `BLUEPRINT_CODES`'s set-then-sorted construction, `BlueprintError`,
  `blueprint_finding`, `canonical_json`, `within_tolerance`, and the module
  docstring's structural-ban paragraph, which this task must not weaken.
- `schemas/audit_report.schema.json` lines 86 to 89, the shipped `stale` field
  and its description, quoted in this plan's objective, and `$defs.coverage_row`'s
  `state` enum, whose sixth member is the literal `"stale"`. Read both so the
  new vocabulary stays structurally distinct from Phase 11's rather than being
  renamed into it.
- `identity.py` as landed: `object_fingerprint(raw, kind)` and
  `normalize_for_fingerprint(raw, kind)`, so the executor knows what the two
  strings this function compares actually are and does not re-derive either.
- `fixtures/corpus_15b.py` as it stands after plan 15B-02, its fixed-seed
  convention and its `teardown`.
- `tests/blueprint_roundtrip.py` as it stands after plan 15B-02, its
  `fail(msg)` helper and its `main()` wiring.
  </read_first>
  <behavior>
Assertions `check_staleness_classifier()` must make. Write them first and
confirm they fail before extending `blueprint.py`.

The vocabulary is closed and is the requirement's own:

- `blueprint.STALENESS_DISPOSITIONS` equals `("rebind", "migrate", "supersede",
  "retain")`, in that exact order, and has exactly four members.
- The tuple order is the requirement's own and is not sorted; assert the order
  explicitly rather than asserting set equality.
- `blueprint.STALENESS_DISPOSITIONS` shares no member with
  `graph.MIGRATION_STATES`, asserted as an empty set intersection, so the
  disposition `migrate` and the migration state `accepted` are never confused
  for one vocabulary. The one shared word between this phase's vocabularies is
  `migrate`, which is a disposition here and a `journal.RECORD_TYPES` member
  there; assert that both exist and that neither tuple contains the other's
  members.

The comparison is exact and fails safe:

- `classify_staleness("abc", "abc")` is `False`.
- `classify_staleness("abc", "abd")` is `True`.
- `classify_staleness("ABC", "abc")` is `True`. No case folding.
- `classify_staleness(" abc", "abc")` is `True`. No stripping.
- `classify_staleness("", "abc")` is `True`.
- `classify_staleness("abc", "")` is `True`.
- `classify_staleness(None, None)` is `True`.
- `classify_staleness("", "")` is `True`. Two absences do not prove sameness.
- `classify_staleness` returns only `True` or `False` and raises nothing for
  any string or `None` input.
- Given a real fixture source, `classify_staleness(base,
  identity.object_fingerprint(open(path,"rb").read(), "source"))` is `False`
  before `edit_source` and `True` after it, computed in the test rather than
  read back from any stored flag.

A row is a derivation, not a stored flag:

- `blueprint.staleness_row(...)` returns a dict whose key set equals
  `set(blueprint.STALENESS_ROW_KEYS)` and whose `stale` value equals
  `classify_staleness(base_fingerprint, current_fingerprint)`.
- Calling `staleness_row` twice with the same arguments returns equal dicts.
- `blueprint.py` contains no assignment that stores a staleness verdict on a
  durable object; asserted behaviorally by the fact that no function in
  `blueprint.py` writes anything, which the existing `hasattr` bans already
  make structural.

The report is ordered, total, and handles the empty and single cases:

- `staleness_report([])` returns `[]`.
- `staleness_report([one])` returns a list of exactly one row.
- `staleness_report(dependents)` returns one row per dependent, never fewer,
  including for dependents that are not stale, so a reader sees the whole
  dependency set rather than only its failures.
- The returned rows are sorted by `(object_id, dependency_object_id)`, and two
  calls with the input list shuffled return equal lists.
- Two dependents sharing an `object_id` and a `dependency_object_id` are both
  returned and their relative order is the input order after the sort, which is
  stable because Python's sort is stable; assert that the two rows appear and
  that their order is reproducible across two runs.

The disposition record refuses before it records:

- `disposition_record(..., disposition="rebind", reviewer_role="reviewer",
  rationale="the source moved to a new edition", ...)` returns a dict whose key
  set equals `set(blueprint.DISPOSITION_KEYS)` and whose `schema_version` is
  `1`.
- `disposition_record(..., disposition="refresh", ...)` raises `BlueprintError`
  with code `blueprint.unknown_disposition`, and the message contains all four
  permitted words.
- `disposition_record(..., disposition="Rebind", ...)` raises the same, because
  comparison is exact ASCII with no case folding.
- `disposition_record(..., reviewer_role="agent", ...)` raises `BlueprintError`
  with code `blueprint.disposition_reviewer_required`, and the message states
  that RELIABILITY-03 names the reviewer as the authority for rebinding.
- `disposition_record(..., rationale="", ...)` and
  `disposition_record(..., rationale="   ", ...)` both raise `BlueprintError`
  with code `blueprint.disposition_rationale_required`, following the
  `graph.empty_rationale` precedent 14B-04 already set for a migration
  proposal.
- Every one of the four permitted dispositions is accepted, asserted by
  building one record per member of `STALENESS_DISPOSITIONS` in a loop, so
  `retain` is proven usable rather than assumed.
- A recursive walk over every returned record finds no `float` and no key whose
  lowercase name contains `mastery`, `completion`, `readiness`, `progress`,
  `percent`, or `score`.
  </behavior>
  <action>
1. Add `check_staleness_classifier()` to `tests/blueprint_roundtrip.py` with
   every assertion in `<behavior>`, wire it into `main()`, and run
   `python tests/blueprint_roundtrip.py` to confirm it fails.

2. Add `build_staleness_fixture(dest)` and `edit_source(fixture, marker)` to
   `fixtures/corpus_15b.py`. `build_staleness_fixture` writes one fictional
   synthetic source file under the course root, records its
   `identity.object_fingerprint` as `base_fingerprint`, and returns three
   dependents: one binding, one migration proposal, and one blueprint, each
   naming the same `dependency_object_id`. `edit_source(fixture, marker)`
   appends the exact line `Revised section marker: ` followed by `marker` to
   the source file, rewrites it atomically, and returns the new fingerprint.
   All content is fictional and fixed-seed; no clock read and no randomness.

3. Add to `blueprint.py` the constants
   `STALENESS_DISPOSITIONS = ("rebind", "migrate", "supersede", "retain")`,
   `REVIEWER_ROLE = "reviewer"`, `STALENESS_ROW_KEYS`, and `DISPOSITION_KEYS`
   exactly as listed in this plan's Artifacts section. Above
   `STALENESS_DISPOSITIONS`, write a comment recording that the four words and
   their order are transcribed verbatim from `REQUIREMENTS.md` RELIABILITY-03's
   sentence "require a rebind, migrate, supersede, or retain review", that the
   tuple is closed and is not to be sorted, that comparison is exact ASCII with
   no case folding and no synonyms, and that a fifth disposition is a change to
   the requirement and not to this module.

4. Add the five new members to `BLUEPRINT_CODES`, keeping the set-then-sorted
   construction so the tuple stays sorted and grows from thirteen members to
   eighteen. Add their `BlueprintError` message templates, verbatim:
   - `blueprint.unknown_disposition`: `"%s is not one of the four staleness
     dispositions rebind, migrate, supersede, or retain; the vocabulary is
     RELIABILITY-03's own and comparison is exact, with no case folding and no
     synonyms"`
   - `blueprint.disposition_reviewer_required`: `"a staleness disposition is
     recorded by a reviewer; RELIABILITY-03 names the reviewer as the authority
     for rebinding, and role %s cannot record one"`
   - `blueprint.disposition_rationale_required`: `"a staleness disposition
     needs a rationale a later reader can evaluate; an empty rationale is
     refused"`

5. Implement `classify_staleness(base_fingerprint, current_fingerprint)`
   returning `True` when either argument is `None` or an empty string, and
   otherwise `base_fingerprint != current_fingerprint` compared as plain string
   inequality. Write a docstring stating in plain sentences that this function
   reads nothing and stores nothing, that both values are supplied by the
   caller who read the live one through `identity.object_fingerprint` at the
   moment of the check, that an unprovable freshness is not freshness so an
   absent value reads stale, and that comparison is exact with no case folding
   because a spurious stale is the safe direction and a spurious fresh is not.

6. Implement `staleness_row(...)` returning the seven-key dict, and
   `staleness_report(dependents)` returning
   `sorted(rows, key=lambda r: (r["object_id"], r["dependency_object_id"]))`
   over one row per dependent, including the fresh ones. Handle a `None` or
   empty `dependents` argument as an empty list.

7. Implement `disposition_record(...)` performing its three refusals in this
   order before building anything: unknown disposition, non-reviewer role,
   empty or whitespace-only rationale. Then return the nine-key dict with
   `schema_version` `1`. It reads no clock and mints no id, so two calls with
   the same arguments return equal dicts.
  </action>
  <verify>
  <automated>python tests/blueprint_roundtrip.py && python itembank.py guard .</automated>
Expected: `tests/blueprint_roundtrip.py` prints `OK blueprint_roundtrip` and
exits 0, and `guard` prints `0 offending files`. The degraded behavior this task
must prove rather than paper over is the absent-fingerprint case: a dependent
whose `base_fingerprint` was never recorded reads stale rather than fresh, and
the report still returns a row for it rather than omitting it. Confirm both, the
stale verdict and the present row, in the same run.
  </verify>
  <acceptance_criteria>
- `python tests/blueprint_roundtrip.py` exits 0 with
  `check_staleness_classifier` run.
- `python -c "import blueprint; print(blueprint.STALENESS_DISPOSITIONS)"`
  prints `('rebind', 'migrate', 'supersede', 'retain')`.
- `python -c "import blueprint; print(len(blueprint.BLUEPRINT_CODES), blueprint.BLUEPRINT_CODES == tuple(sorted(blueprint.BLUEPRINT_CODES)))"`
  prints `18 True`.
- `python -c "import blueprint as b; print(b.classify_staleness('a','a'), b.classify_staleness('A','a'), b.classify_staleness('',''), b.classify_staleness(None,'a'))"`
  prints `False True True True`.
- `python -c "import blueprint; print(blueprint.staleness_report([]), blueprint.staleness_report(None))"`
  prints `[] []`.
- `python -c "import blueprint,graph; print(set(blueprint.STALENESS_DISPOSITIONS) & set(graph.MIGRATION_STATES))"`
  prints `set()`.
- `python -c "import blueprint; print(hasattr(blueprint,'evidence'), hasattr(blueprint,'journal'), hasattr(blueprint,'course'))"`
  still prints `False False False`.
- `python itembank.py guard .` prints `0 offending files`.
- `git diff --name-only` after this task lists only `blueprint.py`,
  `fixtures/corpus_15b.py`, and `tests/blueprint_roundtrip.py`.
- None of the three changed files contains an em dash character.
  </acceptance_criteria>
  <precondition>Plan 15B-02 is green and `blueprint.py` exists with `BLUEPRINT_CODES` at thirteen members.</precondition>
  <reversibility rating="costly">`STALENESS_DISPOSITIONS` is transcribed from
  `REQUIREMENTS.md` RELIABILITY-03's own four words, so this plan makes no
  choice to reverse; changing the vocabulary means changing the requirement
  first. It is rated costly rather than one-way for that reason, and no
  checkpoint is owed for a decision the planner did not
  make.</reversibility>
  <done>Two fingerprints in, one derived verdict out, four closed disposition
  words transcribed from the requirement, and a report that shows every
  dependent rather than only the failing ones.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: a stale dependent blocks acceptance until a disposition matches</name>
  <files>blueprint.py, fixtures/corpus_15b.py, tests/blueprint_roundtrip.py</files>
  <read_first>
- `blueprint.py` in full as it stands after Task 1, in particular
  `classify_staleness`, `staleness_row`, `staleness_report`,
  `disposition_record`, and the five new `BLUEPRINT_CODES` members.
- `.planning/REQUIREMENTS.md` RELIABILITY-03's Degraded clause, quoted: "a
  stale proposal is shown as stale and blocked from acceptance until
  reconciled".
- `15B-RESEARCH.md` Pitfall 4 in full, including its named warning sign.
- `audit_writer.py` lines 304 to 322, `write_units`'s `writer.stale_preflight`
  refusal, the shipped precedent for refusing a write on a fingerprint mismatch
  rather than overwriting. This task's block is the same idea one level up, at
  the dependency rather than at the target.
- `fixtures/corpus_15b.py` as it stands after Task 1, `build_staleness_fixture`
  and `edit_source`.
  </read_first>
  <behavior>
Assertions `check_staleness_blocks()` must make. Write them first and confirm
they fail before extending `blueprint.py`.

The block is computed from rows and dispositions and nothing else:

- `acceptance_block([], [])` returns `[]`.
- `acceptance_block(rows, [])` where no row is stale returns `[]`.
- `acceptance_block(rows, [])` where two rows are stale returns exactly two
  refusal dicts, one per stale row, not one for the first.
- Each refusal dict has the key set `{"code", "object_id",
  "dependency_object_id", "base_fingerprint", "current_fingerprint",
  "message"}`, its `code` is `blueprint.stale_dependent`, and its `message` is
  the exact string `"the dependency this object was built against has changed;
  record a rebind, migrate, supersede, or retain review before accepting"`.
- The returned refusals are sorted by `(object_id, dependency_object_id)`.

A matching disposition clears exactly its own row:

- With one stale row and one `disposition_record` naming the same `object_id`,
  the same `dependency_object_id`, and a `current_fingerprint` equal to the
  row's live one, `acceptance_block` returns `[]`.
- With two stale rows and a disposition matching only the first,
  `acceptance_block` returns exactly one refusal, for the second.
- A disposition whose `object_id` matches but whose `dependency_object_id` does
  not clears nothing.
- Every one of the four dispositions clears the block, asserted by looping over
  `STALENESS_DISPOSITIONS` and rebuilding the same case four times, so `retain`
  is proven to clear rather than assumed to.

Reconciliation is per change, not once and forever:

- After a disposition clears a row, call `edit_source` again so the
  dependency's live fingerprint moves a second time, rebuild the row against
  the new live fingerprint, and assert `acceptance_block` returns exactly one
  refusal whose `code` is `blueprint.disposition_superseded` rather than
  `blueprint.stale_dependent`, and whose `message` is the exact string
  `"a review was recorded for an earlier version of this dependency and no
  longer applies; the dependency has changed again since it was reconciled"`.
- The superseded refusal names both the fingerprint the disposition was
  recorded against and the current one, so a reader can see which change went
  unreviewed.

The rebuild shortcut is refused structurally:

- `blueprint.py`'s source contains no call to `authoring.run_authoring`, no
  call to any function whose name contains `regenerate` or `rebuild`, and no
  import of `authoring`; asserted by `hasattr(blueprint, "authoring")` being
  `False` and by a source scan for the two substrings. The module cannot
  rebuild a stale derivative because it cannot reach the thing that builds one.
- `acceptance_block` has no parameter that could carry a regeneration callable,
  asserted by its signature having exactly two parameters.

Empty and null inputs:

- `acceptance_block(None, None)` returns `[]`.
- `acceptance_block(rows, None)` behaves as `acceptance_block(rows, [])`.
- A disposition list containing a dict missing a `DISPOSITION_KEYS` member is
  ignored for matching rather than crashing, and the row it would have cleared
  is still refused. A malformed clearance clears nothing.
  </behavior>
  <action>
1. Add `check_staleness_blocks()` to `tests/blueprint_roundtrip.py` with every
   assertion in `<behavior>`, wire it into `main()`, and run
   `python tests/blueprint_roundtrip.py` to confirm it fails.

2. Add the `blueprint.disposition_superseded` message template to
   `blueprint.py`, verbatim: `"a review was recorded for an earlier version of
   this dependency and no longer applies; the dependency has changed again
   since it was reconciled"`.

3. Implement `acceptance_block(rows, dispositions)` with exactly two
   parameters. Treat `None` for either as an empty list. For each row whose
   `stale` is `True`, look for a disposition whose `object_id` and
   `dependency_object_id` both match and whose keys form a superset of
   `DISPOSITION_KEYS`; a disposition missing a key is skipped. When no
   candidate matches, emit a `blueprint.stale_dependent` refusal. When a
   candidate matches but its `current_fingerprint` does not equal the row's
   `current_fingerprint`, emit a `blueprint.disposition_superseded` refusal
   carrying both fingerprints. When a candidate matches and its
   `current_fingerprint` equals the row's, emit nothing for that row. Return
   the refusals sorted by `(object_id, dependency_object_id)`.

4. Write `acceptance_block`'s docstring stating in plain sentences that this
   function decides what is blocked and nothing decides it twice; that it
   returns a list rather than raising so a caller can report every blocked
   dependent at once; that plan 15B-04's acceptance functions are what turn a
   non-empty list into a refusal before any write; and that no path in this
   module rebuilds a stale derivative, because RELIABILITY-03's Degraded clause
   says blocked until reconciled, not rebuilt and accepted.

5. Add `build_reconciliation_case(dest)` to `fixtures/corpus_15b.py`, returning
   a dict with the keys `rows`, `dispositions`, `live_fingerprints`, and
   `second_edit_fingerprint`, so the superseded-disposition case is a fixture
   rather than test-local scaffolding and plan 15B-07's tracer can reuse it.

6. Run the full local suite once: `for t in tests/*.py; do python "$t" || exit 1; done`
   and confirm exit 0, so a change to `blueprint.py` that broke an earlier plan's
   assertions is caught here rather than at the freeze gate.
  </action>
  <verify>
  <automated>python tests/blueprint_roundtrip.py && python itembank.py guard .</automated>
Expected: `tests/blueprint_roundtrip.py` prints `OK blueprint_roundtrip` and
exits 0, and `guard` prints `0 offending files`. The degraded behavior this task
must prove rather than paper over is the superseded disposition: after a second
edit to the same dependency, a previously clearing review no longer clears, and
the refusal that replaces it names `blueprint.disposition_superseded` rather
than silently reusing the earlier decision or silently regenerating the
derivative. Confirm the code, both fingerprints in the message payload, and that
no write occurred.
  </verify>
  <acceptance_criteria>
- `python tests/blueprint_roundtrip.py` exits 0 with `check_staleness_blocks`
  run.
- `python -c "import blueprint; print(blueprint.acceptance_block(None,None), blueprint.acceptance_block([],[]))"`
  prints `[] []`.
- `python -c "import inspect,blueprint; print(len(inspect.signature(blueprint.acceptance_block).parameters))"`
  prints `2`.
- `python -c "import blueprint; print(hasattr(blueprint,'authoring'))"` prints
  `False`.
- `grep -v '^#' blueprint.py | grep -c -E "regenerate|rebuild"` prints `0`.
- `python -c "import blueprint; print('blueprint.stale_dependent' in blueprint.BLUEPRINT_CODES, 'blueprint.disposition_superseded' in blueprint.BLUEPRINT_CODES)"`
  prints `True True`.
- `for t in tests/*.py; do python "$t" || exit 1; done` exits 0.
- `python itembank.py guard .` prints `0 offending files`.
- None of `blueprint.py`, `fixtures/corpus_15b.py`, or
  `tests/blueprint_roundtrip.py` contains an em dash character.
  </acceptance_criteria>
  <precondition>Task 1 is green and `STALENESS_DISPOSITIONS`, `staleness_report`, and `disposition_record` exist on `blueprint.py`.</precondition>
  <reversibility rating="reversible">`acceptance_block`'s refusal shape is
  internal to this phase and is consumed only by plan 15B-04's acceptance
  functions and plan 15B-07's tracer; changing it costs one edit in each.</reversibility>
  <done>A stale dependent is refused by name, a matching reviewer disposition
  clears exactly its own row, a second change to the same dependency supersedes
  the earlier review rather than inheriting it, and no code path in this module
  can rebuild a stale derivative.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| dependency on disk to staleness verdict | The live fingerprint is read by the caller at the moment of the check; a value read earlier and carried forward would authorize an acceptance against a change nobody saw. |
| reviewer disposition to cleared block | A recorded disposition is the only thing that turns a refusal into a permission; its shape decides how much it may clear and for how long. |
| stale dependent to durable acceptance | A change to a source, an objective, or a version reaches a durable write only through a recorded reviewed decision. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-15B-03-01 | Tampering | a stale dependent accepted because the content still passed the gates | high | mitigate | `acceptance_block` emits one `blueprint.stale_dependent` refusal per unmatched stale row, and plan 15B-04's acceptance functions raise on a non-empty list before any write; the block is computed from the rows, never from the content's gate results. |
| T-15B-03-02 | Tampering | a stale derivative silently rebuilt instead of reviewed | high | mitigate | `blueprint.py` does not import `authoring` and cannot reach any generator; `hasattr(blueprint, "authoring")` is `False`, `acceptance_block` has exactly two parameters so no regeneration callable can be passed in, and a source scan for `regenerate` and `rebuild` returns zero non-comment lines. |
| T-15B-03-03 | Spoofing | an agent recording its own staleness disposition | high | mitigate | `disposition_record` refuses any `reviewer_role` other than the literal `reviewer` with `blueprint.disposition_reviewer_required`, citing RELIABILITY-03's "Authority: reviewer for rebinding". |
| T-15B-03-04 | Elevation of Privilege | one recorded review clearing every future change to the same dependency | high | mitigate | A disposition carries the `current_fingerprint` it was recorded against, and a row whose live fingerprint has moved past it produces a `blueprint.disposition_superseded` refusal naming both values. |
| T-15B-03-05 | Tampering | an absent base fingerprint reading as fresh | high | mitigate | `classify_staleness` returns `True` for `None` and for the empty string on either side, including for two empty strings; four separate assertions cover the absent cases. |
| T-15B-03-06 | Tampering | a cached staleness boolean trusted after the dependency moved | high | mitigate | The verdict is derived on every call from two supplied arguments; `blueprint.py` writes nothing, which the existing structural import bans make a property rather than a promise. |
| T-15B-03-07 | Spoofing | a malformed disposition dict clearing a block | medium | mitigate | A disposition whose keys do not form a superset of `DISPOSITION_KEYS` is skipped during matching and the row it would have cleared is still refused, asserted directly. |
| T-15B-03-08 | Tampering | a fingerprint normalized before comparison, letting two different digests compare equal | medium | mitigate | Comparison is plain string inequality with no case folding, no stripping, and no Unicode normalization; the case and leading-whitespace cases are each asserted to read stale. |
| T-15B-03-09 | Information Disclosure | real source content entering the repository through the staleness fixture | high | mitigate | `build_staleness_fixture` and `edit_source` write fictional fixed-seed content only, and `python itembank.py guard .` is in both tasks' acceptance criteria. |
| T-15B-03-10 | Tampering | supply chain: a hashing or diff dependency added for fingerprint comparison | high | mitigate | None is added; the comparison is string inequality and the fingerprints are produced by the already-shipped `identity.object_fingerprint`. Per `PLANNING-DIRECTIVES.md` section 4a the absence of dependencies is explicitly not the mitigation: any dependency ever added here is vendored at a pinned version with a recorded checksum and a named license review. |
| T-15B-03-11 | Denial of Service | a large dependent list making the block quadratic | low | accept | Matching walks the disposition list once per stale row, which is quadratic in the worst case over a repository-local list a human authored. Accepted because the input is local and a slow block is a loud local failure with no data at risk. |
</threat_model>

<out_of_scope>
Refused by this plan, by name, so no adjacent temptation is decided by executor
judgment:

- No acceptance function. `graph.accept_migration`, `graph.reject_migration`,
  `course.accept_migration`, and `director.accept_revision` are plan 15B-04's.
  This plan decides what is blocked; it raises nothing and writes nothing.
- No rebuild, regeneration, or refresh of a stale derivative, under any name,
  in any function, in this phase.
- No `DRAFT_STATES` tuple and no seven-member artifact lifecycle enum. Plan
  15B-01's decision table locked that: each object kind keeps its own narrow
  closed state set.
- No fourth coverage-state vocabulary. This plan mints a disposition
  vocabulary, which is a different axis from coverage, and it asserts the two
  do not intersect rather than assuming it.
- No change to `schemas/audit_report.schema.json`'s `stale` field or to
  `$defs.coverage_row`'s six-member `state` enum. Phase 11's staleness
  representation for its own object kind stays exactly as shipped.
- No durable storage of a staleness verdict, a stale flag, or a reconciliation
  timestamp anywhere.
- No CLI command and no daemon route.
</out_of_scope>

<flagged_assumptions>
Surfaced, not silently dropped, per the spec-less probe fallback protocol.

- **RELIABILITY-03, unclassified edge row (unresolved).** The deterministic
  edge probe could not classify RELIABILITY-03 into any of its eight shape
  categories, so no acceptance criterion was derived from that row and none is
  invented here. What this plan does cover, from the requirement's own text
  rather than from the probe: the requirement's Fixture sentence is implemented
  by plan 15B-07's `scenario_staleness_blocks`, its Degraded clause is
  implemented by Task 2's `acceptance_block`, and its four disposition words
  are transcribed in Task 1. The probe row itself is carried forward as an open
  assumption for the phase verifier to review by hand, and plan 15B-07's freeze
  record repeats it in its Open items section rather than closing it.
- **The reviewer role is a string, not an authenticated identity (assumption,
  recorded).** `disposition_record` refuses any `reviewer_role` other than
  `reviewer`, but nothing in this single-learner local product authenticates
  that the caller is one. This is the same authority model
  `journal.commit_operation`'s `origin` already carries, where a caller passing
  an empty actor name records an empty name honestly. Recorded so the freeze
  record does not imply a stronger guarantee than the code makes.
</flagged_assumptions>

<summary_obligations>
`15B-03-SUMMARY.md` records: which truth was verified by which command, with
the command's actual stdout; the exact `BLUEPRINT_CODES` tuple after this
plan's five additions, so plan 15B-07's freeze record can enumerate it; the
measured wall-clock time of one full `tests/blueprint_roundtrip.py` run; the
full-suite result from Task 2 step 6; whether the unclassified RELIABILITY-03
probe row is still unresolved; and any deviation from this plan with its
reason.
</summary_obligations>

<output>
Create
`.planning/phases/15B-quality-blueprint-acceptance/15B-03-SUMMARY.md`
when done.
</output>
