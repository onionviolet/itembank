---
phase: 14B-graph-course-package-prototype
plan: 05
type: execute
wave: 5
depends_on: ["14B-04"]
files_modified:
  - course_package.py
  - fixtures/corpus_14b.py
  - tests/course_package_roundtrip.py
  - .planning/phases/14B-graph-course-package-prototype/14B-DECISIONS.md
autonomous: false
requirements: [PORT-03]
must_haves:
  truths:
    - "Export is not complete until a clean-machine, offline restore validates the manifest: the restore drill runs against a destination with no shared journal, no shared registry, no shared evidence store, and no shared settings, and it recomputes every payload fingerprint rather than trusting the manifest's own claim (PORT-03)."
    - "Every loss is reported by name and never silently dropped: a linked external source, a rights-restricted source, machine-local settings, an unreachable source root, and an unsupported object kind each produce a named row in the loss report with its category, its target, and its reason (PORT-03 degraded clause)."
    - "Unknown rights do not relax at export: a source whose package right is unknown or denied is excluded from the payload and named in the loss report under rights-restricted, and no code path in course_package.py writes a payload for a source whose package right is not the exact string granted (RIGHTS-01)."
    - "A restore gap is reported against the manifest and never silently accepted: a missing payload, a fingerprint mismatch, and an entry whose relative path escapes the destination each produce a named refusal or a named restore-loss row, distinct from the export-time loss report, and both reports are returned."
    - "Two payload entries with identical fingerprints and different object ids are packaged separately and appear as two manifest entries; they are never deduplicated into one payload file. Two manifest entries claiming the same relative path are refused with package.duplicate_relpath (PORT-03 adjacency edge)."
    - "Exporting a course with zero objectives and zero bound sources produces a valid package whose entries list holds exactly the course sidecar, an evidence export file that is present and zero bytes rather than absent, and a loss report whose body is the single line No losses.; restoring it succeeds and reports zero losses (PORT-03 empty edge)."
    - "Output order is specified and stable when elements compare equal: manifest entries are sorted by kind then object_id, and loss report rows by category then target, so two exports of the same unchanged course produce byte-identical manifests apart from package_id and created (PORT-03 ordering edge)."
    - "A package archive is untrusted input the moment it crosses a machine boundary: every extracted entry's target is resolved and contained before anything is written, an escaping entry is refused by name and never clamped to a safe path, a symbolic-link entry is refused, and the file the escaping entry named does not exist on disk afterward."
    - "Restoring evidence goes through the one evidence writer: a second restore of the same package records zero new events and reports every event as already recorded, so a restore is idempotent and no second evidence store is created."
  prohibitions:
    - statement: "A package must not silently omit rights-restricted, unreachable, or unsupported material; every omission is named in the loss report with its reason."
      status: kept
      verification: flagged-unverified
    - statement: "Unknown rights must not relax to permissive at export, at packaging, or at restore."
      status: kept
      verification: flagged-unverified
  artifacts:
    - "course_package.py gains build_manifest, loss_report_text, verify_manifest, restore of evidence, and the optional archive transport with its containment guard"
    - "tests/course_package_roundtrip.py, the PORT-03 assertion file"
    - "fixtures/corpus_14b.py gains clean_machine_dest and a hand-built traversing archive"
  key_links:
    - "The manifest is written with state prepared before any payload and flipped to applied only after every payload re-verifies, the audit_writer.py shape. If a later change flips it first, an interrupted export becomes indistinguishable from a complete one and restore_package's package.not_applied refusal stops protecting anything."
    - "restore_package must recompute identity.object_fingerprint for each payload rather than reading the manifest's recorded value back to itself. A restore that trusts the manifest is not a validated restore, and PORT-03's whole clause is about validation."
    - "course_package.py imports evidence for the export and the restore, and that is correct: evidence.append_event is the one evidence writer. course.py still must not import it. The two modules have different jobs and the boundary is asserted in both directions."
---

<objective>
Land PORT-03: export a synthetic course as a package, restore it on a machine
that never saw the original, validate every entry against the manifest, and
report every loss by name. The requirement's own sentence is the acceptance
bar: "Export is not complete until a clean-machine, offline restore validates a
manifest and reports every loss, restoring all supported canonical objects and
evidence."

This plan carries the one place in Phase 14B where the project's
single-local-user threat posture stops applying. `evidence.py`'s own module
docstring records that fingerprints here are change detection and not a security
boundary, and that is right for locally authored content. A package a learner
receives from someone else is different: the amended Users constraint in
`.claude/CLAUDE.md`, recorded 2026-08-14, makes external installations a
supported goal, and a package crossing a machine boundary is untrusted input
from that moment. The Zip Slip guard in this plan is therefore real and not
defensive theater.

Decisions already made, cited, and never re-derived here:

- **PORT-03**, verbatim above, including its Degraded clause: "a restore gap is
  reported against the manifest, not silently accepted".
- **RIGHTS-01**: rights are operation-specific and `package` and `export` are
  two of the seven; unknown stays restrictive. Phase 14B reuses
  `identity.rights_state` and `identity.rights_granted` and invents no second
  rights vocabulary.
