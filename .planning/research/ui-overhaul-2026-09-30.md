# Parallel UI overhaul implementation

Date: 2026-09-30. Status: integrated source frozen and verified; visual preference
and installed acceptance remain open. This packet owns execution of the
September 30 direction and extends [the UI goal owner](ui-goal-review-2026-09-29.md).
It does not replace the capability backlogs or their production gates.

## Goal and settled implementation choices

Deliver a coherent source-served learning workspace across Home, Courses,
course overview, reading, lessons, and practice. Replace weak composition
where useful instead of accumulating another override layer. Preserve useful
behavior because it works, not because it cost effort to build.

- D1: A compact shared navigation frame, with current course and activity
  context. Existing routes and destinations remain reachable; label controls
  with concrete learner actions and place administration in secondary controls.
- D2: Home centers an exact saved activity when known, then course choices.
  Courses is the full collection. Do not invent recency, priority, completion,
  or mastery. Ambiguous sittings require an explicit choice.
- D3: A precise but expressive learning workshop is the working direction:
  readable source and response areas, restrained framing, coherent typography,
  intentional accent roles, and subject-specific content rather than decorative
  dashboard filler. Compare a quieter reading treatment and a more expressive
  workshop treatment on the same synthetic journey before settling details.
  Both are reversible candidates, not claims of human preference.
- D4: Reading, lesson, and practice receive task-specific working space inside
  the same app. Source context, private notes, learner input, and runtime
  feedback remain distinguishable. Secondary tools open deliberately and have
  a clear return. Core controls work with keyboard and at narrow widths.
- D5: Complete a served synthetic journey before claiming delivery: Home to
  course to reading/lesson to practice, permitted reference detour and exact
  return, reload, failed save/retry, and honest feedback. No scoring, grammar,
  response protocol, or evidence semantics change in this pass.

## Base, authority, and recovery

Base Git revision: `8ccd45832b66b0b86bb406d6232ef0633ef71dc3` plus the inherited
dirty working tree. The prior September 30 source gate is historical evidence,
not certification of the coming changes. A1-A5 released their source ownership.
The active learner installation and fresh-build hold remain in force.

The user explicitly authorized revamping old code and creating parallel chats.
Source edits, synthetic previews, targeted tests, and integration are allowed.
No commit, push, new archive/app build, install, release, real coursework access,
or external data upload is authorized here. Use local project chats and local
synthetic content; no new model/service connection is required.

Baseline copies of all eight owned source files are saved under
`.reasonix/ui-overhaul-20260930/base/surfaces/`; `base.sha256` records their
dirty-input hashes. Each lane verifies its files still match before first edit,
records any later deliberate adoption, and captures its diff against those
copies. Restore only a reviewed task diff against the current bytes, never
reset the shared checkout or copy baseline files over another writer's work.

One writer per source file. Builders are not alone in this checkout and must
preserve inherited work. Existing tests are assigned below; do not weaken
behavior assertions to hide regressions. Replace exact CSS-string assertions
with meaningful structural or rendered checks when the design actually changes.
Read modules by symbol and disclose sampling limits.

## Parallel lanes

Dispatch registry (2026-09-30): V `01a0f0d8-726f-7381-99dc-f158a067a4d6`,
N `01a0f0d8-7e9f-7ed1-a38e-7ab9b45a4977`, W
`01a0f0d8-905b-7013-990d-da1c7ad539ea`, and I
`01a0f0d9-4675-7c01-82d3-191e12aefe09`. V/N/W retain their table ownership
until explicit release. I owns the packet, UI-SPEC, STATE, vision inbox, and
new journey test. All three builder lanes have now explicitly released their
source and assigned tests to I; their named evidence records preserve handoff
hashes, commands and limits. Builder releases were received before the combined
source-only gate started.

N released source and assigned tests on September 30. I verified released
daemon/home hashes against N's evidence before adopting the daemon reading
call site to pass the existing resolved root theme. V/W final hashes also match
their released bytes. I's daemon integration is the only post-lane source edit.

