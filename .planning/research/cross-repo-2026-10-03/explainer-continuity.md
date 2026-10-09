# L4 explainer continuity, October 3

Status: implemented and scoped source gates passed. L4 releases its writer
ownership to coordinator chat `01a102a5-223f-7293-ae74-1922372ac0c8` after this
report. Source remains uncommitted. Integration and the sole broad preflight
belong to C. No successor chat is needed for this lane.

## Scope and authority

The dispatch in `../cross-repo-implementation-2026-10-03.md` authorizes the U1
experience change from reset on reopen to bounded tab, admitted lesson revision
and occurrence continuity. `../UI-REMAINING-2026-09-30.md` U1 records the prior
deliberate reset behavior. AGENTS, AGENT-WORKFLOW sections 1 and 6,
EXEC-CONTEXT, STATE current position, and SOURCE-TO-COURSE presentation and
progressive-enhancement sections were sampled for this slice. This is not an
exhaustive vision or module audit.

L4 changed only `surfaces/lesson_interaction.py`,
`surfaces/lesson_progressive.py`, new
`tests/js/lesson_exploration_continuity.test.mjs`, new
`tests/lesson_exploration_roundtrip.py`, new
`tests/fixtures/exploration_lineplot.md`, and this report. Existing dirty
direct-manipulation controls, reading composition, focus behavior, and all
other lanes' edits were preserved. Daemon, lesson.py, old shared tests,
original comparison fixture and shared planning changes belong to C.

## Observed result

Comparison committed scalar values and lineplot committed predictions and
intercepts survive native course detours, browser Back, explicit reopen and
reload. Guided reveal count and emphasis also survive, using a key that names
the exact rendered stage shape. Each control slot is scoped to its heading
and ordinal within that heading. Continuous and guided views share the same
admitted comparison/lineplot slots.

The presentation ledger uses `sessionStorage`, bounded to 16 admitted contexts,
32 slots per context and 32768 serialized characters. Identity is supplied by
the native caller; titles and URLs never join state. A changed teaching
revision removes that occurrence's previous state. Distinct source objects,
course uses, ordinary independent tabs and same-origin opener-cloned tabs do
not share exploration. Legacy, ambiguous, invalid or unavailable identity
gets current-page exploration without persistent restore. No GET enrolls or
changes a binding.

Only committed values are stored. Pointer previews cancel on Escape, blur,
resize, pagehide, lost capture or explicit cancel. Exact numeric drafts can be
cancelled with Escape or Cancel change. Lineplot prediction drafts cancel on
Escape, blur or Cancel prediction. Reset comparison clears only that block;
Reset exploration clears the lineplot prediction and intercept and returns
focus to prediction. Start again clears guided presentation state. These
controls have native buttons, inputs and selects with keyboard equivalents.

Denied or full storage keeps the controls usable and reports the fallback.
Corrupt storage is cleared, starts from authored defaults and reports recovery.
Static/script-free authored explanation, points, transfer prompt and starting
comparison remain available. The lineplot fieldset now permits 320px reflow,
and explicitly authored newlines retain their separate lines.

The new original synthetic fixture extends the existing rise-line treatment
with a prediction about all points and slope, intercept manipulation, an
explanation based on equal differences, and a falling-line transfer prompt.
It also contains an original comparison and a static transfer prompt. It uses
only existing LINEPLOT/COMPARE contracts. No authored JavaScript, new canonical
format, assessment authority, response event, score or mastery state was added.

## Interface and coordinator reconciliation

`exploration_attributes(lesson_id=None, revision_id=None, occurrence_id=None)`
returns a leading-space attribute string. It escapes all values and returns
empty for absent, blank, non-string, over-256-character or control-character
identity. The attributes are `data-exploration-lesson`,
`data-exploration-revision` and `data-exploration-occurrence` on
`#lesson-content`.

C accepted the exclusive lesson.py lease and wired
`lesson_page(exploration_context=None)` plus
`daemon._lesson_exploration_context`. Registered course uses name the unique
clean journal bank/lesson object, a teaching-content SHA-256, and exact course
binding ID plus binding revision. Duplicate uses require an explicit admitted
occurrence. Standalone allowlisted sources use explicitly standalone admitted
file identity. C also preserved course/occurrence on the mode switch, updated
the obsolete shared sessionStorage prohibition, and reconciled the original
comparison fixture copy. No route request remains open.

## Executed checks and evidence