- **`14B-RESEARCH.md` Pattern 6**: a BagIt-inspired manifest hand-rolled in the
  standard library, with the package as a plain directory tree first and an
  archive only as optional transport. The Alternatives Considered table records
  the real cost of a `bagit` dependency rather than rejecting it on principle,
  per `PLANNING-DIRECTIVES.md` section 4a.
- **`14B-RESEARCH.md` Pattern 6 loss categories**: absolute local paths,
  rights-restricted material, machine-local settings, and unreachable external
  sources, each named rather than silently dropped.

Decisions this plan makes and locks:

| Open question | Locked answer | One-line rationale |
|---|---|---|
| Package default form | A plain directory tree. `archive="zip"` is optional transport and never the source of truth | If the archive were the default, the traversal guard would be load-bearing on the ordinary path rather than on an opt-in one; `14B-RESEARCH.md` Assumption A5 names this and says the guard is tested either way, which this plan does. |
| Which right gates payload inclusion | `package`. A source whose `package` right is not the exact string `granted` is excluded and named | RIGHTS-01 lists `package` as one of the seven operation-specific rights; using `export` instead would conflate handing a file to a person with writing it into a bundle. |
| Where a linked source goes | Not into the payload. A `link` operation preserves external identity and location and copies nothing, so a linked source is a loss-report row under `external-link` | `14A-03-PLAN.md`'s `op_link` mints an object id and records a fingerprint and path without writing the target; a package that silently inlined it would change what `link` means. |
| Machine-local settings | Never included, and always named in the loss report under `machine-local` as not included by design | `14B-RESEARCH.md` Pattern 6's table: a restore must not silently assume settings travelled. |
| Restore of evidence | Through `evidence.append_event`, the one evidence writer, one event at a time, reporting the `recorded` and `already_recorded` counts it returns | Non-negotiable 2 forbids a second evidence store, and `append_event`'s own contract already answers which of the two happened, so a second restore is idempotent for free. |
| Clean machine, simulated honestly | A destination temp directory containing nothing, with `HOME`, `APPDATA`, and `XDG_DATA_HOME` pointed at a second empty temp directory for the duration, and an assertion that `course_package.py` exposes no network module at all | A restore that quietly read the exporting machine's registry or settings would pass a fake drill; pointing the environment away and asserting the module has no network attribute makes the drill honest. |

Purpose: an export that has never been restored is a promise, not a backup.
Output: the package layer, the loss report, the clean-machine restore drill, and
the traversal guard.
</objective>

<context>
@.planning/phases/14B-graph-course-package-prototype/14B-RESEARCH.md
@.planning/phases/14B-graph-course-package-prototype/14B-PATTERNS.md
@.planning/phases/14B-graph-course-package-prototype/14B-04-PLAN.md
@.planning/PLANNING-DIRECTIVES.md
@audit_writer.py
@evidence.py
</context>

## Artifacts this phase produces (plan 14B-05 share)

Added to `course_package.py`. Every symbol below is new in this phase.

- Constants: `EVIDENCE_DIRNAME = "evidence"`,
  `EVIDENCE_FILENAME = "evidence_export.jsonl"`,
  `LOSS_REPORT_FILENAME = "LOSS-REPORT.md"`,
  `LOSS_CATEGORIES = ("external-link", "rights-restricted", "machine-local",
  "unreachable-source", "unsupported-kind")`,
  `PACKAGE_RIGHT = "package"`, `PACKAGED_KINDS = ("course", "objective",
  "source", "lesson", "bank")`, `ARCHIVE_FORMATS = (None, "zip")`.
- Functions: `build_manifest(base, course_root)`, `loss_report_text(manifest)`,
  `verify_manifest(package_root)`, `extract_archive(archive_path, dest)`.
  `export_package` and `restore_package`, created in plan 14B-01, gain their
  `archive`, evidence, and loss-report behavior here.
- New `PackageError` codes: `package.duplicate_relpath`,
  `package.missing_payload`, `package.manifest_unreadable`,
  `package.symlink_payload`, `package.unsupported_archive`.

New test file: `tests/course_package_roundtrip.py`, a direct-execution script,
exit 0 on pass.

New fixture entry points in `fixtures/corpus_14b.py`:
`clean_machine_dest(tmp)` returning a destination directory plus the
environment overrides to apply, `build_traversing_archive(path)` writing a zip
whose entry name escapes its root, and `build_symlink_archive(path)`.

No CLI command, no daemon route, and no journal record type is produced by this
plan. `restore_package` journals with `operation="restore"`, a record type
Phase 14A already reserved.

<tasks>

<task type="checkpoint:decision" gate="blocking">
  <name>Task 1: the package manifest format</name>
  <files>.planning/phases/14B-graph-course-package-prototype/14B-DECISIONS.md</files>
  <read_first>
- `14B-RESEARCH.md` "Pattern 6" in full, including the package tree diagram,
  the loss-category table, and the Security note paragraph on why the package
  is a plain directory tree first; plus Assumption A5 and the Alternatives
  Considered row for `bagit`.
- `course_package.py` as it stands after plan 14B-01: `MANIFEST_ENTRY_KEYS`,
  `PACKAGE_STATES`, `export_package`, `restore_package`, `safe_target`.
- `.claude/CLAUDE.md` Constraints, the Users bullet as amended 2026-08-14, and
  the ROADMAP Phase 18 entry, for what an external installation means for a
  package that leaves this machine.