| Lane | Source ownership | Test ownership | Output and gate |
| --- | --- | --- | --- |
| V: visual system | `surfaces/presentation.py`, `surfaces/theme.py` | `tests/presentation_roundtrip.py`, `tests/theme_roundtrip.py`, `tests/responsive_product_roundtrip.py`, `tests/visual_character_roundtrip.py`, new `tests/ui_overhaul_visual_roundtrip.py` | Shared shell, tokens and composition; two identical-content local comparison previews in `prototypes/ui-overhaul-20260930/visual/`. Check light/dark/custom accent, focus, reduced motion, long content and 390px reflow. |
| N: navigation and course entry | `surfaces/daemon.py`, `surfaces/home.py`, limited to presentation helpers and markup, no API/persistence/scoring changes | `tests/desk_experience_roundtrip.py`, `tests/desk_craft_roundtrip.py`, `tests/course_shell_roundtrip.py`, `tests/course_resume_roundtrip.py`, new `tests/ui_overhaul_navigation_roundtrip.py` | Clear resume and course entry, reduced duplicated orientation, deliberate secondary administration. Preserve exact session links, shelf reorder, degraded/empty states and read-only GETs. |
| W: learning workspace | `surfaces/reading_desk.py`, `surfaces/lesson.py`, `surfaces/quiz_page.py`, `surfaces/quiz.py`, presentation only | `tests/reading_desk_roundtrip.py`, `tests/quiz_symbol_return_roundtrip.py`, new `tests/ui_overhaul_workspace_roundtrip.py` | Task-specific reading, lesson and response composition; no keyed disclosure or response serialization changes. Preserve source notes, draft recovery, reference return, native answer controls and no-script meaning. |
| I: integration | This packet after dispatch, `.planning/UI-SPEC.md`, `.planning/STATE.md`, `.planning/USER-VISION-INBOX.md`; source/test ownership transfers only after each builder releases its lane | new `tests/ui_overhaul_journey_roundtrip.py`; shared tests not owned above after lanes freeze | Inspect lane diffs, reconcile cross-surface composition, execute complete served journey and one combined source-only preflight on frozen inputs. Record exact limits and a single next action. |

Shared convention: use existing shell classes, design tokens, native controls,
route identity and JS IDs wherever possible. New classes start `overhaul-` and
do not define competing tokens. V may style the existing `reading-layout`,
`reading-column`, `reading-notes`, lesson and quiz roots, and `overhaul-*` hooks.
N and W own markup and any narrowly local CSS in their files, with shared
palette/font/spacing tokens. A missing shared primitive is an integration
request, not permission to edit another lane's file. Global nav markup belongs
to V's existing shared presentation module; N supplies course/entry context.

Each builder writes only its own evidence file:
`ui-overhaul-2026-09-30-V.md`, `ui-overhaul-2026-09-30-N.md`, or
`ui-overhaul-2026-09-30-W.md` in this research directory. Record changed paths,
baseline and final hashes, actual commands/results, observed screens or honest
preview gaps, unresolved integration requests, and explicit ownership release.
Do not edit STATE, shared vision records, this packet, or other lane evidence.
Do not run full preflight concurrently. Targeted checks and quick source-only
preflight are allowed. Never replace the user's installed app to obtain a preview.

## Readiness and acceptance

Readiness sampled synthesis section 16.3: goal, provenance, visual direction,
writer, non-goals, current authorities, recovery and observable gates are named.
No new durable format, registry, strategy, permission, rights, egress or migration
is introduced. Existing theme settings remain compatible. Novel interactive
teaching mechanisms stay in prior prototypes; this pass recomposes their
existing supported surfaces rather than committing new semantic contracts.

Integrate only when V/N/W have released ownership. I checks the actual rendered
source in a disposable synthetic root at desktop and 390px, long/multilingual
content, keyboard flow, light/dark, and representative failure/recovery states.
Runtime withholding in formal tests, pending prose, stable drafts and exact
session return are hard acceptance criteria. Navigation must not hide supported
capabilities merely to make screenshots cleaner. Source preview passes are not
human visual or accessibility acceptance.

Run relevant existing learner, reading, response, authority and accessibility
checks, then one `python3 scripts/preflight.py --source-only` after inputs are
frozen. Use installed Chrome through the existing visual-QA channel if its
default executable is absent. Read full diagnostic logs for failed gates.
The preserved dirty-tree failure and deferred build/schema/human gates remain
explicit; do not describe them as a clean full pass. Run another full suite
only for new changes or unresolved failures that justify it.

Final evidence stays in this packet. Integrator records IDs and status for the
four chats, what replaced old design, checks, remaining limits, source hashes,
undo instructions, and the single ranked next step in STATE. Build, installed
and human acceptance wait for their own gates. No extra summary or second
capability backlog is needed.

## Integration observations in progress

I compared V's actual quiet-light and workshop-light 1440px screenshots with
identical fictional content. The workshop puts source and private notes side
by side and uses separate grounds; quiet reading puts them in sequence. Adopt
the workshop as the reversible working direction for concurrent study tasks,
retaining measured prose and narrow stacking. This is an implementation choice,
not observed human preference. Both candidates and their controls remain saved
under `prototypes/ui-overhaul-20260930/visual/`.

The early served journey passed read-only entry, refused note save with
byte-identical accepted state, fresh-fingerprint retry, exact symbol/lesson
return, exam rationale withholding and reload without duplicate answers.
Chrome observed all six surfaces at 1280px/390px in light/dark, no horizontal
overflow, visible keyboard focus, local draft after refused save and reload,
successful retry, and exact reference return. These were evolving inputs and
need final frozen-source confirmation. Reading omitted theme CSS before this
pass; W repaired its default and optional resolved-theme input. I adopted
N's released daemon seam to preserve existing saved theme/accent settings.

