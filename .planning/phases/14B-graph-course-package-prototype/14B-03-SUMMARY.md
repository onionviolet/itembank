# 14B-03 summary: bindings, the rights gate, overlays, and the version migration

**Executed 2026-08-26.** Sources and treatments bind to objectives, rights are
enforced at the moment of the binding rather than at export, an imported scope
is immutable by construction, and the version migration section 3a asks for is
prototyped rather than promised.

## Which truth was verified by which command

| Truth | How | Result |
|---|---|---|
| Rights are enforced at the binding, not only at export | `bind_source` against meridian, whose seven rights are all unknown | `course.rights_not_granted`, naming the source, `read`, `unknown`, and `next safe action: record` |
| A refused binding writes nothing | sidecar bytes and journal entry count compared across the refusal | both unchanged |
| Unknown stays restrictive and never relaxes | every binding against a freshly minted source | refuses until a grant is recorded |
| A granted right never implies another | orrery, whose `quote` is granted and `read` is unknown | `bind_source` still refuses |
| A recorded grant unblocks exactly one operation | `grant_right(read)` then `bind_source` | one revision, one `## Bindings` row, snapshot `granted` |
| A treatment consumes the right its kind maps to | `guided-lesson` against lantern's granted `transform` | succeeds |
| The wrong right refuses by name | `excerpt` (maps to `quote`) against the same source | refuses naming `quote` |
| Direct reading is a treatment, not a free pass | `direct-reading` against an unknown `read` | refuses |
| A stale snapshot never authorizes | revoke `read`, then bind a second objective | refuses naming `denied` while the earlier row still reads `granted` |
| An unregistered object cannot be bound | binding `"0" * 16` | `course.unknown_source` |
| The treatment vocabulary is closed | `treatment_right("flashcards")`, `add_binding(treatment_kind="flashcards")` | `graph.unknown_treatment_kind`, message contains `eleven` |
| Coverage is reported, never claimed | `BINDING_STATES` membership, and an unrecognized state read | no `verified`, no `assumed`; degrades to `unknown`, never `covered` |
| The derived title cell is not load-bearing | a source's derived `title` edited to a wrong value, then a treatment bound | binds successfully through the minted id alone |
| An imported scope is immutable | the serialized objectives line for the import compared character for character across an overlay | identical |
| A local edit is an overlay with its own identity | `overlay_objective` | new minted id, `origin` local, `overlays` naming the import, one `## Migrations` row with kind `overlay` and state `proposed` |
| There is no in-place edit path for an import | `add_objective(..., objective_id=<imported id>)` | `graph.imported_objective_immutable` |
| Overlays chain and nothing is deleted | overlaying the overlay | three rows, the first two byte-identical, the newest projected once |
| A future version is refused before any field is read | a version-2 fixture given a deliberately malformed `## Edges` section | `graph.future_schema_version`, not `graph.malformed_section` |
| An older version upgrades forward through a named step | `parse_course` of the version-0 fixture | header reads 1, `upgraded_from` is 0, every edge `override` is `advisory` |
| An upgrade preserves what it could not read | the version-0 fixture's `## Cohorts` section after upgrade and re-serialize | emitted unchanged |
| A gap in the upgrade chain is named, never skipped | `upgrade_document(doc, 7)` | `graph.unknown_upgrade_path` |
| No real content entered the repository | `python3 itembank.py guard .` | `0 offending files` |
| The published schema still checks in whole | `python3 schema_validate.py --all` | exit 0 |

## The assertions were falsified before they were trusted

Two invariants were deliberately broken. Changing the gate from
`identity.rights_granted` to a `!= "denied"` test, the classic bug in which
unknown quietly reads as permitted, was caught by the all-unknown refusal
assertion. Making `overlay_objective` also rewrite the imported row's statement
was caught by the character-for-character comparison of the imported line. A
green test that asserts nothing is worse than no test.

## Deviations from this plan, with reasons

1. **`graph.validate_binding` was added and is not in the plan's artifact
   list.** The plan requires an unrecognized binding state to degrade to
   `unknown` "on read", which needs a read function; the artifact list names
   none. It mirrors `validate_edge` exactly, and the expected `public_api()`
   list in the test was extended in the same commit, which is the discipline
   that list exists to enforce.
2. **`add_objective` gained two parameters, `import_version` and
   `objective_id`.** The plan asserts that calling `add_objective` "with an
   existing imported objective's id in a way that would rewrite it" raises, and
   the function had no id parameter to pass. `objective_id` is the way that
   rewrite is expressed, and it is refused for an imported row.
3. **The schema's binding, treatment, state, and origin enums already landed in
   plan 14B-02.** That plan's Task 3 directed writing the sets "plan 14B-03
   will use", so they were written then. Nothing was added to the schema here.
4. **`fixtures/corpus_14b.py` now writes each source file before recording it**
   with `journal.commit_operation(operation="link", write_target=False)`. As
   written in plan 14B-02 the link was recorded first and the file written
   after, which left the registry holding a `None` fingerprint against real
   bytes on disk, so `journal.object_state` would have read `conflict` for
   every corpus source. Found while building the revocation helper, which needs
   a valid expected fingerprint to commit against.
5. **`grant_right` and `revoke_right` are fixture helpers, not one helper.**
   The plan names only `revoke_right`; the rights test also needs to grant
   `read` on orrery before it can revoke it, so both wrap one private
   `_set_right`.
6. **The plan's final acceptance criterion, `for t in tests/*.py; do python
   "$t" || exit 1; done` exits 0, does not hold and cannot.** Three suites
   (`day_roundtrip.py`, `retention_ui_roundtrip.py`, and `phase_062_audit.py`
   which reports the first two) assert the exact copy printed with Anki closed,
   and Anki is running on this machine. Verified pre-existing in
   `14B-01-SUMMARY.md` by stashing every change and re-running on the clean
   tree. 72 of 75 pass and no new failure was introduced.
7. **One weak assertion inherited from plan 14B-01 was corrected here.**
   `check_thin_slice` tested `if not journal.entries(stub_root)`, and
   `journal.entries` returns a generator, which is always truthy. It now tests
   `list(...)`. The assertion had no teeth as written and passes with teeth
   now.

## An observation worth recording, outside this plan's scope

Running the full suite rewrites a tracked planning file:
`.planning/phases/14A-identity-lifecycle-operation/14A-TRACER-REPORT.md`
re-records its own measured timings on every run, so `git status` reports it as
modified after any suite run by anyone. It was reverted here rather than
committed, because re-recording 14A's performance measurements is not part of
this plan. Whether that file should be regenerated on every run, or written
only when the tracer is invoked deliberately, is a question for whoever owns
14A's tracer.
