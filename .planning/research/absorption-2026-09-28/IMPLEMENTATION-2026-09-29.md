# Audit continuation implementation

Date: 2026-09-29. This record owns the bounded continuation of CAP-04/27,
F1 and the packaged CAP-03 authoring gate. It does not close all 27 capability
groups or the F1-F10 backlog.

## Authority and scope

User instruction: "implement accordingly, in parallel as needed?"

The existing synthesis and question backlog define the next ready slices.
Three disjoint lanes own quiz presentation, reading-desk continuity and the
packaged authoring test. The integrator owns documentation and delivery gates.
Read roots are this repository and its existing machine-local delivery notes.
Writes are source, synthetic tests, documentation and disposable build outputs.
No donor code or assets are copied. No new remote service is configured.
Runtime scoring, accepted files, note journals and source rights remain under
their existing owners. Browser drafts are presentation state, not evidence or
accepted notes.

## Implemented slices

F1 uses existing `dnd` row-to-category semantics. A row with exactly one `___`
renders a native inline dropdown in the baseline, served and offline quiz.
Ordinary rows retain their controls. Stable row IDs preserve duplicate labels,
category reuse and served assignment drafts. Reload restores permitted values,
and an acknowledged submission clears the draft. Browser storage failure
degrades to the existing form. No parser, schema or scoring rule changes.

CAP-04/27 gives the source reading desk tab-local position, focus and unsaved
wording recovery scoped to course, assignment, revision and source fingerprint.
Position resumes through an explicit button. Recovered wording stays labeled
unsaved until the learner saves through the existing note operation. An
uncertain-save reload preserves its retry identity. Changed or unavailable
source bytes cannot silently receive an old draft. Prior wording remains
copyable in a separate read-only recovery field and navigation cannot
overwrite that recovery record.

The course-workbench test now accepts `--runtime` for a portable `.pyz` or
frozen executable. Its disposable course exercises cited preview, paragraph
correction, bounded diff, accept, undo, stale conflict and report-only refusal
over real HTTP. Fixture preparation remains source-based. The server under
test comes from the supplied package.

## Verification and delivery

Targeted F1 Python and JavaScript checks pass. Existing fill-surface and quiz
transition/observer checks pass. Reading-desk Python and JavaScript checks,
course resume, course workbench, accepted lesson revision and reading-package
restore checks pass. Relevant owner symbols were sampled in the large quiz
module rather than reading it whole.

An independent read-only review of the sampled quiz and reading-owner changes
found no actionable draft-loss, retry or disclosure finding. This is code
review evidence, not human accessibility acceptance.

The packaged authoring journey passes against the portable archive and the
sidecar embedded in the macOS candidate. The macOS build completes with an
ad-hoc signed app and a checksum-verified DMG. Full preflight ran all 153
Python scripts and the JavaScript suite. All but one Python script passed.
The failing visual-accessibility assertion banned every non-text draft
control. It now permits only stable-ID assignment selects while retaining
the exclusion of visual commit controls. That repaired script passes,
including its real layout-engine gate, and all four dedicated F1 JavaScript
checks pass. No production source changed after the full run. The full suite
was not repeated after this test-only correction. Final quick preflight and
diff whitespace checks pass.

Full preflight's clean-tree gate fails because authorized work and concurrent
repairs are uncommitted. This is not a clean full-preflight pass. CI-only
optional-dependency installation and the published-schema pipeline are not
claimed by local preflight.

The installed app is running against the learner workspace and was not
replaced or interrupted. Candidate packaging does not establish installed UI
acceptance. A live Open Notebook service, human screen-reader/touch/visual
review, learning transfer and the wider restore decisions remain open.

## Recovery and remaining work

These changes are uncommitted. Other concurrent source edits were preserved,
including authoring-preview validation and evidence-retraction repairs.
Undo only this packet's named hunks and added tests, preserving concurrent
work. The candidate lives in ignored `dist` output.

Next: exercise the candidate authoring and reading journey in a separate
synthetic workspace, then complete installed acceptance when the active
learner session can be preserved. Drag word banks, one-to-one matching,
alternative valid orders, new math/domain checkers and the remaining CAP
slices retain their existing backlog gates.

## Chain link: F1 category buckets

Unit: `audit-f1-buckets-20260929`.
Predecessor and current task: `01a0ee99-a181-7762-9f87-8426e72a131e`.
Successor: `01a0eebd-95bd-7343-b1ec-2a676010eeef` on the same local checkout.
Dispatch completed. Candidate-journey write ownership has transferred.