## Frozen integration result

F1: The old 224px desktop rail and repeated workspace labels are replaced by a
compact horizontal frame. Home keeps exact saved-session entry and compact
course choices; Courses retains reorder, removal and recovery controls. The
reading desk pairs source with private notes; lessons keep measured prose and
widen existing code/table/diagram treatments; quiz input and runtime feedback
have separate composition. Existing routes, native names/IDs, response formats,
runtime disclosure, scoring and evidence authority remain intact.

F2: I inspected all eight actual task diffs against the dirty baseline, rather
than attributing the much larger inherited Git diff to this task. Final V/W
bytes match their handoffs; home matches N. Daemon differs from N only by the
one reading call-site argument supplying the existing resolved root theme.
Large modules were sampled at changed presentation symbols, callers and their
tests, not read in full. This is no backend or whole-vision audit.

### Final source fingerprints

The initial fingerprints are recorded in Base above and `base.sha256`; both
columns below identify the exact dirty input and integrated output.

| Source | Before SHA-256 | Final SHA-256 |
| --- | --- | --- |
| `surfaces/presentation.py` | `563a5bf9190adbbe7a09e71b0ecf71a38fa838a075d01f8aabe573beab070dfb` | `f3ae0422acc88c7235ec6d69a764966ef440ccb2c68397cf14d46d2d62970685` |
| `surfaces/theme.py` | `1380b674b1827505a6c28d36509b1ccd09e715deb37a8aed5d08e622488349e4` | `003282985f3e71447a6307ca852f1337d6db18f2c51b863544b0546b81dfc8d1` |
| `surfaces/daemon.py` | `72e66da98728c114fa813e6588fdbc408a560fdcc93cd4c2046068b8c2e76b9c` | `a7f8d77b9c6c6576bd2598d331f1465d8d2ec0c07cf019cdf1ca4f55ed7374e5` |
| `surfaces/home.py` | `24307ce5b56d0e4351392d4803b1a7b585b57fc3feb6f974e2a089bb5c2c95e3` | `90dafb159609c7f899f6ee1a7a36daf4b495c58fe0e732b04d081828d649d1a2` |
| `surfaces/reading_desk.py` | `0011e557ea9779b8b12ed2c6ecfc5578cf262f89c9e4c3ae01f4807f9bba4653` | `085244b14d3becb683fa86d5d1ba9eb51a2a6962f30fd5317dc64f1ec1ae1974` |
| `surfaces/lesson.py` | `8d9d3f34f8fa6f805b999a63768c69ab564174995ffa78e3c4e5f9b1a709da17` | `e7af446339d6904e64908ec62ad55027dfb3e4d8e2d96b1c68f2a29012ff56c3` |
| `surfaces/quiz_page.py` | `5bb9999c0f34998c2299f5b25618f6afb8ff86d0c4cbda2e7a9bc4a3b64c280f` | `598639300e9edd9f0f0ab49b401d39d1bc041d3dde2bd5e6873b3ba65b07636b` |
| `surfaces/quiz.py` | `b93d63ea7ac265b5c07d035edddce8a8b3d420d4b6465286cd8b15f4ead83fe3` | `01bd75abe3d059ca69deccd3e12ee135b4164b0b21449e3fceddd9103b5c9f70` |

### Commands, rendered behavior and diagnostic closure

`python3 tests/ui_overhaul_journey_roundtrip.py --browser-shots
.reasonix/ui-overhaul-20260930/final-journey-shots` passed on frozen production
inputs. Twenty-four source-served observations cover Home, Courses, overview,
reading, a long multilingual lesson and practice at 1280px/390px, light/dark.
Each has zero horizontal page overflow. The driven journey preserves notes
after an injected 503, reloads the local draft, retries successfully, selects a
native answer with the keyboard, submits through the runtime, returns from a
symbol reference to the exact sitting/item, and reloads without a second answer.
The HTTP leg proves read-only entry, refused-save byte preservation and fresh
fingerprint retry, saved custom theme/accent, exact admitted lesson return and
exam rationale withholding. Separate fictional banks per browser matrix cell
avoid conflating this first-response check with practice-retry semantics.

Final screenshots and `measurements.json` are in that local shots directory;
`final-journey.log` records the successful command. I inspected desktop reading,
narrow dark practice and narrow light overview, plus the earlier Home and
same-content comparison screens. W's twelve no-script desktop/narrow light/dark
captures additionally cover long source, code/table lessons and native quiz
fallbacks. V's 25 comparison renders cover desktop/tablet/390px/320px, custom
accent, keyboard focus, target size, reduced motion, resize input retention and
long/no-script content. Their named lane records own those checks and limits.