- `.planning/PLANNING-DIRECTIVES.md` section 4a, the Supply chain paragraph, in
  full. It governs what option-c would cost.
- `.planning/phases/14B-graph-course-package-prototype/14B-DECISIONS.md`, so
  the new section is appended.
  </read_first>
  <decision>
What exactly does `manifest.json` contain, and is the package a plain directory
tree with an optional archive, or an archive by default?
  </decision>
  <context>
This is rated one-way. A manifest is the thing a restore validates against, and
a package may be handed to another person under the external-installation goal
recorded in the amended Users constraint in `.claude/CLAUDE.md`. Once a package
exists on another machine, changing the manifest key set means either a
migration or a package that the receiving build cannot read. The archive-versus-
directory choice additionally decides whether the path-traversal guard is on the
default path or on an opt-in one.
  </context>
  <options>
    <option id="option-a">
      <name>RECOMMENDED DEFAULT: plain directory tree, seven-key manifest, zip as optional transport</name>
      <pros>`manifest.json` carries `schema_version`, `package_id`, `created`,
      `course_object_id`, `state`, `entries`, and `loss_report`. Each entry
      carries the five keys `object_id`, `kind`, `revision`, `relpath`, and
      `fingerprint`. The package is a directory a human can open and read, which
      matches the authorability posture the whole phase is judged on. The
      traversal guard is still built and still tested, because a zip transport
      exists. This is `14B-RESEARCH.md` Pattern 6 and Assumption A5.</pros>
      <cons>Handing a course to someone means handing them a folder, so a
      separate archive step exists for transport.</cons>
    </option>
    <option id="option-b">
      <name>Archive by default</name>
      <pros>One file to hand over. Simplest to email or copy.</pros>
      <cons>The traversal guard becomes load-bearing on every restore rather
      than on an opt-in path, and a human cannot read the package without
      unpacking it, which weakens the same authorability property the sidecar
      format was chosen for.</cons>
    </option>
    <option id="option-c">
      <name>BagIt proper, with the `bagit` dependency</name>
      <pros>Interoperability with external digital-preservation tooling.
      Nothing hand-rolled.</pros>
      <cons>A multi-file general-purpose format and a new dependency for a
      narrow, project-specific need. `14B-RESEARCH.md` records the real cost
      rather than rejecting it on principle: the dependency would need
      vendoring at a pinned version with a recorded checksum and a named license
      review, and there is no named external consumer yet. Revisit when one
      exists.</cons>
    </option>
  </options>
  <action>
Ask Weibao the question above with all three options and the recommended
default named, and record the answer verbatim in
`.planning/phases/14B-graph-course-package-prototype/14B-DECISIONS.md` under a
dated heading `## D-14B-4. The package manifest format`.

What the executor does with each answer:

- **option-a**: proceed as Tasks 2 and 3 are written.
- **option-b**: before Task 2, change `export_package`'s default `archive`
  value to `"zip"`, move the traversal and symlink assertions in Task 3 from
  the optional-transport section to the default path, and record in
  `14B-DECISIONS.md` that the authorability review in plan 14B-06 must now
  cover reading a package after unpacking it.
- **option-c**: STOP. Do not add the dependency in this plan. Record the answer
  and re-run the package legitimacy gate protocol against `bagit`, then bring
  the result back as a new decision. `14B-RESEARCH.md`'s Package Legitimacy
  Audit was skipped because this phase proposes zero external packages; that
  audit must exist before any package is installed.

Do not proceed with a silent default. An unanswered checkpoint stops the wave.
  </action>
  <verify>
`14B-DECISIONS.md` contains a dated `## D-14B-4` heading naming exactly one of
`option-a`, `option-b`, or `option-c`, with Weibao's answer recorded verbatim.
  </verify>
  <acceptance_criteria>
- `.planning/phases/14B-graph-course-package-prototype/14B-DECISIONS.md`
  contains the literal heading `## D-14B-4. The package manifest format`.
- The recorded answer names exactly one of `option-a`, `option-b`, `option-c`.
- The file contains no em dash character.
  </acceptance_criteria>
  <reversibility rating="one-way">A manifest a receiving build validates
  against becomes a published contract the moment a package crosses a machine
  boundary. Changing the key set afterwards means a migration or an unreadable
  package.</reversibility>
  <resume-signal>Reply with `option-a`, `option-b`, or `option-c`.</resume-signal>
</task>

<task type="auto" tdd="true">
  <name>Task 2: the manifest, the rights gate on packaging, and the named loss report</name>
  <files>course_package.py, fixtures/corpus_14b.py, tests/course_package_roundtrip.py</files>
  <read_first>
- `course_package.py` as delivered by plan 14B-01: `safe_target`,
  `export_package`, `restore_package`, `MANIFEST_ENTRY_KEYS`, `PACKAGE_STATES`.
- `audit_writer.py` lines 246 to 265 (`_write_bytes_atomic`) and lines 346 to
  402 (`_write_shadow`'s prepared-manifest-before-mutation, atomic replace, and
  after-fingerprint guard). This is the exact shape `export_package` follows.
- `journal.py` as landed: `read_registry`, `read_object`, `object_state`.
- `identity.py` as landed: `rights_state`, `rights_granted`, `registry_rows`,
  `object_fingerprint`.