Ordinary `dnd` rows now support dragging into category buckets in both
interactive quiz clients. A drop invokes the existing category button path,
so its stable-ID answer, draft and scoring behavior stay the same. Bucket
lists reflect assignments made with either input. Inline blanks retain their
native dropdowns. Table classification retains its existing controls. Native
forms remain the script-free fallback. Submission locks drag interaction,
and a refused submission reopens it. External drops cannot supply a row.

The new `tests/js/f1_bucket_drag.test.mjs` checks duplicate labels, category
reuse, movement between buckets, keyboard-equivalent button changes, served
reload, locked and refused submissions, external drops and table fallback.
All 45 selected JavaScript tests pass, including the existing inline,
transition and observer tests. F1 baseline, scoring, stylesheet and visual
accessibility Python checks pass. Quick preflight and whitespace checks pass.
The visual suite's existing browser gate passed, but it does not exercise the
new drag interaction. Direct native/browser drag acceptance remains open.

This link did not repeat full preflight or rebuild packages. The existing
`dist` candidate predates this slice and is stale for final acceptance.

## Successor packet: candidate browser and final integration

GOAL: Exercise the combined authoring, reading recovery and drag-bucket
candidate in a disposable synthetic workspace, repair only reproduced defects,
then build and validate the final candidate.

OWNER: The runtime and accepted-file owners remain authoritative. Weibao owns
human accessibility, preference and learning-transfer acceptance.

BASE: This repository root in the same local checkout, branch
`codex/opentutor-gap-inventory-20260927`, committed revision
`8ccd45832b66b0b86bb406d6232ef0633ef71dc3` plus the dirty inputs below.
Resolve the checkout from the task cwd. Uncommitted work is required, so do
not create a clean worktree or reset to the base commit.

| Relevant dirty input | SHA-256 |
| --- | --- |
| surfaces/quiz_page.py | e67fc949bd3c2129450a61059c71c54a2ffc5a093fdc3c133f4955cb64b6cbf7 |
| surfaces/reading_desk.py | a3d62cfe6471da84489ccdbaa8724bab0e3ce7652fe12f2fe674667225ca53c5 |
| surfaces/agent_operation.py | 0e47a1147816d9c94e2706aefb2c9604a080c3337e7836ff807ac12e7ed9259a |
| surfaces/course_workbench.py | fc31bfd04f94faaee2ccfa5caeda018deac4f148325d464ba3b5be0b93c0fea8 |
| tests/course_workbench_roundtrip.py | 7c6ed93afa4fb4651197e09eddb7d2082d607c1d5843b3e69435ab1cf2b3be31 |
| tests/js/f1_bucket_drag.test.mjs | 82cee4f5f67894d32db536172fb689e4a9b8b2cbd1b897506a67645b39fea2c7 |
| tests/js/f1_inline_completion.test.mjs | 010359d22374be7ae86b7b092e9590411ffcba13bb4ed6f766a3bd3b692765fa |
| tests/js/reading_note_save.test.mjs | 789cbdec5fbfe0e44e4a63f57907f8a3edb970c69f783aa083d1abf221c72bbe |

AUTHORITY: Source and synthetic-test edits, disposable runtime/browser
fixtures, local package builds and documentation are authorized. No commit,
push, release, personal-app replacement, hosted service setup, donor code copy,
real coursework inspection or learner-data mutation is authorized by this
packet. Chaining is user-authorized, but another link requires a new concrete
ready unit and stable stopping point.

WRITER: Successor owns candidate-journey work after dispatch. The predecessor
relinquishes writes to that scope. The predecessor may record the returned
successor ID in this packet immediately after dispatch.

SCOPE: Relevant quiz and reading presentation, candidate test fixtures,
`tests/course_workbench_roundtrip.py` runtime seam, ignored build outputs and
this record's evidence. Authoring-owner edits are allowed only for a
reproduced journey defect with unchanged scoring and accepted-write authority.

DO NOT TOUCH: Concurrent instruction and skill audits, unrelated dirty hunks,
real banks or notes, the active installed app and learner root, scoring
semantics, parser grammar, rights/egress policy, or wide restore decisions.

AUDITS: `FEATURE-INVENTORY.md` maps 604 numbered findings to 27 capability
owners with older prose coverage unresolved. The absorption synthesis owns
ranked tasks. The question backlog owns remaining F1-F10 scope. This record
reconciles the implemented partial F1 and reading slices. Broader CAP and
domain findings remain registered, prototype or backburner under those owners.
The Phase 20 crosswalk retains human visual/touch/screen-reader checks. The
17C audit retains provenance, rights, sitting-state and media restore choices.
None is closed by this packet.

