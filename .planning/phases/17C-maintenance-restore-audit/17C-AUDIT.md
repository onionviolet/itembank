---
phase: 17C-maintenance-restore-audit
plan: 01
date: 2026-09-05
audited_commit: 5286683d78f7e72aa40e89f5272c10fd678d8280
drill_script: tools/restore_drill_17b.py
status: tasks 1 to 3 complete; Task 4 (Weibao's acceptance) owed
---

# 17C maintenance and restore audit

The post-Phase-17 audit the ROADMAP governance clause names, run so it stops
being ownerless. 17B proved the tracer's one unit restores; this audit
sweeps every canonical object class, checks that no loss is silent, sweeps
maintenance owners, and names the recurring triggers that fire it again.

Weibao holds acceptance authority on this report. Nothing below is
self-accepted.

## Task 1: precondition

`17B-GATES.md` exists and carries the milestone exit record. Every gate row
reads pass, pass-carrying-a-routed-defect (each with a named defect,
mechanism, and owning subphase), or `deferred-human`.

**Deviation, recorded rather than silently resolved.** The plan's halt
condition asks for every row to read passed or defect-routed. Two rows, G4
(the screen-reader walk) and G8 (the visual acceptance at 1280 and 375),
read `deferred-human`: they are owed human reviews, not defects, and an
agent may not sign them (17B-CONTEXT D-04). This audit does not treat an
owed human review as a halt, under Weibao's standing directive of
2026-09-01, reaffirmed 2026-09-05, that human legs are deferred and
recorded rather than blocking. They stay owed and are listed again in the
findings below so this report does not quietly absorb them.

Audited commit: `5286683d78f7e72aa40e89f5272c10fd678d8280`.
Drill script, as D-07 requires and as 17B left it: `tools/restore_drill_17b.py`.
No finding F0: the script path is recorded and the script takes `--commit`,
so this audit reran it rather than writing a second drill.

## Task 2: restore drill sweep

### The drill, rerun verbatim at the audited commit

```
python3 tools/restore_drill_17b.py --commit HEAD --workdir "$TMPDIR/17c_sweep"
```

```
restore drill: repository /Users/weiwei/Documents/Dev/itembank
restore drill: commit 5286683d78f7e72aa40e89f5272c10fd678d8280 (HEAD)
restore drill: workdir $TMPDIR/17c_sweep
restore drill: cloned at commit, HEAD 5286683d78f7e72aa40e89f5272c10fd678d8280
restore drill: source course copied from course_fixture_17b
restore drill: fresh empty data directory $TMPDIR/17c_sweep/data
restore drill: network made unavailable (proxies at http://127.0.0.1:9, sockets refused, ITEMBANK_NO_NETWORK=1)
restore drill: network refused inside the worker = True
manifest: state applied, keys course_object_id, created, entries, loss_report, package_id, schema_version, state
manifest: 7 payload entr(y/ies) carried
  carried: bank unit3_bank.md (1672ba231fd446ee)
  carried: course course-graph.md (ba070378d35d44e7)
  carried: course scope.md (d035bddef2d84eff)
  carried: lesson unit3_lesson.md (36157b3e10cb46e5)
  carried: objective objectives.md (95abc1ccd3e241f9)
  carried: source sources/lantern_moss_survey.md (5c5bc6b17baa44c6)
  carried: source sources/fen_hydrology_field_notes.md (8bd25c20ceaa4e20)
manifest validation: 7 of 7 entries verified by recomputation, complete = True
restore: 7 of 7 entries verified, complete = True, evidence events recorded = 40
source registry: 7 canonical object(s); 0 did not reach the destination
evidence: 40 event(s) in the source log, 40 carried by the package
loss report: 1 row(s)
  [export] machine-local: settings
      not included by design; model backend configuration, update policy, and local paths belong to the machine, not to the course
restore drill: PASS
```

Exit code 0.

### The sweep, one row per canonical object class

The class list is `.claude/CLAUDE.md`'s durable-object list, plus the
operation journal, which this plan adds because the journal is
restore-relevant state the mutation rules govern rather than an entry on
the object list. Verdicts are read from the destination tree
(`$TMPDIR/17c_sweep/data`) and its rebuilt registry, never from the
manifest's own claim.

| canonical object class | verdict | how it was judged |
|---|---|---|
| course | restored, bytes | `course-graph.md` 5856 bytes at the destination, fingerprint recomputed |
| scope or framework version | restored, bytes | `scope.md` 2264 bytes, carried as an object of kind `course` |
| concept | restored, pointer | concepts have no object kind of their own; they live in the sidecar's `## Structure` table, which crossed inside `course-graph.md` |
| objective | restored, bytes and pointer | `objectives.md` 2027 bytes, plus the sidecar's `## Objectives` table |
| source | restored, bytes | both `sources/*.md` files, 3920 and 3567 bytes |
| source binding | restored, pointer | the sidecar's `## Bindings` table, 30 rows, inside `course-graph.md` |
| artifact | restored, bytes | the lesson and the bank are this course's artifacts |
| lesson | restored, bytes | `unit3_lesson.md` 7357 bytes; lints as part of the bank's LESSON-REF check |
| bank or assessment form | restored, bytes | `unit3_bank.md` 15785 bytes; `itembank.py lint` at the destination reports 8 items, 0 errors, 0 warnings |
| activity | not exercised | no activity object exists in the audited course; the sweep can report no verdict for a class with no instance, and says so rather than claiming a pass |
| learner note | not exercised | no `_notes` directory exists in the audited course. Untested, not proven absent from packages: see F-LOSS-4 |
| learner artifact | not exercised | same as learner note |
| evidence event | restored, bytes | 40 of 40 events in the source log carried and recorded at the destination |
| strategy | restored by code, not by package | strategy contracts are read from `strategies.strategy_contract` in the code under test, not from per-course files; a clean machine gets them from the clone |
| agent operation | NOT RESTORED, and not named | 35 applied `agent_operation` entries exist in the source journal (of 82 applied entries in 131 lines); the package carries no journal, and no loss row names them. F-LOSS-1 |
| rights grant | NOT RESTORED, and not named | 6 applied `grant_rights` entries in the source (12 lines, prepared and applied); every destination row reads `rights: null` or all-`unknown`. F-LOSS-2 |
| accepted revision | not exercised | no `accept_revision` entry exists in the audited course's journal; the mechanism is the journal's, so F-LOSS-1 covers it if one ever does |
| operation journal (this plan's addition) | NOT RESTORED, by design, not named | the source journal holds 131 lines, 82 of them applied, across 9 record types (mint 1, link 6, edit_in_place 24, agent_operation 35, move 2, external_edit 1, reconcile 1, adopt 6, grant_rights 6); the destination journal holds 14 lines, 7 applied, all `restore`. The design is defensible (a restore mints the destination's own journal, which is what makes it a clean-machine restore) but no loss row says the provenance did not travel. F-LOSS-1 |

### Loss-report completeness

The drill's loss report carries exactly one row:
`[export] machine-local: settings`, which is accurate and by design.

Every NOT RESTORED row above must appear by name in that report. Four do
not, so four silent losses are recorded as findings. A fifth is a payload
gap rather than a journal one and is the most consequential of the five,
because it is the one a learner would meet as a broken page.

- **F-LOSS-1, provenance and operation history do not cross and nothing
  says so.** The package carries no operation journal, so how every object
  entered the course, who acted, what an agent did, what was moved, what
  was reconciled, and what was adopted are all absent at the destination,
  which instead shows seven objects at revision 1 restored by one actor.
  The restore is honest about bytes and silent about history. Next safe
  action: either add a `provenance-not-carried` loss category naming what a
  package structurally cannot carry, or carry a read-only provenance
  export beside the evidence export. Owner: 14B (packaging), consequence
  for 14A (the journal is the record that does not travel).
- **F-LOSS-2, rights state does not cross and nothing says so.** Every
  restored object arrives rights-unknown, so a restored course cannot be
  re-exported without the owner granting every right again, and a learner
  reading the destination cannot tell a right that was never granted from
  one that was granted and lost. Unknown staying restrictive means this
  fails safe, which is why it is a silent-loss finding and not a breach.
  Next safe action: carry each entry's rights record in the manifest entry
  and replay it through `journal.op_grant_rights` at restore time, or name
  the loss. Owner: 14B.
- **F-LOSS-3, `_attempts` session state does not cross and nothing says
  so.** The audited course carries six files under `_attempts/`, including
  a resumable session and a lesson run. None crosses and none is named.
  Sessions are arguably machine-local, which is a defensible answer, but it
  is not the answer the report gives; it gives none. Next safe action:
  decide the axis (machine-local by design, or carried) and name it either
  way. Owner: 14B, with the runtime phase that owns session files.
- **F-LOSS-4, unregistered course files do not cross and nothing says so.**
  A package carries registry objects. Files inside the course root that no
  operation ever bound are invisible to it: in the audited course,
  `README.md`, `treatments.md`, and the whole `media/` directory. Next safe
  action: report unregistered files inside a course root as a named loss
  category at export time, since "the exporter cannot see it" and "the
  learner does not need it" are different claims. Owner: 14B.
- **F-LOSS-5, a restored bank cites media the package did not carry, and
  the linter does not notice.** `unit3_bank.md`'s MEDIA table cites
  `media/lantern_moss_cycle.svg` with a recorded sha256. The file is not a
  registered object, so it did not cross; the destination has no `media/`
  directory at all; and `python3 itembank.py lint` on the restored bank
  still reports `8 items, 0 errors, 0 warnings`. This is the one finding a
  learner would meet directly, as a missing diagram in an otherwise
  complete-looking course. Next safe action, two of them: bind media files
  as objects (or extend F-LOSS-4's category to cover them), and make
  `lint` check that a cited MEDIA path exists and matches its recorded
  digest. Owner: 14B for the packaging half, the model or lint phase for
  the check.

No finding in this list contradicts a passing G10. G10 asks that supported
canonical objects and evidence restore and that unsupported capabilities be
named; the supported objects and the evidence do restore. These five are
the audit's own widening of the question from "did the supported objects
cross" to "does the report name everything that did not", which is what
17C exists to ask.

## Task 3: maintenance-owner sweep and recurring triggers

### Owner sweep

Run verbatim:

```
grep -n "Owner:" .planning/REQUIREMENTS.md
```

49 lines, against 48 at planning time. Crossed against the requirement
blocks in the section that uses the convention ("Expanded source-to-course
families", added 2026-08-13, lines 375 to 1062): 49 blocks, 49 with a named
`Owner:`, **zero unowned**.

- **F-OWN-1, an observation, not a defect.** The `Owner:` convention starts
  at the 2026-08-13 section. The earlier v1 and v2 requirement bullets
  (EVID, PROTO, LESSON, and the rest) are one-line requirements with no
  Owner field at all, by the shape they were written in rather than by
  omission, and their status of record is the phase directory, as
  `REQUIREMENTS.md`'s own 2026-09-03 header note says. Recorded so a later
  audit does not read the absence as 170 unowned requirements. Next safe
  action: none required; if Weibao wants owners on the v1 bullets, that is
  a wording pass, not a finding to repair.
- **Accepted-revision records.** No `accept_revision` journal entry exists
  in the audited course, and the accepted-revision mechanism is 15B's
  record type rather than a `.planning/` file class, so there is no
  separate owner sweep to run against it. Recorded rather than skipped in
  silence.

### Recurring audit triggers

This audit reruns when any of the following change. The globs are what a
maintainer or a hook should watch.

| trigger | fires on changes to | why |
|---|---|---|
| 14B, course and file semantics | `course_package.py`, `course.py`, `graph.py`, `journal.py`, `identity.py`, `fixtures/corpus_14b.py` | these own what a package carries, what a loss report names, and what an object is; every finding above lives here |
| 16C, agent job protocol | `director.py`, `capabilities.py`, `tools/capabilities_manifest.py`, `.claude/skills/**`, `.agents/skills/**` | an agent operation is journalled state that a restore does not carry (F-LOSS-1), so a change to what agents record changes what is lost |
| 17B, tracer, drill, and export packaging | `tools/restore_drill_17b.py`, `course_fixture_17b/**`, `.planning/phases/17B-production-vertical-tracer/17B-GATES.md` | the drill is this audit's instrument; a change to the instrument invalidates the last reading |

## Summary

| item | result |
|---|---|
| drill result | PASS, exit 0, at commit `5286683` |
| canonical object classes swept | 18 (17 from the durable-object list plus the operation journal) |
| restored | 10 (8 by bytes, 2 by pointer), plus strategy contracts carried by the code |
| not exercised | 4 (activity, learner note, learner artifact, accepted revision) |
| NOT RESTORED | 3 journal-borne classes (agent operation, rights grant, operation journal) plus two payload gaps (`_attempts`, unregistered files including media) |
| loss-report completeness | FAIL: 1 row printed, 5 silent losses found |
| owner sweep | 49 of 49 next-milestone requirement blocks own a named owner; zero unowned |
| findings | F-LOSS-1 to F-LOSS-5, F-OWN-1 (observation) |
| owed human legs, carried forward from 17B | the G4 screen-reader walk, the G8 visual acceptance at 1280 and 375, the G5 default rollup choice, and the 17B milestone acceptance signature |

Every finding is routed, none is repaired here: repairing a finding is out
of this plan's scope, and all five are contract changes in 14B's surface.

## Acceptance (Task 4, blocking)

Awaiting Weibao. Accept as written, accept with owner assignments for the
findings, or reject with reasons. An unanswered checkpoint takes no silent
default, and an agent does not accept its own audit.

Verdict: ____________  Name: ____________  Date: ____________