One `python3 scripts/preflight.py --source-only` ran after all source releases,
using `ITEMBANK_VISUAL_QA_CHANNEL=chrome`. A local `sitecustomize` capture hook
saved every subprocess's full diagnostics without modifying commands, results
or tests. `preflight.log` and `full-gate-logs/` preserve the run. It executed 170
Python scripts, deferred three app-build scripts, and ran 106 JavaScript cases.
The full run failed tests, JS and clean. Four Python failures and twelve JS
failures were stale presentation fixtures; each received a focused repair and
passed a targeted rerun. The other 166 Python scripts and 94 JS cases passed
in the combined run. No production edit followed its start and no equivalent
full suite ran concurrently or afterward.

| Diagnostic | Scoped repair and successful rerun |
| --- | --- |
| `cross_subject_suite_tracer.py` used the old Settings page hash | Updated `mode_layer_roundtrip.py` rendered-CSS baseline while retaining no-sections equality, saved accent and fixed-layer authority checks. Both mode-layer and cross-subject scripts pass. |
| `ia_route_roundtrip.py` counted exact class strings and expected Home reorder/removal | Count class tokens with HTMLParser and verify management controls/fingerprint on Courses. All 27 route checks pass; refusal, receipt, restart and empty-state assertions remain. |
| `model_ui_roundtrip.py` read a media-query threshold as a fixed element width | Restrict scan to actual min-width declarations. Disclosure, pending, zoom/motion and assist checks pass. |
| `presentation_profiles_roundtrip.py` expected the old response class assignment bytes | Assert both semantic response classes with additive presentation hooks. Public content, response forms and authority assertions pass. |
| `desk_craft_reorder.test.mjs` used compact Home as a reorder fixture | Render the actual full Courses collection and keep the production optional focus helper to preserve all saved-session lead checks. All 12 mouse/touch-cancel/keyboard/stale/network cases pass. |

Successful repair logs are `mode-layer-final.log`, `cross-subject-final.log`,
`ia-route-final.log`, `model-ui-final.log`, `presentation-profiles-final.log`
and `desk-reorder-final.log` in the same local evidence directory. Runtime
authority, pending prose, formal assessment and no-key checks passed in the
combined gate. Its actual Chrome accessibility matrix has thirteen positive
gates and the expected hover-only negative failure. Automated evidence is not
human accessibility certification.

Operational finding: the inherited local test snapshot
`.reasonix/chat-wrapup-20260930/surface-test-before.py` was counted as another
scorer because it contained a test named `check_study_no_scorer_or_response`.
I preserved it as `surface-test-before.py.txt`; both byte hashes are
`6a81b7f925eea740e00652fe42b6863737daa47d3da3c5ae10cdebac2b72ef52`.
The unchanged structural one-scorer gate then passed. Save inert code snapshots
with a non-executable suffix. Reverting the rename restores the false positive,
not a product scorer. A source journey probe also needed to wait for note-list
refresh after the saved acknowledgement; those are separate UI moments.

### Boundaries, recovery and next action

The dirty-tree gate remains unsatisfied because inherited and authorized
uncommitted work is preserved. This record claims full-run coverage plus
focused repair success, not a clean rerun or clean working tree. Sample/archive
builds, optional dependency installation and the two CI-only legs remain
deferred. Human visual preference, touch/screen-reader/learning-transfer review,
fresh package and installed acceptance remain open. P2-P5 semantic contracts,
whole-root restore crash/race publication, pinned live companion and Open
Notebook service gates retain their existing owners. No commit, push, new
build/archive/install/release, real course inspection or data upload occurred.

Exact integration patches are `.reasonix/ui-overhaul-20260930/I-<module>.patch`,
with the dirty baseline and final manifests beside them; lane patches remain
at their evidence paths. Undo only reviewed task hunks against current bytes,
then rerun the affected checks. Never reset the checkout or copy a baseline
over inherited work. Shared-test repairs are identified above; the new journey
test is independently removable. UI-SPEC and vision disposition point here;
no learner-data mutation needs undo because every test root was disposable.

The final synthetic source daemon is available for review in Codex's browser
panel. It uses a disposable fixture root and an ephemeral loopback port, so its
URL is session-local. Opening was queued by the app for this chat. It does not
replace the active learner installation. Next action, also recorded in STATE:
review this source preview for visual preference and representative accessibility.

Final record check: `python3 scripts/preflight.py --quick --source-only` passed
every running fast gate; build, full tests, clean and JS were explicitly skipped.
`git diff --check` passed. `shasum -a 256 -c` verified all eight source files,
the new journey test and five integration-repaired test files against
`final.sha256`. The full production/source hash table above remains unchanged.