CONTEXT: The installed learner app is active and must be left running. Build
with `sh scripts/build_shell_macos.sh dist`, since the Tauri configuration
embeds the sidecar from `dist`. The previous bundle is stale after this link.
The workbench's `--runtime` gate accepts a `.pyz` or embedded frozen daemon.
There is no verified live Open Notebook service. Native/browser observations
and simulated DOM checks must be reported separately.

TOOLS NEEDED: Existing Python/Node tests, local packaging toolchain and
available browser automation. Read the machine-local runtime notes for the
current launch recipe rather than copying machine paths into project docs.

EVIDENCE: Narrow gates above pass. The earlier full run executed 153 Python
scripts and JavaScript. Its one draft-contract test mismatch was corrected
and rechecked. Its dirty-tree gate is still an expected uncommitted-work
failure. That earlier run predates the drag slice. Human accessibility,
learning transfer, live companion behavior and real installed acceptance are
unverified.

NEXT ACTION: Verify the dirty fingerprints and use a long synthetic source
and duplicate-label dnd fixture to exercise drag, category-button fallback,
reload, refused submission, reading detour and unsaved-note recovery in a real
browser at desktop and narrow widths.

GATE: The same row-to-category answer survives drag, keyboard/touch-equivalent
buttons, reload and retry without exposing withheld feedback. Reading wording
survives a detour and changed-source recovery. The authoring task previews,
corrects, accepts and undoes through the existing journal. Fixes pass owning
tests. Build the final native candidate, run the packaged workbench journey,
and run full preflight once on the final source. Preserve and explain an
expected dirty-tree failure rather than committing unrelated work to clear it.
Stop at human-only or unchanged external gates.

RETURN: Changed paths, actual browser and package observations, final gate
results, skipped checks, remaining dispositions and one concrete next action.
Append evidence here and update current state without duplicating the audit
inventories.

## Chain link: combined candidate journey and final integration

Unit: `candidate-journey-20260929`.
Predecessor: `01a0ee99-a181-7762-9f87-8426e72a131e`.
Current task: `01a0eebd-95bd-7343-b1ec-2a676010eeef`.
The committed base and all eight dirty-input SHA-256 values above matched
before work. Concurrent instruction, skill and authoring repairs were preserved.

Chrome exercised the served API renderer without a baseline in a disposable
synthetic workspace. The fixture removed only the initial baseline, retaining
the real daemon session, scoring and disclosure API. Actual pointer dragging
placed two identical labels with distinct row IDs into different buckets.
Keyboard Space changed a category button, the inline dropdown worked, and a
reload restored every assignment. At 390px width the page had no horizontal
overflow. Clicking category buttons provided the touch-equivalent path; no
physical touch-device acceptance is claimed.

A fixture-only HTTP 403 refused the first submission before the runtime handled
it. The response stayed visible and locked until Check saved state confirmed
the question was still active. Controls then reopened, and reload retained the
same row assignments. Retry recorded through the real runtime. Exam mode
displayed Recorded and held every verdict; no rationale or key was exposed.

A source paragraph long enough for roughly 12,000px of desktop scrolling
exercised course detour, reload, the explicit resume button and unsaved wording
recovery at desktop and 390px widths. External edits to only the synthetic
source disabled reading and note save. The previous wording remained copyable
in its separate read-only field. Typing new wording and reloading could not
overwrite that old-source record.

One reproduced presentation defect was repaired: stale source availability
displayed `course.reading_source_stale`. The reading surface now explains the
changed source and the next recovery step. It leaves the availability envelope,
accepted-write authority and disabled actions unchanged. Focused Python reading
checks and all nine reading-note JavaScript checks passed.

The real browser authoring journey used the existing synthetic workbench
fixture with a local stub source response. Citations remained visible through
preview and paragraph correction. Accept applied the corrected file through
the existing journal. Undo restored the original file, verified from disk.
`tests/course_workbench_roundtrip.py --browser-hold` now exposes that disposable
fixture for interactive checks and stops it on Enter; default automated and
packaged gates retain their previous behavior.

After final source edits, `sh scripts/build_shell_macos.sh dist` completed.
Ad-hoc signature verification and DMG checksum verification passed. The
workbench `--runtime` gate passed against both `dist/itembank.pyz` and the
frozen daemon embedded in `dist/itembank.app`, including preview, correction,
accept, undo, stale conflict and report-only refusal. Archive SHA-256:
`c37a4bb7377174877c9d514e532501bbf274e15939b11541d2d793aa8adb2ab1`.
DMG SHA-256:
`2d258940ce49a3c5408a20d749ba85240897083f66c20240bc03a2867e11546a`.

