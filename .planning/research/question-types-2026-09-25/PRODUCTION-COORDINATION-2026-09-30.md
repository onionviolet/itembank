# Staged and polynomial production coordination

Status: bounded source implementation and verification complete, 2026-09-30.

User authorization: "implement in parallel accordingly, coordinate chats until its done".
This approves the preceding O1 staged, O2 polynomial and O3 UI lanes. The
staged D1-D5 and checker R2-R4 proposals are the implementation contract for
this bounded pass. This is not authorization to commit, push, build a fresh
archive, replace the installed app or access real course material.

## Owners and handoffs

| Lane | Exclusive write ownership | Observable gate |
| --- | --- | --- |
| S, `staged_runtime` | Runtime, selection, session adapter, evidence and session/response/event schemas initially | Genuine practice barrier, whole-unit selection, linked child events, legacy upgrade, process serialization and evidence/session crash recovery |
| C, `checker_contract` | Shared parser, item/lint schemas and checker authoring; both staged declarations and polynomial fields | Both declarations lint; authored checker cases pass; ordinary parsing remains compatible |
| C after S release | Polynomial additions in runtime, session/evidence projections and response/event schemas | Exact checking, typed refusal without attempt, raw draft recovery, actual mode/tier withholding and accepted-revision undo |
| U, `ui_validation` | Quiz page, quiz surface and daemon client routes | Synthetic real served desktop/narrow journeys, keyboard/reload/reference detours, held feedback, no private checker/staged leaks |
| Root | Integration, owning planning projections and final coordinated checks | Frozen inputs, one source-only preflight, narrow failure repairs and updated acceptance limits |

One writer per shared file. C and S agree parser/public interfaces before
integration. C waits for S's explicit runtime/evidence/session release. U uses
runtime public payloads and never settles correctness. All lanes preserve the
existing dirty tree and record input fingerprints. Recovery snapshots use
`.py.txt`, never a second discoverable Python scorer.

## Authority and limits

Canonical bank declarations remain in the existing parser. Assessment state,
scoring, disclosure and attempt evidence remain with the deterministic runtime.
Staged cases select two existing MC children as one unit, commit each once and
hold practice feedback until the second commitment. Formal feedback retains
whole-sitting release. Session v4 prevents older readers ignoring the barrier.

Polynomial scope is one pinned rational-polynomial domain, variable `x`,
expanded form and fixed resource bounds. Invalid, unsupported, unavailable and
error states refuse without wrong or pending-prose evidence. Private teacher,
diagnostics and authored tests never enter learner HTML or public JSON.

Only fictional fixtures, temporary sessions and local served sources are used.
No new external service or remote data egress is added. Accepted authored
changes retain expected fingerprints, journal acceptance and undo. Existing
accepted learner files and the installed sitting remain untouched.

## Verification and recovery

Each lane runs focused meaningful checks and records exact commands, changed
paths, fingerprints and unresolved gates in its production evidence report.
Root schedules one combined source-only preflight after all production writers
freeze. Source checks do not close physical touch, screen-reader, human visual
preference, learning transfer, clean packaged or installed acceptance. The
existing dirty-tree and build hold remain explicit.

Undo uses lane baseline snapshots and a bounded reverse diff after checking
current fingerprints. Never restore a whole shared file over another lane's
later edits. This packet does not claim completion until final evidence is
recorded below.

## Final delivery and ownership release

S delivered genuine staged runtime behavior and released shared files to C.
C delivered the shared parser, exact polynomial scorer extension and reviewed
staged-header proposal route. U delivered native/API clients and served
continuity checks. All production writers released ownership before the
combined run. Root added the published staged declaration and exact polynomial
grammar to `itembank spec`, updated README and reconciled the owning state,
feature, backlog and contract projections. No other agent remains assigned a
production writer in this pass.

The bounded delivery is source-complete:

- Fixed two-MC cases use complete selection, genuine answer/reason commitment,
  per-case feedback release, raw linked evidence, session v4 and exact
  process/crash recovery. No exam transport is used for production practice.
- Polynomial fields use one pinned exact rational grammar and expanded-form
  rule inside the existing scorer. Private authored tests validate teacher,
  diagnostic, wrong-form and refusal outcomes. Unresolved checks preserve the
  original input and append no attempt. Mode and hint-tier barriers hold.
- Existing proposal storage and journal acceptance admit staged header changes
  with bounded diff, cancellation, stale refusal and exact undo. Existing
  checker item authoring preserves accepted-revision and undo controls.