- `.planning/REQUIREMENTS.md` PORT-03 and RIGHTS-01, in full, including their
  Fixture sentences.
- `14B-RESEARCH.md` "Pattern 6" in full, including the loss-category table.
- `tests/durability_roundtrip.py` lines 44 to 63 and 185 to 239, for the
  subprocess spawn-and-kill harness this task reuses to interrupt an export.
  </read_first>
  <behavior>
Assertions in the new `tests/course_package_roundtrip.py`, written before the
code, using the same local `fail(msg)` helper convention every existing
roundtrip test defines for itself.

The manifest:

- `course_package.build_manifest(base, course_root)` returns a dict with exactly
  the seven keys `schema_version`, `package_id`, `created`, `course_object_id`,
  `state`, `entries`, and `loss_report`.
- Every entry's key set equals `set(course_package.MANIFEST_ENTRY_KEYS)`.
- `schema_version` equals `course_package.PACKAGE_SCHEMA_VERSION`, which is `1`.
- Every entry's `fingerprint` equals
  `identity.object_fingerprint(<payload bytes>, entry["kind"])`.
- Only kinds in `course_package.PACKAGED_KINDS` produce an entry; an object of
  any other kind produces a loss-report row with category
  `unsupported-kind`.

The rights gate on packaging (RIGHTS-01):

- The `meridian-field-response` source, whose seven rights are all `unknown`:
  no payload file is written for it, and the loss report has one row with
  category `rights-restricted`, `target` equal to its object id, and a `reason`
  containing the strings `package` and `unknown`.
- The `lantern-computing` source, whose `package` right is `denied`: same
  treatment, with `denied` in the reason.
- A source whose `package` right is set to `granted` IS written to the payload
  and produces a manifest entry and no loss row.
- A source whose `transform` right is `granted` but whose `package` right is
  `unknown` is still excluded. A granted right does not imply another.
- Structural: `course_package.py` contains one call path that decides payload
  inclusion, and it goes through `identity.rights_granted(rights,
  course_package.PACKAGE_RIGHT)`. Asserted behaviorally by the four cases above.

The loss report, every category named (PORT-03 degraded clause):

- `course_package.LOSS_CATEGORIES` equals `("external-link",
  "rights-restricted", "machine-local", "unreachable-source",
  "unsupported-kind")`.
- A source registered through `journal.op_link`, so owned externally, produces
  exactly one row with category `external-link` whose reason contains the
  words `linked, not imported`.
- A machine-local settings row is always present with category `machine-local`,
  `target` equal to the string `settings`, and a reason containing the words
  `not included by design`. It is present even when nothing else is lost,
  because a restore must not silently assume settings travelled.
- A source whose recorded root does not exist at export time produces one row
  with category `unreachable-source`.
- `course_package.loss_report_text(manifest)` returns Markdown beginning with
  the exact line `# Package loss report`, then a blank line, then a table with
  the column headers `category`, `target`, and `reason`.
- With zero loss rows, `loss_report_text` returns the heading, a blank line, and
  the single line `No losses.` and nothing else.
- `LOSS-REPORT.md` is written into the package root and its content equals
  `loss_report_text(manifest)`.

Ordering and adjacency (PORT-03 ordering and adjacency edges):

- `manifest["entries"]` is sorted by `(kind, object_id)`, the same rule
  `identity.registry_rows` uses, and the order is identical across two exports
  of the same unchanged course with the registry's iteration order shuffled
  between them.
- `manifest["loss_report"]` rows are sorted by `(category, target)`.
- Two exports of the same unchanged course produce manifests that are
  byte-identical after removing the `package_id` and `created` values.
- Two source objects with identical fingerprints and different object ids
  produce TWO payload files and TWO manifest entries. They are never
  deduplicated into one payload, because two ids are two objects.
- A manifest constructed with two entries claiming the same `relpath` raises
  `PackageError` with code `package.duplicate_relpath` when passed to
  `export_package`.

The empty case (PORT-03 empty edge):

- Exporting a course with zero objectives, zero sources, and zero bindings
  succeeds. `manifest["entries"]` has exactly one member, the course sidecar
  itself.
- `evidence/evidence_export.jsonl` exists and is zero bytes. It is present and
  empty, never absent, so a restore can tell "no evidence" from "evidence
  missing".
- `LOSS-REPORT.md` body is the single line `No losses.` apart from the
  `machine-local` row, which is always present; assert the report has exactly
  one row and it is the `machine-local` one.
- Restoring that package succeeds, reports `entries_verified` `1`, and reports
  zero restore losses.

Crash safety:

- Killing an `export_package` subprocess between the prepared manifest write and
  the payload write, using the `tests/durability_roundtrip.py` harness, leaves a
  `manifest.json` whose `state` is `prepared`, and a later
  `restore_package` on it raises `PackageError` with code
  `package.not_applied`. Either the old valid state or the new valid state,
  never a mixed one.
  </behavior>
  <action>
1. Create `tests/course_package_roundtrip.py` first, with its own `fail(msg)`
   helper, the `ROOT` and `sys.path.insert` header convention, a
   `check_manifest_and_losses()` function holding every assertion above, and a
   `main()` that prints `OK course_package_roundtrip`. Run it and confirm it
   fails.