The rebuilt native macOS candidate launched separately with an explicit
synthetic banks root. Its WebKit UI preserved independent duplicate-label and
inline selections across a course detour. Native reading wording survived a
detour and then moved into the separate read-only recovery field when the
source changed. The repaired notice rendered in that final app. This is native
candidate evidence, distinct from Chrome and JSDOM. Only owned candidate and
synthetic server processes were stopped; the installed learner shell and its
sidecar remained running.

Ignored proof images and build log live in `dist/candidate-journey-20260929/`.
Machine-local fixture and launch details are retained in `.reasonix/REASONIX.md`.
One full preflight run on this final source completed: all 153 Python scripts,
the JavaScript gate and every other local gate passed except the expected
dirty-tree gate. Exit status was 1, reporting `FAILED on clean`. This is not a
clean full-preflight pass. CI-only optional dependency installation and the
published-schema pipeline remain unrun. Final whitespace checks passed.
The preflight log is saved beside the proof images. No production source was
edited after this build and complete run by this link.

### Candidate input boundary

The candidate includes the original packet's dirty changes and this link's
reading-status repair. Archive entries match these final source SHA-256 values:

| Candidate module | SHA-256 |
| --- | --- |
| surfaces/reading_desk.py | 0011e557ea9779b8b12ed2c6ecfc5578cf262f89c9e4c3ae01f4807f9bba4653 |
| surfaces/daemon.py | 4a25a5c35ec4b903892fb5e7e7239298176381b1748b35510a9bae3faed9225d |
| surfaces/presentation.py | 3b23773147c3c000f8ae109c06fa450a797d9ec0682a114affd9ea193cc121f0 |

Quiz, authoring and workbench source hashes still match the predecessor packet.
The large quiz and daemon modules were sampled by symbol, not read in full.

After this candidate build and full preflight, chat
`01a0eec6-892a-78e2-9c9e-08df41fb0883` reported new user authorization for a
separate Home/Courses slice. It owns `surfaces/daemon.py`, scoped desk/shelf CSS
in `surfaces/presentation.py`, `tests/desk_experience_roundtrip.py` and
`research/ui-goal-review-2026-09-29.md`. That later slice is excluded from this
candidate, native/browser observations and full-preflight evidence. The two
module hashes above matched the live checkout when the boundary was recorded,
before its later source edits. Do not call that future source packaged or
fully verified using this candidate's results.

Human screen-reader, physical touch, accessibility and learning-transfer
acceptance remain open, as do live Open Notebook, installed learner acceptance,
the wider restore decisions and the existing CAP/F1-F10 dispositions. No
commit, push, install, release or successor dispatch occurred. The chain stops
at these human and unchanged external gates; no new concrete source unit was
established by this journey.

Next action: Weibao reviews the candidate's screen-reader and physical-touch
journey while preserving the active learner session. The independently
authorized Home/Courses source lane retains its own gate and owner.

## Combined candidate integration: Home and Courses

Unit: `combined-candidate-20260929`, current task
`01a0eebd-95bd-7343-b1ec-2a676010eeef`. The existing chain accepted the
Home/Courses packet in `research/ui-goal-review-2026-09-29.md`, section
Final candidate packet for the existing chain. Chat
`01a0eec6-892a-78e2-9c9e-08df41fb0883` relinquished its four named source/test
paths. This section supersedes the earlier candidate exclusion for the latest
build, retaining the earlier build's evidence and input boundary above.

The committed base remains `8ccd45832b66b0b86bb406d6232ef0633ef71dc3`.
All four Home/Courses hashes matched before building, and earlier quiz, reader,
authoring and workbench module hashes still matched their final predecessor
values. Concurrent instruction and skill edits were preserved. No reproduced
defect required an additional source repair in this integration link.

| Combined input | SHA-256 |
| --- | --- |
| surfaces/daemon.py | 38a12a1bb6bea5f4bd81e580ae417bbeeaefd5615aa54a80af699c850274bcd9 |
| surfaces/presentation.py | f1a9d57b70e1360bf9ad7f6aa2e8487d5a689a8983a8087e8aa2097160e4af26 |
| tests/desk_experience_roundtrip.py | bae4fdf321b1bf733d3cf0d721f8a7db413b94efb44781ada5499480aade761e |
| tests/js/desk_craft_reorder.test.mjs | 5cd9adafe7f7d5d1cccc0aea6814744ca3009b27d907d22839d6765258151758 |

