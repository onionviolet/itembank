---
phase: 17B-production-vertical-tracer
plan: 04
type: execute
wave: 4
depends_on: ["17B-03"]
files_modified:
  - tools/restore_drill_17b.py
  - .planning/phases/17B-production-vertical-tracer/evidence/17B-04-restore.md
  - .planning/phases/17B-production-vertical-tracer/evidence/17B-04-egress.md
  - .planning/phases/17B-production-vertical-tracer/17B-GATES.md
autonomous: false
requirements: [G10, G11, 17B-CONTEXT D-06, D-07, D-09]
must_haves:
  truths:
    - "A fresh clone plus fresh data directory, offline, restores the tracer's canonical objects and evidence, and every capability the restore could not carry appears in a loss report (G10)."
    - "Egress capture equals the disclosed manifest, or the not-applicable path is recorded with its reason and the rights-unknown refusal check still runs (G11, 17B-CONTEXT D-09)."
    - "17B closes with every gate either passed or carrying a named defect and a named owner, and the exit record says which (17B-CONTEXT D-06)."
  artifacts:
    - "tools/restore_drill_17b.py, rerunnable by 17C as a sweep"
    - "evidence/17B-04-restore.md with the manifest validation and loss report"
    - "17B-GATES.md carrying the milestone exit record and a final state on all eleven rows"
  key_links:
    - "The drill script uses stdlib only; a third-party artifact here violates 17B-CONTEXT D-08."
    - "17C consumes this drill as input, not substitute: it runs from a commit hash argument, not from this working tree's state."
---
<objective>
Close the milestone through the last two gates and the exit record: the D-07
scripted clean-machine restore drill (G10), the D-09 egress and rights-unknown
checks (G11), the exit record in 17B-GATES.md with every gate passed or
carrying a named defect and owner (17B-CONTEXT D-06), and the final human
checkpoint. Surface commands frozen by earlier subphases are cited by
contract; this plan pins its own artifacts with commands runnable today.
</objective>
<context>
@.planning/phases/17B-production-vertical-tracer/17B-CONTEXT.md
@.planning/phases/17B-production-vertical-tracer/17B-GATES.md
@.planning/phases/14B-graph-course-package-prototype/14B-FREEZE.md (course package export and manifest commands)
@.planning/phases/14A-identity-lifecycle-operation/14A-FREEZE.md (rights grants and refusal behavior)
</context>
<tasks>
<task type="auto">
  <name>Task 1: scripted clean-machine restore drill (G10, 17B-CONTEXT D-07)</name>
  <files>tools/restore_drill_17b.py, .planning/phases/17B-production-vertical-tracer/evidence/17B-04-restore.md, .planning/phases/17B-production-vertical-tracer/17B-GATES.md</files>
  <read_first>17B-CONTEXT.md D-07; 14B-FREEZE.md for the export package and manifest validation commands.</read_first>
  <action>
1. Write tools/restore_drill_17b.py, stdlib only, taking `--commit <hash>` and
   `--workdir <temp dir>`. It must, in order: `git clone` this repository at
   the given commit into the temp directory, create a fresh empty data
   directory beside it, make network access unavailable to the process under
   test (set the proxy environment variables to an unreachable address and
   pass the offline flag the 14B contract froze), restore the exported course
   package and evidence produced by the frozen 14B export command, run
   manifest validation, and print a loss report listing every capability the
   restore could not carry (an empty loss report prints "loss report: none").
2. Run the drill against the current commit, in PowerShell:
```
python tools/restore_drill_17b.py --commit HEAD --workdir "$env:TEMP\17b_restore"
```
   Expected: exit 0, final line `restore drill: PASS` with the manifest
   validation result and the loss report above it; any failure names the first
   missing canonical object.
3. Transcribe the full run output into evidence/17B-04-restore.md and update
   gate row G10 with state, evidence pointer, and the proof column filled. A
   capability the frozen surface cannot restore goes into the loss report
   and, where it contradicts a contract, a D-06 defect.
  </action>
  <verify>The step 2 command exits 0; evidence/17B-04-restore.md contains the loss report; row G10 updated; `python itembank.py guard .` exits 0.</verify>
</task>
<task type="auto">
  <name>Task 2: egress and rights-unknown checks (G11, 17B-CONTEXT D-09)</name>
  <files>.planning/phases/17B-production-vertical-tracer/evidence/17B-04-egress.md, .planning/phases/17B-production-vertical-tracer/17B-GATES.md</files>
  <read_first>17B-CONTEXT.md D-09; 14A-FREEZE.md rights grant vocabulary and refusal behavior.</read_first>
  <action>