| Exact command | Result and limit |
| --- | --- |
| `node --test tests/js/lesson_exploration_continuity.test.mjs tests/js/lesson_comparison_controls.test.mjs tests/js/lesson_progressive.test.mjs tests/js/lesson_craft.test.mjs` | 18 passed. Includes 6 new storage/continuity cases and the existing comparison, progressive and craft checks. |
| `python3 tests/lesson_exploration_roundtrip.py` | Passed native admitted-object/revision/occurrence identity, ambiguous refusal, static disclosure and unchanged canonical/evidence bytes. |
| `ITEMBANK_VISUAL_QA_CHANNEL=chrome python3 tests/lesson_exploration_roundtrip.py --browser --output .reasonix/cross-repo-implementation-20261003/explainer-continuity` | Passed native Back/detour/reopen/reload, tab/opener/occurrence/revision isolation, keyboard reset and explicit/Escape cancel, synthetic blur, storage failure/recovery, guided continuation, 1280/390/320 reflow, reduced-motion setting and script-free reading. No browser download. |
| `PYTHONWARNINGS=ignore python3 tests/lesson_interaction_roundtrip.py` and `PYTHONWARNINGS=ignore python3 tests/lesson_progressive_roundtrip.py` | 17 and 3 passed. Earlier unsuppressed progressive run also passed with existing file-handle and deprecation warnings. |
| `git diff --check -- surfaces/lesson_interaction.py surfaces/lesson_progressive.py` and `python3 -m py_compile surfaces/lesson_interaction.py surfaces/lesson_progressive.py tests/lesson_exploration_roundtrip.py` | Passed. Actual module diffs were reviewed while distinguishing pre-existing dirty hunks. |

Local evidence is under
`.reasonix/cross-repo-implementation-20261003/explainer-continuity/`:
`receipt.json`, `native-1280.png`, `native-390.png`, `native-320.png`, and the
preserved `failed-reflow-320.png`. The receipt records start/end source hashes,
installed Chrome, viewport widths, limits and no source drift during the final
run. Screenshots were visually inspected. Browser checks are automated evidence,
not human accessibility or learning acceptance.

## Base and output pins

Base HEAD: `28bf561865cf0696a8beb42dd6f356b8bf6ec648`. Both owned modules were
already dirty. Initial pins:

| Input | Initial SHA-256 |
| --- | --- |
| `surfaces/lesson_interaction.py` | `f89d501d549f607df5a87aaf81146e660ca5ad1482ac9de30542c97060d45814` |
| `surfaces/lesson_progressive.py` | `7f5c678c324e34c98add50a026c23ec55dc7618ebf14700a54b9078bc9a8b18b` |

Final verified source pins:

| File | SHA-256 |
| --- | --- |
| `surfaces/lesson_interaction.py` | `f14005ea6e7687a8ad4bcd5c8c91fdaa24df9e13c1fdd55b844dcbfe2457cf62` |
| `surfaces/lesson_progressive.py` | `c5cc503cae91ef9883c674fb8cb685140e65c80b107a2ba4cb2ac6c0fc7a6ecc` |
| `tests/lesson_exploration_roundtrip.py` | `cc5fce29344168e6104f5e1d1f5772c150ca8e0efb0f31436a2b8c51ed7e896d` |
| `tests/js/lesson_exploration_continuity.test.mjs` | `dc3420cc8afbe4ac7dd4bad24c53b97322230aa5906f0c22017d2a3779505b38` |
| `tests/fixtures/exploration_lineplot.md` | `7e79afa4f739eb8ca97ee4292b8d44d45f13db2f31298ec64bcc92d4eddf482d` |
| C-owned `surfaces/lesson.py` | `499248303970d01c8531530bf463f71f72630d1dcacb73bae886a02563e748a9` |
| C-owned `surfaces/daemon.py` | `c54f53804d680fbd5a303ffb74462a6e34fa706db154fab4bc2f3e33ad6ea1a9` |

## Failed runs and operational findings

The original failures retain their disposition. They are not retrospectively
called passes:

- F1: The first native import failed because concurrent daemon integration
  referenced `course_ops.course.CourseError` after L5 renamed the module
  attribute. C repaired the daemon exception tuple; L4 did not edit that lane.
- F2: The first native fixture produced no hook because legacy
  `course.bind_treatment` rows had blank permanent binding IDs. The synthetic
  fixture now uses existing `graph.enroll_binding` plus journaled
  `course.write_course`. The real GET still refuses ambiguous/unenrolled uses.
- F3: Two browser runs found a 320px fieldset extending to x=322. The owned
  fieldset `min-inline-size:0` fixed that measured overflow. The failed image is
  retained; subsequent full browser runs pass.
- F4: A browser assertion assumed the corruption notice would appear on the
  first visible lineplot. Comparison initialization runs first and repairs the
  shared ledger, so its notice carries the recovery text. The assertion now
  checks all explainer recovery messages; behavior was already correct.

These findings belong to this implementation owner rather than provider memory.
Concurrent shared imports can be temporarily incomplete; request the owning
lane to repair them instead of modifying its files. Use current admitted
binding IDs in synthetic route fixtures; a legacy binding is not an occurrence
identity just because it points to the same file.

## Recovery and limits

User recovery is per-control Reset, or closing the tab for temporary storage.
Source rollback must first coordinate removal of C's optional hook call, then
reverse only L4 enhancement hunks and remove the three new test/fixture files.
Do not restore whole modules from HEAD: the initial modules contained other
dirty work. Keep this evidence report as history or mark it superseded.

No commit, push, install, package, release, paid provider, real learner file,
active sitting or learner egress occurred. No broad preflight ran in L4.
Physical touch, screen-reader task parity, human visual preference and learning
transfer remain separate acceptance gates. Only relevant model/lesson/daemon
symbols and contracts were read; no whole-module certification is claimed.
The final combined source gate belongs to C after all writer releases.
