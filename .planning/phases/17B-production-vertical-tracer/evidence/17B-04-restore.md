# 17B-04 evidence: the clean-machine restore drill (gate G10)

Recorded 2026-09-05 by plan 17B-04 Task 1, under 17B-CONTEXT D-07 (restore
drill mechanics) and D-08 (no new dependencies). The drill script is
`tools/restore_drill_17b.py`, stdlib only, and it takes a commit hash rather
than this working tree's state so 17C can rerun it as a sweep.

**Verdict: G10 fails, with two named defects routed to owning subphases.**
The restore itself is sound: the package the frozen 14B surface produced
restored offline into an empty directory and validated by recomputation. What
fails is the gate's first clause. The package carried one of the seven
canonical objects the tracer authored and none of the forty evidence events,
so a clean machine does not get the tracer's course back.

## The command, and the deviation from the plan's PowerShell line

Plan 17B-04 Task 1 step 2 gives the command in PowerShell:

```
python tools/restore_drill_17b.py --commit HEAD --workdir "$env:TEMP\17b_restore"
```

**Deviation, recorded rather than glossed.** That line is a Windows artifact
inherited from 17B-CONTEXT D-07's "this Windows machine" sentence. The machine
this drill ran on is macOS (Darwin 27.0.0, zsh, Python 3.14.6), so the POSIX
equivalent was run instead:

```
python3 tools/restore_drill_17b.py --commit HEAD --workdir "$TMPDIR/17b_restore"
```

`$TMPDIR` is the POSIX equivalent of the Windows TEMP variable, `python3` of
`python`. Nothing else changed; the drill script itself is platform-neutral
(it uses `os.path`, `shutil`, and `subprocess` only). The drill has not been
run on Windows, so no claim is made about it there.

Commit under test: `48703ab47a6261f774ee6e8f093aef6ddbdabb8a`, cloned detached
into the work directory. The working tree's uncommitted changes are therefore
NOT under test, which is the point of taking a commit hash.

## How the clean machine was simulated

| requirement (D-07) | how it was met |
|---|---|
| a fresh clone at the tested commit | `git clone --no-checkout` of this repository into `<workdir>/clone`, then `git checkout --detach <hash>`; the worker runs with `cwd` and `PYTHONPATH` at the clone, so every itembank import resolves to the code at that commit |
| a fresh empty data directory | `<workdir>/data`, created empty and asserted empty before the restore; the restore mints the destination's own journal, registry, and evidence log as it writes |
| network access unavailable to the process under test | every proxy variable set to `http://127.0.0.1:9` (the discard port, nothing listening), `no_proxy` emptied, `ITEMBANK_NO_NETWORK=1` set, and a generated `sitecustomize.py` on the worker's path replacing `socket.socket`, `socket.create_connection`, `socket.create_server`, and `socket.getaddrinfo` with a raising stub. The worker proves it rather than asserting it: it attempts a connection and reports the refusal (`network refused inside the worker = True`) |
| a clean home | `HOME`, `APPDATA`, `XDG_DATA_HOME`, and `USERPROFILE` all point at an empty directory, matching the frozen 14B `corpus_14b.clean_machine_dest` overrides, so a restore that quietly read the exporting machine's settings or evidence store cannot pass while proving nothing |
| the frozen 14B export and validation surface | `course_package.export_package`, `course_package.verify_manifest`, `course_package.restore_package`, called with no wrapper of this plan's own |

**One note on the offline flag.** The plan asks for "the offline flag the 14B
contract froze". `14B-FREEZE.md` froze no such flag. What 14B froze is
structural: `course_package.py` states in its module docstring that it imports
no `urllib`, no `socket`, and no `subprocess`, so a restore is structurally an
offline operation rather than an offline one by habit, and the frozen clean
restore scenario enforced offline only by redirecting the home directory.
`ITEMBANK_NO_NETWORK=1` is this repository's conventional offline marker
(16B-03 records that no shipped code reads it), so the drill sets it as a
declaration of intent and does not rely on it: the proxy variables and the
socket blocker are what actually hold, and the worker's own connection attempt
is what proves it.