1. The planned default is that the tracer run makes no hosted-model call, so
   the not-applicable path is expected. If waves 2 or 3 did make one, they
   were obligated to capture the disclosed manifest and outbound payload at
   call time into evidence/ (17B-02 Task 1 step 4, 17B-03 Task 1); compare
   those captures byte-for-byte and record match or mismatch. If the tracer
   made no hosted call, record in evidence/17B-04-egress.md, verbatim: "G11
   egress: not applicable, the tracer run made no hosted-model call
   (17B-CONTEXT D-09)."
2. Run the rights-unknown refusal check in either case: attempt a
   remote-process or export operation on a fixture source whose rights state
   is unknown, using the frozen 14A rights commands, and confirm the operation
   refuses rather than proceeds. Transcribe command and refusal output.
3. Confirm the refusal diagnostic is redacted (no source body text in the
   error). Update gate row G11 with state, evidence pointer, and the proof
   column filled.
  </action>
  <verify>evidence/17B-04-egress.md contains either the byte comparison or the exact not-applicable line, plus the refusal transcript; row G11 updated.</verify>
</task>
<task type="auto">
  <name>Task 3: milestone exit record (17B-CONTEXT D-06)</name>
  <files>.planning/phases/17B-production-vertical-tracer/17B-GATES.md</files>
  <read_first>17B-GATES.md all eleven rows; every evidence file under evidence/.</read_first>
  <action>
1. Sweep the gate table first: every row's proof column names its proving
   command or fixture (no proof cell may still read `pending`); fill any the
   earlier waves missed from their evidence files.
2. Append to 17B-GATES.md a section headed `## Milestone exit record`, dated,
   stating for each gate G1 through G11: final state `pass` or `fail`, and for
   every `fail` the named defect, its diagnosed mechanism, and its owning
   subphase (13.5 D1/D2 precedent). No row's state cell may remain `pending`
   or `human-pending`. The concrete-check text transcribed from the ROADMAP
   legitimately contains the word "pending" (the G5 check names pending
   states); only the state and proof columns are swept.
3. State whether the freeze condition holds, verbatim in one of these two
   forms: "All eleven gates pass; 17B freezes." or "Gates <list> carry named
   defects with owners <list>; 17B closes with defects routed, freeze per
   Weibao's Task 4 decision."
  </action>
  <verify>
```
python -c "import sys; rows=[l.split('|') for l in open('.planning/phases/17B-production-vertical-tracer/17B-GATES.md',encoding='utf-8') if l.startswith('| G')]; bad=[c[1].strip() for c in rows if c[3].strip() in ('pending','human-pending') or c[5].strip() in ('pending','human-pending')]; sys.exit('unswept rows: '+', '.join(bad)) if bad else print('gate table swept')"
```
prints `gate table swept`, exit 0 (the state and proof cells of all eleven rows read neither `pending` nor `human-pending`; the concrete-check column may contain the word), and the file contains the heading `## Milestone exit record`.</verify>
</task>
<task type="checkpoint:human-verify" gate="blocking">
  <name>Task 4: final human checkpoint on the exit record</name>
  <files>.planning/phases/17B-production-vertical-tracer/17B-GATES.md</files>
  <read_first>The completed 17B-GATES.md exit record.</read_first>
  <action>
Ask Weibao to read the exit record and either accept the phase close (with
defects routed to owners where present) or refuse it naming the blocking gate.
Record his verdict, name, and date beneath the exit record. An agent never
self-certifies the milestone exit. An unanswered checkpoint stops the wave; it
never gets a silent default.
  </action>
  <verify>17B-GATES.md ends with a dated acceptance or refusal line naming Weibao, and
```
python -c "import sys; t=open('.planning/phases/17B-production-vertical-tracer/17B-GATES.md',encoding='utf-8').read(); sys.exit('em dash found') if chr(8212) in t else print('no em dash')"
```
prints `no em dash`, exit 0.</verify>
</task>
</tasks>
<out_of_scope>New tokens, new dependencies (the drill script is stdlib only), scorer or parser edits, real course content in-repo, the 17C full sweep (this drill is its input, not its substitute), MCP, packaging, signing, onboarding (Phase 18 and 999.3 own these), and repairing earlier phases beyond D-06's single-file bound.</out_of_scope>
<summary_obligations>Record in 17B-04-SUMMARY.md: the drill command and full output pointer, the loss report contents, the egress or not-applicable determination, the refusal transcript pointer, the final state of all eleven gates, every routed defect with owner, and Weibao's exit verdict with date.</summary_obligations>