2. Add to `course_package.py` the constants `EVIDENCE_DIRNAME`,
   `EVIDENCE_FILENAME`, `LOSS_REPORT_FILENAME`, `LOSS_CATEGORIES`,
   `PACKAGE_RIGHT = "package"`, `PACKAGED_KINDS`, and `ARCHIVE_FORMATS`, plus
   the two new refusal codes with these exact message templates:
   - `package.duplicate_relpath`: `"two manifest entries claim the same payload
     path %s; refused"`
   - `package.missing_payload`: `"manifest entry %s names payload %s, which is
     not in the package"`

3. Implement `build_manifest(base, course_root)`. It reads
   `journal.read_registry(base)`, walks objects in `identity.registry_rows`
   order, and for each object decides one of three outcomes: include as a
   payload entry; exclude with a named loss row; or skip as an unsupported
   kind with a named loss row. Inclusion requires `identity.rights_granted(
   record.get("rights"), PACKAGE_RIGHT)` to be True, read from the CURRENT
   registry, never from a value copied elsewhere. The course sidecar itself is
   always entry one and is not rights-gated, because it is the course's own
   record rather than a bound source. Always append the `machine-local` loss
   row. Sort `entries` by `(kind, object_id)` and `loss_report` by
   `(category, target)` before returning.

4. Implement `loss_report_text(manifest)` producing exactly the shape described
   in `<behavior>`, with no em dash characters in any generated reason string.
   The reason strings this plan fixes, verbatim:
   - `external-link`: `"linked, not imported; the external file keeps its own
     identity and location and is not copied into a package"`
   - `rights-restricted`: `"the %s right for this source is %s; unknown and
     denied both stay restrictive, so this object is named here rather than
     packaged"`
   - `machine-local`: `"not included by design; model backend configuration,
     update policy, and local paths belong to the machine, not to the course"`
   - `unreachable-source`: `"the recorded root was unavailable when this
     package was built; the object is named here rather than omitted silently"`
   - `unsupported-kind`: `"kind %s is not one of the packaged kinds course,
     objective, source, lesson, bank; it is named here rather than dropped"`

5. Extend `export_package` to write `LOSS-REPORT.md` and
   `evidence/evidence_export.jsonl` alongside the manifest and the payload,
   keeping the prepared-then-applied ordering from plan 14B-01 exactly:
   manifest at `prepared`, then payload, then evidence export, then loss report,
   then re-verify every payload fingerprint, then rewrite the manifest at
   `applied`. The evidence export filters `evidence.events(log)` to events whose
   `objective` value is a sixteen-hex id present in the course document, writes
   one JSON object per line with `sort_keys=True`, and writes a zero-byte file
   when nothing matches. Refuse a duplicate `relpath` before writing anything.

6. Extend `fixtures/corpus_14b.py` with an `unreachable_root_case(dest)` helper
   that registers a source against a root and then removes the root, and a
   `duplicate_fingerprint_sources(root)` helper that registers two byte-identical
   sources with two ids.

7. Re-run the test until green, then run `python itembank.py guard .`.
  </action>
  <verify>
  <automated>python tests/course_package_roundtrip.py</automated>
Expected: prints `OK course_package_roundtrip` and exits 0. Also run
`python itembank.py guard .`, expected `0 offending files`. Degraded states
this task proves, each with its own named assertion: a source with unknown
rights is excluded and named rather than packaged or silently dropped; a denied
right behaves identically to unknown; a linked source is named rather than
inlined; an unreachable root is named rather than omitted; machine-local
settings are always named as not included by design; an unsupported kind is
named rather than skipped; a zero-loss export still produces a readable report;
and an interrupted export leaves a manifest at `prepared` that a restore
refuses.
  </verify>
  <acceptance_criteria>
- `python tests/course_package_roundtrip.py` exits 0 and prints
  `OK course_package_roundtrip`.
- `python itembank.py guard .` prints `0 offending files` and exits 0.
- `course_package.py` contains `def build_manifest(` and
  `def loss_report_text(`.
- `python -c "import course_package as p; print(p.LOSS_CATEGORIES)"` prints
  `('external-link', 'rights-restricted', 'machine-local', 'unreachable-source', 'unsupported-kind')`.
- `python -c "import course_package as p; print(p.PACKAGE_RIGHT, p.PACKAGE_SCHEMA_VERSION)"`
  prints `package 1`.
- `python -c "import course_package as p; print(p.loss_report_text({'loss_report': []}))"`
  prints the heading line, a blank line, and `No losses.`
- `course_package.py` and `tests/course_package_roundtrip.py` contain no em
  dash character.
  </acceptance_criteria>
  <reversibility rating="costly">The loss category names and the reason strings
  become the copy a receiving user reads. Changing them later is a copy change
  and not a migration, but a package already handed over carries the old
  wording.</reversibility>
  <done>An export names every object it could not carry, with its category and
  its reason, and a rights-restricted source is excluded by the same
  `identity.rights_granted` gate the bindings use.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 3: the clean-machine offline restore drill and the archive containment guard</name>
  <files>course_package.py, fixtures/corpus_14b.py, tests/course_package_roundtrip.py</files>
  <read_first>
- `course_package.py` as it stands after Task 2, especially `safe_target` from
  plan 14B-01.