**One note on where the exported side comes from.** The journal, the registry,
and the evidence log are deliberately untracked (non-negotiable 3: evidence
stays on disk, never in the repository), so a fresh clone contains the
fixture's files and none of its durable identity or history. The exporting
side therefore has to be the live course. The drill copies
`course_fixture_17b/` into `<workdir>/source_course` first and exports from the
copy, so the repository's own fixture is never mutated by a drill run.

## The run, transcribed in full

```
restore drill: repository /Users/weiwei/Documents/Dev/itembank
restore drill: commit 48703ab47a6261f774ee6e8f093aef6ddbdabb8a (HEAD)
restore drill: workdir /var/folders/zg/7y5nnphj6bd6bcxgm4tmgv280000gn/T/17b_restore
restore drill: cloned at commit, HEAD 48703ab47a6261f774ee6e8f093aef6ddbdabb8a
restore drill: source course copied from course_fixture_17b
restore drill: fresh empty data directory /var/folders/zg/7y5nnphj6bd6bcxgm4tmgv280000gn/T/17b_restore/data
restore drill: network made unavailable (proxies at http://127.0.0.1:9, sockets refused, ITEMBANK_NO_NETWORK=1)
restore drill: network refused inside the worker = True
manifest: state applied, keys course_object_id, created, entries, loss_report, package_id, schema_version, state
manifest: 1 payload entr(y/ies) carried
  carried: course course-graph.md (ba070378d35d44e7)
manifest validation: 1 of 1 entries verified by recomputation, complete = True
restore: 1 of 1 entries verified, complete = True, evidence events recorded = 0
source registry: 7 canonical object(s); 6 did not reach the destination
evidence: 40 event(s) in the source log, 0 carried by the package
loss report: 14 row(s)
  [export] machine-local: settings
      not included by design; model backend configuration, update policy, and local paths belong to the machine, not to the course
  [export] rights-restricted: 1672ba231fd446ee
      the package right for this source is unknown; unknown and denied both stay restrictive, so this object is named here rather than packaged
  [export] rights-restricted: 36157b3e10cb46e5
      the package right for this source is unknown; unknown and denied both stay restrictive, so this object is named here rather than packaged
  [export] rights-restricted: 5c5bc6b17baa44c6
      the package right for this source is unknown; unknown and denied both stay restrictive, so this object is named here rather than packaged
  [export] rights-restricted: 8bd25c20ceaa4e20
      the package right for this source is unknown; unknown and denied both stay restrictive, so this object is named here rather than packaged
  [export] rights-restricted: 95abc1ccd3e241f9
      the package right for this source is unknown; unknown and denied both stay restrictive, so this object is named here rather than packaged
  [export] rights-restricted: d035bddef2d84eff
      the package right for this source is unknown; unknown and denied both stay restrictive, so this object is named here rather than packaged
  [drill] canonical-object-missing: bank unit3_bank.md (1672ba231fd446ee)
      this object is in the source registry and is not at the destination after the restore
  [drill] canonical-object-missing: course scope.md (d035bddef2d84eff)
      this object is in the source registry and is not at the destination after the restore
  [drill] canonical-object-missing: lesson unit3_lesson.md (36157b3e10cb46e5)
      this object is in the source registry and is not at the destination after the restore
  [drill] canonical-object-missing: objective objectives.md (95abc1ccd3e241f9)
      this object is in the source registry and is not at the destination after the restore
  [drill] canonical-object-missing: source sources/lantern_moss_survey.md (5c5bc6b17baa44c6)
      this object is in the source registry and is not at the destination after the restore
  [drill] canonical-object-missing: source sources/fen_hydrology_field_notes.md (8bd25c20ceaa4e20)
      this object is in the source registry and is not at the destination after the restore
  [drill] evidence-not-carried: 0/40 events
      the source evidence log holds 40 events and the package carried 0; no loss category names this
restore drill: FAIL, the first canonical object the restore did not carry is bank unit3_bank.md (1672ba231fd446ee)
restore drill: FAIL, the source evidence log holds 40 event(s) and the package carried none
```