- Native/API and Chrome source journeys pass at 1280/390/320: keyboard,
  reload, supported reference/Back/resized return, changed-revision draft
  notices, genuinely held course detours and unavailable storage. Static staged
  HTML refuses before keyed preparation or replacing an existing output.

Lane evidence: [staged](STAGED-PRODUCTION-2026-09-30.md),
[checker/parser/authoring](CHECKER-PRODUCTION-2026-09-30.md), and
[learner UI](../STAGED-CHECKER-UI-2026-09-30.md).
Root's independent `tests/staged_checker_disclosure_roundtrip.py` covers actual
Home/report/evidence projections, model-hint refusal, real polynomial refusal,
raw evidence, schema validation and active-formal withholding.

## Aggregate verification and exact limits

One `python3 scripts/preflight.py --source-only` run executed 181 of 184 Python
scripts. Its nine failed scripts were `director_roundtrip`, `file_fault_tracer`,
`gate_roundtrip`, `lesson_roundtrip`, `model_phase_roundtrip`,
`paced_lesson_tracer`, `scoring_roundtrip`, `three_domain_tracer` and
`visual_accessibility_roundtrip`. Root registered `bank.invalid_staged_cases`
in the source lint-code catalogue and repinned the approved additive scorer
extension while retaining the unchanged legacy/prose checks. All nine scripts
pass focused reruns. The two browser-matrix reruns use
`ITEMBANK_VISUAL_QA_CHANNEL=chrome`, the installed browser, because the default
Playwright headless-shell executable is unavailable. No browser installation
was attempted. `protocol_roundtrip` also passes after the registry repair.

The initial JS gate exposed an accessibility attribute missing from a minimal
test DOM. Root added actual attribute behavior and association assertions.
The subsequent full JS run exposed an ordinary-ordering fixture that omitted
the new empty activity state. Its targeted suite passes after explicitly
initializing that state. The final `node --test tests/js/*.test.mjs` gate passes
all 112 cases, zero skipped or failed. No production quiz/runtime bytes changed
for these fixture repairs.

Final quick source-only preflight passes all gates it runs. The original full
run remains failed; the full Python suite was not repeated. Its dirty-tree gate
remains unsatisfied, since authorized source changes and inherited work stay
uncommitted. Three app-build scripts remain deferred:
`a5_integrated_package_roundtrip.py`, `math_offline_roundtrip.py` and
`packaging_roundtrip.py`. The sample-build gate and two CI-only legs also remain
deferred. This report does not convert full-plus-focused evidence into a claim
that the original combined preflight passed.

Logs are under `.reasonix/staged-checker-production-20260930/`:
`preflight-source-only.log`, the nine named `*-repaired.log` logs,
`protocol-final.log`, `inline-js-repaired.log`, `ordering-js-repaired.log`,
`js-repaired-final.log` and `quick-docs-final.log`. Both earlier failed JS runs
are retained for comparison. `source-freeze-repaired.json` and `.sha256` name
24 final source/schema/test/README inputs. Of the original 21 frozen inputs,
only `model.py` changed after the combined run, for the missing lint-code
registration; the three other repairs are test files.

## Recovery, held acceptance and future scope

`recovery-manifest.json` records measured baseline/final fingerprints and task
diffs for the four S-start runtime files, three U-start UI files, parser and
item/lint schemas. The parser and item/lint schema task-start bytes were
reconstructed from prior preserved snapshots and verified against the
worker's independently measured initial hashes before being saved. Authoring
reversal is explicitly reconstructed from its two additive edits, rather than
misrepresented as a measured initial-byte snapshot. Root test repair snapshots
are stored in `root-repairs-baseline/`. Python snapshots use `.py.txt`.
Apply only a reviewed task diff against matching current fingerprints; never
reset inherited dirty work or overwrite subsequent shared edits. Session and
response schema reversal needs a scoped diff review; an exact task-start
response-schema snapshot was not captured.

The installed learner sitting and fresh-build hold are preserved. No commit,
push, app archive build, installation, release or real learner-source access
occurred. Synthetic tests may exercise temporary course packages or HTML;
they do not certify a fresh installed application. Human visual preference,
physical touch, screen-reader and learning-transfer acceptance remain open.
Large production modules were read through relevant symbols and functions;
this is not an exhaustive whole-module review.

Broader symbolic domains, P3 exact evidence anchors/first-error semantics, P5
immutable activity graphs, populated-root merge and external-provider trials
retain their existing prerequisites. U1 temporary exploration persistence was
not changed. The current remaining sequence is owned only by STATE, not by
another implementation queue in this evidence record.