- `evidence.py` lines 95 to 105 (`evidence_dir`, `log_path`), 735 to 755
  (`append_event` and its `recorded` versus `already_recorded` contract), and
  755 to 774 (`events`).
- `discovery.py` as landed, specifically `inside_any_root`, the containment
  check this task reuses rather than writing a second one.
- `14B-RESEARCH.md` "Pattern 6", the Security note paragraph beginning "this is
  the load-bearing reason the package is a plain directory tree first", and the
  Security Domain table's Zip Slip row, in full.
- `.claude/CLAUDE.md` Constraints, the Users bullet as amended 2026-08-14, for
  why a package from another person is untrusted input.
  </read_first>
  <behavior>
Assertions added to `tests/course_package_roundtrip.py` in a new
`check_clean_restore()` function and a `check_archive_containment()` function,
written before the code.

The clean machine, honestly simulated:

- `fixtures.corpus_14b.clean_machine_dest(tmp)` returns a destination directory
  that contains nothing, plus a dict of environment overrides for `HOME`,
  `APPDATA`, and `XDG_DATA_HOME` pointing at a second empty temp directory.
- The restore runs with those overrides applied and with the exporting course
  root's path not present in the destination at all.
- `os.path.exists(os.path.join(dest, "_journal"))` is `False` before the
  restore, and the restore creates it. No state is shared.
- `hasattr(course_package, "urllib")`, `hasattr(course_package, "socket")`, and
  `hasattr(course_package, "http")` are all `False`. A restore is offline by
  construction, not by intention.