Exit status: 1.

## The loss report

Fourteen rows, in two origins. Seven come from the export-time loss report
inside the manifest (`[export]`), and seven are the drill's own checks
(`[drill]`) over what actually landed at the destination.

| origin | category | target | what it means |
|---|---|---|---|
| export | machine-local | settings | by design; model backend configuration, update policy, and local paths belong to the machine |
| export | rights-restricted | `1672ba231fd446ee` | `unit3_bank.md`, the tracer's bank |
| export | rights-restricted | `36157b3e10cb46e5` | `unit3_lesson.md`, the tracer's lesson |
| export | rights-restricted | `95abc1ccd3e241f9` | `objectives.md` |
| export | rights-restricted | `d035bddef2d84eff` | `scope.md` |
| export | rights-restricted | `5c5bc6b17baa44c6` | `sources/lantern_moss_survey.md` |
| export | rights-restricted | `8bd25c20ceaa4e20` | `sources/fen_hydrology_field_notes.md` |
| drill | canonical-object-missing | bank `unit3_bank.md` | named first by the failure line |
| drill | canonical-object-missing | course `scope.md` | |
| drill | canonical-object-missing | lesson `unit3_lesson.md` | |
| drill | canonical-object-missing | objective `objectives.md` | |
| drill | canonical-object-missing | source `sources/lantern_moss_survey.md` | |
| drill | canonical-object-missing | source `sources/fen_hydrology_field_notes.md` | |
| drill | evidence-not-carried | 0 of 40 events | no frozen loss category names this one, which is the second defect below |

The six `canonical-object-missing` rows are not independent of the six
`rights-restricted` rows: they are the same six objects seen from the
destination instead of from the manifest. Both are printed because an
export-time refusal and a destination-side absence are different facts, and a
reader who cannot tell them apart cannot route either one.

What did restore, and validated: the course sidecar `course-graph.md`
(`ba070378d35d44e7`), verified by recomputation, one of one manifest entries,
`complete = True` on both the manifest validation and the restore.

## D-06 item 10: no operation grants a right after an object is minted

**Gate:** G10. **Owning subphase: 14A** (identity and rights lifecycle), with
a consequence in 14B (`course_package.build_manifest`). **Severity: blocking
for G10 as written.**

**Mechanism, diagnosed rather than guessed.** `course_package.build_manifest`
includes a payload only when `identity.rights_granted(rights, "package")` is
exactly `True`, and unknown stays restrictive (RIGHTS-01, correct on its own
terms). Rights, however, live on a revision record: `journal._commit_impl`
sets `effective_rights = rights` and passes it to `identity.revision_record`,
so a right can only be written by a commit that advances the revision. There
is no grant or revoke operation anywhere in the frozen 14A surface
(`journal.py` exposes `op_link`, `op_import`, `op_copy`, `op_move`,
`op_edit_in_place`, `op_supersede`, `undo`, and `reconcile`, and none of them
is a rights operation), and `rights=` is documented on `op_link` and
`commit_operation` as meaningful only for `kind == "source"`.

Two probes, run on a scratch copy of the fixture so the fixture was untouched:

1. Committing the lesson's CURRENT bytes with `rights={"package": "granted"}`
   is refused: `journal.JournalError: the new bytes for 36157b3e10cb46e5 are
   identical to the current bytes; no revision was recorded`
   (`journal.no_change`). A rights-only revision is impossible.
2. Committing the lesson's bytes plus one newline with the same grant
   succeeds, and the registry row then reads `{"package": "granted"}`.

So granting the `package` right to an already-authored artifact requires
editing its bytes, which advances its revision and changes its fingerprint.
That is an artifact change made to obtain a permission, which the course
artifact workflow's audit-before-editing rule forbids, so there is no correct
way to package the tracer's lesson and bank today.