The desk Python gate and all 12 desk reorder JavaScript cases passed. The
combined build completed with signature verification and a checksum-verified
DMG. Both packaged workbench journeys passed against the archive and the frozen
daemon embedded in the native candidate, including correction, accept, undo,
stale conflict and report-only refusal. The archive's daemon and presentation
entries match the combined source hashes above.

The desk fixture's read-only served checks also passed against the actual
archive. It created three idle synthetic courses before a fourth course with
one canonical saved sitting. Viewing Home and Courses did not write fixture
learner state. The native candidate launched on that same disposable root.
Its Home selected the saved-last course, displayed Practice, Question 1 of 2,
and linked the exact `session=synthetic` and `course=sample-study-skills` sitting.
Following that link reached the runtime's same question and position.

Moving the first idle course down through native Course options saved the new
order. Reopening Home from its navigation link reloaded the server-rendered
shelf with that order while keeping the saved course highlighted and its exact
destination intact. Chrome then exercised the rebuilt native proxy: reload
retained the same saved order, position and destination. Home and Courses both
had document width equal to viewport width at 390px, including the long course
title. This narrow-layout evidence is Chrome on the packaged proxy, not a
physical touch-device or narrow native-window acceptance claim.

Actual native Home and narrow browser screenshots, plus the build log, are
retained in ignored `dist/combined-candidate-20260929/`. The temporary viewport
was reset. Only the owned candidate shell, its sidecar and the disposable
archive fixture server were stopped. The installed learner shell and its
sidecar remained running on their unchanged root.

The latest archive SHA-256 is
`c5d208d6c43382ee966dd519a9df24b5330204c5653aaff4b8c9d69c0139d041`.
The latest DMG SHA-256 is
`8383734291c4bc712b77b6f9afb5a96f5c716fdc6aed1f762d3a7c0128f0b8a4`.
These latest ignored package files replace the earlier candidate files; the
older hashes above describe the earlier build only.

One full preflight on the combined inputs completed. All 154 Python scripts,
the JavaScript gate and every other local gate passed except the expected
dirty-tree gate. It exited 1 with `preflight: FAILED on clean`; this is not a
clean preflight or CI pass. CI-only optional dependency installation and the
published-schema pipeline remain unrun. No second full run was needed on these
combined inputs. Whitespace checks passed. All source/test and package entries
in the saved checksum manifests still matched after the run.

The complete log is saved in `dist/combined-candidate-20260929/preflight.log`.
`inputs.sha256` names the tested quiz, reader, authoring, Home/Courses and
relevant test bytes; `packages.sha256` identifies the matching archive and DMG.
No production source changed during this integration link. Repository writes
were limited to this evidence owner and the current STATE projection, plus the
ignored local runtime notes and disposable build/fixture/proof outputs.

The large daemon and presentation modules were reviewed only at the desk/shelf
helpers, shelf script and applicable CSS. Prior real Chrome drag, refusal and
reading-recovery evidence remains tied to unchanged quiz and reader hashes;
the combined full suite and packaged authoring checks verify integration.
Human preference, visual comfort, screen-reader, physical-touch and learning
transfer acceptance remain open. G3 subject expression, wider G4 continuity,
live Open Notebook, installed acceptance and the existing CAP/F1-F10/restore
dispositions retain their owners and gates. No commit, push, install, release
or extra successor is authorized or performed by this link.

The integration packet's technical gate is complete. Next action: Weibao
reviews the combined candidate's screen-reader and physical-touch journey while
preserving the active learner session. No new concrete source unit was selected,
and no successor was created solely for the remaining human or external gates.

## A5 source integration continuation, 2026-09-30

The earlier combined candidate remains a dated package proof, not current
source or installed acceptance. A1-A4 have now completed their distinct lanes.
The existing [A5 integration evidence](A5-INTEGRATION-2026-09-29.md) owns native
outline routing and exact sitting return, joined readiness/history, explicit
local source context and quote notes, archive-safe and note-only restore
repairs, opt-in inline fill and guarded structural drag arrival.
Ordinary source HTTP and actual source ordering pointer/reload/keyboard
Remove/Add/runtime/report checks pass. The final source-only combined gate is
pending. The user has deferred fresh builds; the last ordering archive has
explicit source drift, and the active installed learner app stays preserved.
P2-P5 production contracts, the live companion, representative human
accessibility/learning-transfer and final-source package gates remain named
prerequisites. Current next steps are in STATE's September 30 resume surface,
not this earlier candidate's human-only next-action sentence.