Validation against the manifest (PORT-03's core clause):

- `course_package.verify_manifest(package_root)` returns a dict with the keys
  `entries_verified`, `mismatches`, `missing`, and `complete`.
- On an untouched package, `complete` is `True`, `mismatches` and `missing` are
  both empty, and `entries_verified` equals the manifest entry count.
- Corrupting one byte of one payload file makes `verify_manifest` report that
  entry in `mismatches` with its expected and found fingerprints, and makes
  `restore_package` raise `PackageError` with code
  `package.fingerprint_mismatch`.
- Deleting one payload file makes `verify_manifest` report that entry in
  `missing`, and makes `restore_package` raise `PackageError` with code
  `package.missing_payload`.
- A `manifest.json` that is not valid JSON raises `PackageError` with code
  `package.manifest_unreadable`. It is never treated as an empty manifest.
- Both reports are returned from a successful restore: the report dict carries
  `losses`, copied from the manifest's export-time loss report, and
  `restore_losses`, computed during this restore. They are two separate lists
  and neither replaces the other.

Restored content and evidence:

- After the restore, `<dest>/course-graph.md` exists, its bytes equal the
  original sidecar's bytes, and `graph.parse_course` of it returns a document
  whose objective ids are the same ids.
- `journal.read_registry(dest)` after the restore holds one row per restored
  object, and `journal.entries(dest)` contains an entry whose `operation` is
  `restore`.
- Every exported evidence event is appended through `evidence.append_event`
  into the destination's own evidence log. The report's `evidence_recorded`
  equals the exported event count and `evidence_already_recorded` is `0`.
- Restoring the SAME package into the SAME destination a second time reports
  `evidence_recorded` `0` and `evidence_already_recorded` equal to the exported
  count, and `len(list(evidence.events(dest_log)))` is unchanged. The one
  evidence writer's dedupe contract makes a restore idempotent.

The archive containment guard (Zip Slip class):

- `fixtures.corpus_14b.build_traversing_archive(path)` writes a zip containing
  one entry literally named `../escape.md`.
- `course_package.extract_archive(path, dest)` raises `PackageError` with code
  `package.path_escape`, and `os.path.exists(os.path.join(dest, "..",
  "escape.md"))` is `False` afterward. The entry is refused, never clamped to a
  safe name and never silently skipped.
- The same holds for an entry named `payload/../../escape.md`, for an absolute
  entry name, and, on platforms where a drive letter is meaningful, for an
  entry name beginning with a drive specification.
- `fixtures.corpus_14b.build_symlink_archive(path)` writes a zip containing a
  symbolic-link entry; `extract_archive` raises `PackageError` with code
  `package.symlink_payload`. A package payload carries files only. If the
  platform cannot create the symlink entry, the test prints exactly
  `SKIP: symlink archive assertion (this platform cannot write a symlink zip entry)`
  and skips that one assertion rather than passing silently.
- `extract_archive` never calls `zipfile.ZipFile.extractall`. Asserted
  behaviorally: the traversing archive raises rather than writing, which
  `extractall` would not do.
- `extract_archive` with a format outside `ARCHIVE_FORMATS` raises
  `PackageError` with code `package.unsupported_archive`.
- A zip whose declared uncompressed size for one entry exceeds one hundred
  megabytes raises `PackageError` with code `package.unsupported_archive`
  naming the entry, so a decompression bomb is refused before it is written
  rather than after.
  </behavior>
  <action>
1. Add `check_clean_restore()` and `check_archive_containment()` to
   `tests/course_package_roundtrip.py` first, wired into `main()`, with every
   assertion above. Run and confirm they fail.

2. Add to `course_package.py` the three new refusal codes with these exact
   message templates:
   - `package.manifest_unreadable`: `"the manifest at %s is not valid JSON; a
     package with an unreadable manifest is refused, never treated as empty"`
   - `package.symlink_payload`: `"the package entry %s is a symbolic link; a
     package payload carries files only"`
   - `package.unsupported_archive`: `"the archive entry or format %s is not
     supported; refused"`

3. Implement `verify_manifest(package_root)` exactly as described. It
   recomputes `identity.object_fingerprint(raw, entry["kind"])` for every
   payload and compares. Its docstring states in plain sentences that a restore
   that reads the manifest's own recorded fingerprint back to itself validates
   nothing, and that PORT-03's clause is about validation.

4. Extend `restore_package` to: refuse a non-applied manifest; call
   `verify_manifest` and refuse on any mismatch or missing entry; route every
   write target through `safe_target`; write each payload atomically; register
   each restored object through `journal.commit_operation` with
   `operation="restore"`; append each exported evidence event through
   `evidence.append_event`, counting the `recorded` and `already_recorded`
   answers it returns; and return the report dict with both `losses` and
   `restore_losses`.

5. Implement `extract_archive(archive_path, dest)` using `zipfile.ZipFile` and
   iterating `infolist()` one entry at a time. For each entry: refuse a
   declared `file_size` above `104857600` with `package.unsupported_archive`;
   refuse an entry whose external attributes mark it a symbolic link with
   `package.symlink_payload`; resolve its target through `safe_target`, which
   refuses an absolute name, any `..` component, and any resolved path outside
   `dest`; then write it. Never call `extractall`. Add a comment above the loop
   stating in plain sentences that a package received from another person is
   untrusted input the moment it crosses a machine boundary, that this is the
   one place in this phase where the project's single-local-user posture stops
   applying, and citing the Zip Slip research and the amended Users constraint.

6. Extend `fixtures/corpus_14b.py` with `clean_machine_dest(tmp)`,
   `build_traversing_archive(path)`, and `build_symlink_archive(path)`. The
   traversing archive is hand-built with `zipfile.ZipFile.writestr` using a
   literal entry name, because a normal zip writer will not produce one.

7. Re-run the test until green. Then run the full suite the way CI runs it,
   then `python itembank.py guard .`.
  </action>
  <verify>
  <automated>python tests/course_package_roundtrip.py</automated>
Expected: prints `OK course_package_roundtrip` and exits 0, having printed the
named SKIP line if the platform forced a symlink-archive fallback. Then run
`for t in tests/*.py; do python "$t" || exit 1; done`, expected exit 0, and
`python itembank.py guard .`, expected `0 offending files`. Degraded states
this task proves, each with its own named assertion: a traversing archive entry
is refused and the file it named does not exist; a symlink entry is refused; an
oversized entry is refused before it is written; a corrupted payload is caught
by recomputation; a missing payload is named; an unreadable manifest is refused
rather than read as empty; a second restore records zero new events; and the
restore runs with no shared journal, registry, evidence store, or settings.
  </verify>
  <acceptance_criteria>
- `python tests/course_package_roundtrip.py` exits 0.
- `for t in tests/*.py; do python "$t" || exit 1; done` exits 0.
- `python itembank.py guard .` prints `0 offending files` and exits 0.
- `course_package.py` contains `def verify_manifest(` and
  `def extract_archive(`.
- `python -c "import course_package as p; print(hasattr(p,'urllib'), hasattr(p,'socket'), hasattr(p,'http'))"`
  prints `False False False`.
- `python -c "import course_package as p; print(p.ARCHIVE_FORMATS)"` prints
  `(None, 'zip')`.
- `course_package.py` and `fixtures/corpus_14b.py` contain no em dash
  character.
  </acceptance_criteria>
  <precondition>The destination used for the restore drill is an empty directory outside the exporting course root, and `HOME`, `APPDATA`, and `XDG_DATA_HOME` are pointed at a second empty directory for the duration of the drill.</precondition>
  <reversibility rating="reversible">The restore report's key names and the
  containment implementation are internal to this module and are not written
  into any durable artifact.</reversibility>
  <done>A package restores on a destination that shares nothing with the
  exporting machine, every entry is validated by recomputation, both loss
  reports are returned, and a hostile archive entry is refused rather than
  clamped.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| package archive to restore path | The load-bearing boundary of this plan. A package built on another machine, possibly by another person under the external-installation goal, crosses into `extract_archive` and `restore_package`. The project's single-local-user posture stops applying here. |
| source rights record to payload writer | A registry field decides whether a source's bytes are copied into a bundle that may leave the machine. |
| manifest claim to restore validation | A manifest that validated itself would validate nothing. |
| exporting machine to destination | A restore that quietly read the exporting machine's registry, settings, or evidence store would pass a fake drill. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-14B-05-01 | Tampering / Elevation of Privilege | Zip Slip: an archive entry name escaping the restore destination | high | mitigate | `extract_archive` iterates `infolist()` one entry at a time and never calls `extractall`; every target goes through `safe_target`, which refuses an absolute name, any `..` component, and any `os.path.realpath` result not contained in the destination. The refusal raises `package.path_escape` and never clamps. Asserted with a hand-built archive containing a literal `../escape.md` entry, and by checking the escaped file does not exist afterward. Cited: the Zip Slip research recorded in `14B-RESEARCH.md`'s Security Domain. |
| T-14B-05-02 | Tampering / Elevation of Privilege | symlink escape during extraction or export | high | mitigate | A symbolic-link archive entry is refused with `package.symlink_payload`; a payload carries files only. On the export side, containment reuses `discovery.inside_any_root` rather than a second, possibly weaker check. |
| T-14B-05-03 | Information Disclosure | rights-restricted material leaking into a package that leaves the machine | high | mitigate | Payload inclusion requires `identity.rights_granted(rights, "package")` to be exactly True, read from the current registry; unknown and denied are both excluded and both named in the loss report. Asserted against sources with unknown, denied, and granted values, and against a source granted `transform` but not `package`. |
| T-14B-05-04 | Tampering | a corrupted or substituted payload restored as authentic | high | mitigate | `verify_manifest` recomputes `identity.object_fingerprint` for every payload before anything is written; a mismatch raises `package.fingerprint_mismatch` naming expected and found. Asserted by corrupting one byte. |
| T-14B-05-05 | Tampering | an interrupted export restored as if complete | high | mitigate | The manifest is written at `prepared` before any payload and flipped to `applied` only after every payload re-verifies; `restore_package` refuses a non-applied manifest with `package.not_applied`. Asserted with the `tests/durability_roundtrip.py` kill harness. |
| T-14B-05-06 | Denial of Service | a decompression bomb in a received archive | high | mitigate | Every entry's declared uncompressed size is checked against a fixed one hundred megabyte ceiling before it is written, refusing with `package.unsupported_archive` naming the entry. |
| T-14B-05-07 | Spoofing | an unreadable or truncated manifest silently treated as an empty package | medium | mitigate | `package.manifest_unreadable` refuses invalid JSON by name rather than defaulting to an empty entry list. |
| T-14B-05-08 | Information Disclosure | a restore drill that quietly read the exporting machine's state and therefore proved nothing | high | mitigate | The destination is an empty directory outside the exporting root, `HOME`, `APPDATA`, and `XDG_DATA_HOME` are redirected for the duration, and `course_package.py` is asserted to expose no `urllib`, `socket`, or `http` attribute so the restore is structurally offline. |
| T-14B-05-09 | Repudiation | a loss that is real but unreported, so the restored course looks complete | high | mitigate | Five named loss categories, each with a fixed reason string; the `machine-local` row is always present even on a zero-loss export; export-time and restore-time losses are two separate lists and both are returned. This is the prohibition recorded in this plan's `must_haves.prohibitions`. |
| T-14B-05-10 | Tampering | a second evidence store created by the restore | high | mitigate | Every restored event goes through `evidence.append_event`, the one evidence writer, and its `recorded` versus `already_recorded` answer is counted and returned, so a second restore of the same package adds nothing. |
| T-14B-05-11 | Tampering | supply chain: a `bagit`, archive, or checksum package added for this work | high | mitigate | None is added; `zipfile`, `hashlib`, `json`, and `shutil` are Python 3.11 standard library. `14B-RESEARCH.md` "Alternatives Considered" records the real cost of `bagit` rather than rejecting it on principle. Per `PLANNING-DIRECTIVES.md` section 4a the absence of dependencies is explicitly not the mitigation: option-c at Task 1 requires the package legitimacy gate protocol to be run before any install, and any dependency ever added here is vendored at a pinned version with a recorded checksum and a named license review, the KaTeX precedent. |
</threat_model>

<out_of_scope>
Refused by this plan, by name:

- No CLI command and no daemon route. `OPERATION-CONTRACT.md` "Pending
  surfaces" names "A course manifest or course package command (14B)" as
  explicitly not yet shippable and says do not invent one.
- No skill documentation. The 999.5 rule holds.
- No EPUB, QTI, or other interoperability adapter. PORT-02 is Phase 17B's and
  waits for a named consumer.
- No third-party package of any kind, including `bagit`, unless Task 1 returns
  option-c, which stops the plan rather than installing one.
- No cloud sync, no hosted backup, no remote package registry. Evidence and
  banks stay on disk; non-negotiable 3.
- No settings, credentials, model backend configuration, or update policy in a
  package. Those are machine-local and are named in the loss report as not
  included by design.
- No evidence rewriting, retraction, or transfer during a restore. Events are
  appended through the one writer and are otherwise untouched.
- No package signing and no package encryption. The external-installation bar
  is Phase 18's, and V2-DEL-01's signing trigger is recorded there.
- No change to `identity.py`, `journal.py`, `discovery.py`, `evidence.py`,
  `model.py`, `runtime.py`, `graph.py`, `course.py`, or anything under
  `surfaces/` or `schemas/`.
</out_of_scope>

<summary_obligations>
`14B-05-SUMMARY.md` records: the option Weibao chose at Task 1; the manifest key
set as landed; the full loss report from one real export, quoted verbatim, so
plan 14B-06's tracer report can cite it; the measured wall-clock time of one
export and one restore of the three-domain corpus, recorded and not promised;
whether the symlink-archive assertion was skipped and on which platform; which
truth was verified by which command; and any deviation from this plan with its
reason.
</summary_obligations>

<output>
Create
`.planning/phases/14B-graph-course-package-prototype/14B-05-SUMMARY.md`
when done.
</output>