For the two sources the same defect has a second face: sources DO get
`identity.rights_default()` at bind time (all unknown), and the operator could
have passed grants to `op_link` when binding them in wave 2. Once bound, the
grant can no longer be made. For the lesson, the bank, `objectives.md`, and
`scope.md` there was never a moment when it could be made, because those kinds
carry no rights at all by the frozen contract while `PACKAGED_KINDS` includes
`lesson` and `bank`.

**Why 14B's own clean restore scenario did not catch it.**
`tests/three_domain_tracer.py`, scenario `clean_restore`, packages
`corpus_14b.packaged_source`, a source minted with `{"package": "granted"}` at
link time. The scenario never asks an owned lesson or bank to cross, so the
guarantee it proved is narrower than the one `14B-FREEZE.md` records for it.

**Not fixed here.** A grant operation is a new operation on a frozen 14A
surface: it needs a record type, a journal entry shape, an undo, and a
decision about whether a rights change advances a revision. That is outside
D-06's single-file, no-contract-change bound, so it is routed rather than
patched.

## D-06 item 11: the evidence export filter compares two different vocabularies

**Gate:** G10. **Owning subphase: 14B** (`course_package`). **Severity:
blocking for G10's "and evidence" clause, and silent, which is worse than the
loss itself.**

**Mechanism.** `course_package._evidence_export_lines` keeps an event when
`event["objective"]` is in `_course_objective_ids(course_root)`, which reads
the `id` column of the sidecar's `## Objectives` table. Those ids are graph
object ids, sixteen hex characters (`67b9a4f0cfab4cb8`, `98b0c52691954d27`,
and five more). The evidence log's `objective` field carries the bank's
`OBJECTIVE:` slugs (`afe:unit3.threshold`, `afe:unit3.minerotrophy`,
`afe:unit3.peat`, `afe:unit3.lagg`, `afe:unit3.layers`, `afe:unit3.cycle`,
`afe:unit3.instrument`), and twenty of the forty events carry no objective at
all. The two vocabularies never intersect, and the sidecar's Objectives table
has no slug column to join them on, so the filter matches nothing for any
course whose evidence was written by the runtime.

Measured: 40 events in `course_fixture_17b/_evidence/evidence.jsonl`, 7
distinct objective slugs, 7 sidecar objective ids, 0 events exported, 0
recorded at the destination.

**Why this is worse than the first defect.** The package still contains
`evidence/evidence_export.jsonl`, zero bytes, and `restore_package` reports
`evidence_recorded = 0` with no loss row, because none of the five frozen loss
categories (`external-link`, `rights-restricted`, `machine-local`,
`unreachable-source`, `unsupported-kind`) names an evidence loss. A restored
course therefore looks complete on the evidence axis and is empty.
`course_package.py`'s own docstring for that function says an empty result is
a zero-byte file rather than an absent one, so a restore can tell no evidence
from evidence missing; here the file cannot make that distinction, because the
filter produced the wrong answer silently.

**Not fixed here.** The fix is either a join column in the sidecar's
Objectives table (a 14B section-and-column change, which the freeze names as
forcing a migration) or a sixth loss category (also frozen). Both are contract
changes, outside D-06's bound.

## What the drill would report if both defects were fixed

Stated so a later reader can check the drill rather than trust it: with the
`package` right granted on all seven objects and the evidence filter joining
on a real key, the export would carry seven payload entries, the destination
registry would hold seven object ids with seven files on disk, forty events
would land in the destination evidence log, and the loss report would print
one row (`machine-local: settings`, which is a deliberate exclusion, not a
loss of course content). The drill's PASS line is reachable; it is not
reachable at this commit.

## Rerunning

```
python3 tools/restore_drill_17b.py --commit <hash> --workdir <dir>
```

`--course` defaults to `course_fixture_17b` and takes any course directory
relative to the repository root. The work directory is deleted and rebuilt on
every run, so a drill can never pass on a previous run's bytes. Exit 0 means
every canonical object and every evidence event crossed and the loss report is
printed above the final line `restore drill: PASS`; exit 1 prints the first
canonical object the restore did not carry.
