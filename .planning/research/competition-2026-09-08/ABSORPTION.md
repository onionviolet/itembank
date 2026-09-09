# Selective competitor absorption

Date: 2026-09-08. Status: deterministic comparison, guided progression, optional-tip folding, authored-wording highlights and inline excerpt previews are implemented in the native lesson renderer. See the latest reader expansion below for current verification. Human review remains owed. External-source grounding and generation remain prototypes.

## Decision against USER-VISION

Keep Itembank and absorb bounded capabilities. Do not fork OpenMAIC as the product base. The user's source-to-course, direct-reading, active-note, portable-lesson, and coherent-workspace goals call for useful treatments around a source. The September 8 clarification explicitly removes simulated classroom overhead from the default scope. This decision is recorded in USER-VISION and IDEA-LEDGER IL-20260908-04 and IL-20260908-05.

| Capability | Disposition | Concrete result and promotion gate |
| --- | --- | --- |
| Source-grounded lesson generation | Prototype | Pinned OpenMAIC generation package 0.3.6 behind a caller-owned model function. Trial exposes outline and single teaching-scene generation with four deterministic contract tests. Source-claim checks, portable Markdown, preview, validation, and accepted-revision recovery remain required. |
| Exact passage assistance | Prototype | Adapted DeepTutor normalization and range grounding with Apache-2.0 attribution. Twenty tests cover boundaries. Loopback UI prepares context only. Production must bind canonical sources and operation grants before calling a model. |
| Interactive explanations | Integrated bounded native treatments | Comparison, guided progression, highlight toggle and optional-tip folding use existing semantic content. The reader expansion below adds source previews and an outline. Human accessibility review remains owed. Broader activity formats remain candidates. |
| Teacher, classmates, discussions, voice, institutional LMS | Backburner | Not part of this default learner flow. Revisit only for a specific learner need with evidence that the extra cost helps. |
| External grading or evidence authority | Do not import | Generated practice remains a draft until Itembank validation. Itembank's runtime retains scoring and disclosure authority. |

## What was actually compared

[LANDSCAPE.md](LANDSCAPE.md) surveys 19 adjacent projects and products. Together with [the OpenMAIC code assessment](../OPENMAIC-ECOSYSTEM-COMPARISON-2026-09-08.md), this is a 20-candidate first pass, not an exhaustive market inventory. [REUSE-AUDIT.md](REUSE-AUDIT.md) identifies pinned reuse boundaries and licensing. [HANDS-ON.md](HANDS-ON.md) records the actual OpenMAIC and DeepTutor trials. Other candidates are documentation research, not successful installations or benchmarks.

OpenMAIC is ahead in visible generated presentation and interactive scenes. That does not establish that it is better for this user's complete workflow. Its source-only generation introduced unlabeled outside material in this trial. DeepTutor produced a useful local-model response but its reader assistance failed. Models and modes differed, so these are observations rather than a speed or quality ranking.

## Absorbed artifacts

### Visual-interaction clarification

The later September 8 USER-VISION entry explicitly retains interactiveness and bright text highlighting while excluding conversational presentation. IL-20260908-06 owns this registered direction. The intended lesson is visually expressive and directly manipulable.

Adopt semantic highlighting for key terms, relevant passages, and the current explanation step. Candidate supporting treatments include click-to-reveal explanation steps, adjustable diagrams, sliders, and small transitions that make a change understandable. These examples interpret the direction rather than claim the user requested each control. Prefer existing renderer capabilities. Routine interaction should not require model calls.

Keep presentation emphasis distinct from learner annotations, source truth, and mastery. Provide readable contrast and a non-color cue. Controls need keyboard and touch equivalents. Motion respects reduced-motion preferences. Static Markdown retains the core explanation. Conversation, character rosters, turn-taking, and narration are not dependencies for these treatments. This clarification originally registered adoption criteria. Link one below now supplies prototype implementation and browser evidence, not production adoption or human visual acceptance.

The runnable work lives in `prototypes/competition/`. Grounding code is an attributed adaptation. The generator trial uses a pinned npm dependency without copying OpenMAIC source or adding root dependencies. Both remain isolated from production files, learner banks, scores, and evidence. No account, upstream fork, commit, or push was created.

[PROTOTYPE-REVIEW.md](PROTOTYPE-REVIEW.md) records independent review. Duplicate occurrence handling, exact remote-target approval, and canonical context offsets were addressed. Twenty grounding tests, four HTTP tests, and four generation fixture tests pass. Tests establish context handling and package-call behavior, not educational quality or accessibility certification. Quick repository preflight passes every executed gate except the pre-existing skill-mirror mismatch at `author-bank/_attempts`. Full suites were not run for these isolated prototypes. The vision audit has no missing interpretation, planning effect, named file, or inbox disposition. Its older soft relationship backlog remains.

## Discovery correction and next gate

The earlier research emphasized NotebookLM-adjacent product patterns. The prior repository search found no OpenMAIC or DeepTutor record. This supports a gap in competitor discovery coverage, not a claim about when every project became discoverable. Future research waves should include runnable GitHub alternatives, multilingual search, primary licensing, and one fixed learner task before implementing overlapping work.

The next production gate belongs to the existing course and reader workstream: one source, one objective, one requested treatment, one draft, deterministic validation, visible source links and synthesis labels, editable plain Markdown, rich preview, and recoverable acceptance. Keep the generator replaceable. Measure time to a usable artifact, corrections, source fidelity, and learner usefulness before adding orchestration. No separate classroom product or automatic multi-agent requirement follows from this research.

## Chain link one: interactive lesson, 2026-09-08

**F4, implemented as a prototype:** [Rainfall, side by side](../../../prototypes/competition/interactive-lesson/index.html) combines the unchanged synthetic source, visible origin and objective, bright bold highlighting, an adjustable comparison, direct reasoning disclosures and a complete static Markdown fallback. [Run instructions and exact evidence](../../../prototypes/competition/interactive-lesson/README.md) distinguish automated checks, browser observations and human legs owed. The interaction uses original browser code and makes no model call or durable write.

**F5, LiaScript trial completed:** the official LiveEditor compiled [the saved synthetic Markdown](../../../prototypes/competition/interactive-lesson/liascript-trial.md). Enter on Next revealed two explanation blocks in order, visibly changing `0/2` to `1/2` to `2/2`. Reload retained editor text. The [official compendium](https://raw.githubusercontent.com/LiaScript/docs/master/README.md) and [BSD-3-Clause runtime license](https://raw.githubusercontent.com/LiaScript/LiaScript/master/LICENSE) were inspected live. No runtime, template, quiz, script, narrator or storage code was imported. Offline packaging and exact hosted-runtime pinning remain unproved. The useful adopted pattern is progressive text enhancement. Native details cost less integration surface for this fixed lesson than another renderer.

**F6, gate and remaining limits:** four JavaScript tests and four Python tests pass. Browser inspection verified keyboard updates, reset/reload, static fallback with scripts disabled, zero network requests on routine interaction, reduced-motion behavior and a 390-pixel layout without horizontal overflow. Highlight contrast is 10.83:1 and 10.72:1. Touch injection was unsupported by the in-app browser. Physical touch, screen-reader announcements and human aesthetics remain owed. The source quote and raw target were verified, but the in-app raw-text preview was not. Quick preflight again failed only on the existing `author-bank/_attempts` mirror mismatch. No full suite or live generation success is claimed.

### Capability to existing owner

| Capability | Live owner sampled | Integration constraint and next action |
| --- | --- | --- |
| Authored emphasis | `surfaces/lesson.py:_inline`, `surfaces/presentation.py` | Keep escape-first rendering and semantic bold meaning. Add bright emphasis only in an explicit instructional context, not across every strong span. |
| Direct explanation reveal | `guided_stages`, `_stage_html`, `_callout_html` | Reuse semantic teaching content. A presentation reveal must never widen runtime-granted assessment disclosure. |
| Parameter comparison | `capabilities.py:callout_example` version 2, lesson renderer | Link two integrates an explicit bounded declarative treatment through the existing role. No arbitrary authored JavaScript or second bank parser. |
| Source and citations | Existing source binding and reading packet | Here RAIN-01 is a synthetic file and paragraph locator. Native work must retain the canonical source owner. Do not repair import undo by weakening R1 through R3. |
| Evidence and acceptance | Runtime and journal | No interaction event is a score, mastery or accepted evidence. Existing files and revision operations remain authoritative. |

### Complete landscape reconciliation

Evidence abbreviations: L = original LANDSCAPE documentation survey, H = HANDS-ON observations, R = REUSE-AUDIT pins, P = PROTOTYPE-REVIEW fixes, I = this interactive trial. These rows retain all 20 candidates. A retained prototype disposition is not a claim that it was installed.

| Candidate | Capability and disposition | Evidence | Owner and next action or trigger |
| --- | --- | --- | --- |
| OpenMAIC | Generation prototype, direct interaction pattern absorbed | H, R, I, native link two | Generator owner: live source-faithful candidate before promotion. Native reader owner: deterministic comparison integrated independently of model timeouts. |
| DeepTutor | Grounding prototype, fixes retained | H, R, P | Reader owner: canonical rich-DOM offset map and operation grants before production calls. Reader assistance failure remains open. |
| OpenTutor | Workspace/review prototype candidate retained | L | Course workspace owner: shared source-to-review trial when that lane begins. |
| Open Notebook | Source notebook prototype candidate retained | L | Source workspace owner: locator fidelity and export/recovery trial before reuse. |
| NotebookLM | Registered UX benchmark | L | Course UX owner: compare source/artifact discoverability using synthetic material only. |
| LiaScript | Progressive explanation prototype verified, enhancement pattern absorbed | L, I, native link two | Lesson renderer owner: native comparison integrated over static Markdown. Full runtime remains optional pending offline/package and compatibility evidence. Native staged disclosure is not claimed. |
| H5P | Interactive content prototype candidate retained | L | Activity adapter owner: one licensed type with offline/accessibility and runtime-submission boundaries before reuse. |
| Lumi AI Editor | Registered drafting/export reference | L | Authoring owner: inspect H5P provenance and review boundaries when export is scoped. |
| eXeLearning | Registered OER authoring/export reference | L | Publishing owner: editable export/reimport test and license review before incorporation. |
| Docling | Extraction prototype candidate retained | L | Source adapter owner: page/table/equation/image locator trial before promotion. |
| MinerU | Registered extraction comparator | L | Source adapter owner: license review then the same preservation fixture. |
| Marker | Registered extraction comparator | L | Source adapter owner: code/model license review before local benchmark. |
| Unstructured | Registered document partitioning reference | L | Source adapter owner: benchmark locator and hierarchy fidelity. |
| Anki | Partial integration already exists, broader round trip registered | L, native audit below | Review owner: preserve existing TSV export, APKG staging and read-only due counts. Verify the complete course round trip without scoring transfer before broader promotion. |
| FSRS | Partial integration already exists, upstream conformance unverified | L, native audit below | Review owner: the existing bounded FSRSStrategy replays settled objective events. Compare against a pinned reference before claiming full upstream algorithm compatibility. Scheduling is not mastery. |
| LearnHouse | Institutional publishing backburner | L | Publishing owner: revisit when multi-user publishing is accepted scope. |
| Moodle | Registered institutional integration | L | Integration owner: LTI/export boundary trial when institutional delivery is required. |
| Open edX | Institutional publishing backburner | L | Publishing owner: revisit for a real institutional deployment and maintenance case. |
| Kolibri | Registered offline distribution reference | L | Packaging owner: inspect license and one offline recovery flow before reuse. |
| Excalidraw | Learner diagram construction backburner | L | Learner artifact owner: revisit with a concrete drawing need and accessible static export. |

### Audit reconciliation and next action

Original L, H, R and P evidence is preserved. P's three grounding fixes stay fixed only within their recorded synthetic boundaries. The prototype does not resolve rich-reader offsets, remote manifests or persistence. R's earlier outline-only recommendation is historical: the existing generation trial now includes a single scene, but both live attempts timed out. I resolves the previous LiaScript trial gap and registered-only interaction row. It does not supersede broader extraction, notes, review or publishing lanes.

Link two now implements the native lesson integration below. No root dependency, production configuration, daemon, scoring, reading recovery, live generation or Phase 20 repair belongs to this change. Human checks, four-subject parity and exact import undo retain their existing owners and gates. No candidate was silently rejected or deleted.

## Chain link two: native comparison, 2026-09-08

**F7, integrated:** the existing `surfaces.lesson.lesson_page` and daemon route render [the synthetic fixture](../../../fixtures/lesson_comparison.md). Run `python3 tests/lesson_interaction_roundtrip.py --serve`, then open `http://127.0.0.1:8767/lesson/lesson_comparison`. This scoped harness uses the real daemon handler without opening a sitting or making the daemon startup update check. The CLI twin is `python3 itembank.py lesson fixtures/lesson_comparison.md --out /tmp/itembank-native-comparison.html`.

The explicit `[COMPARE: 12,18,24,mm]` first body line inside `[!EXAMPLE]` opts into fixed A, adjustable B, maximum and unit. Only bounded nonnegative whole numbers are supported, with maximum 1 to 10000. A static explanation is mandatory. The native page adds a labelled slider, reset, two labelled meters and a textual difference. Ordinary examples, tables and bold text keep their old rendering. Bright emphasis is scoped to this comparison and retains semantic bold, with measured contrast 13.71:1. The fixture names its objective, labels synthesis, links to the exact source excerpt and retains hypothetical static examples. The unrelated synthetic question exists only because the bank CLI requires an item. It is not linked as evidence of the rainfall objective.

**F8, authority and compatibility:** `model.parse_lesson_comparison` is the shared scalar validator for lint and render. No second bank parser, scorer, source model or evidence store was introduced. `runtime.glossable` checks the entire opted-in body before either controls or invalid static fallback can render. A withheld block has no authored body or parameters in the page. Missing runtime context fails closed. Required lesson gates still truncate before the component, including its script. The small trusted script uses DOM text and bounded input values only. It contains no authored-code evaluation, network request, persistence or submission. This is teaching presentation, not validated generation or accepted learner content.

The existing `callout_example` capability profile is version 2 and retains its registry identity. The additive lint code required two contract-coupled paths beyond the packet's candidates: `schemas/lint_error.schema.json` gained its enum member and `tests/lesson_roundtrip.py` gained the eighteenth-code expectation. Production changes otherwise stay in `model.py`, `capabilities.py`, `surfaces/lesson.py` and `surfaces/lesson_interaction.py`. Fixture and focused tests are the two new test artifacts. The large model and renderer files were sampled by symbol, not read in full. All initially dirty configuration, manifest, daemon-test, Phase 20 and reading files were left untouched by this link.

**F9, verification:** `python3 tests/lesson_interaction_roundtrip.py` passes 12 tests. They cover bounded and non-finite input, missing static explanation, absent opt-in, invalid fallback, hostile text and unit escaping, runtime-held key text, missing runtime context, required-gate truncation, continuous/guided/paced static content, no script egress or persistence calls, and a real native HTTP GET that leaves every file in its temporary root unchanged. Quoted nested markers and fenced examples remain inert. An unterminated fence cannot hide the next heading's invalid declaration from lint. `python3 tests/lesson_roundtrip.py`, `python3 tests/capability_profile_check.py` and `python3 tests/gate_roundtrip.py` pass. Existing ResourceWarning and DeprecationWarning messages in the focused unittest run are not regressions repaired here. The clean focused transcript used `python3 -W ignore::ResourceWarning -W ignore::DeprecationWarning tests/lesson_interaction_roundtrip.py`.

Browser inspection used the actual native route. Home and arrow keys changed B and its signed difference. Enter on reset restored 18. Reload after B=0 restored 18. A 390 by 844 viewport had scroll width 390. Reduced-motion emulation reported no comparison animation. Disabling scripts hid the controls while retaining explanation, initial arithmetic and source. Keyboard activation of the source link reached the exact excerpt anchor. Network monitoring recorded zero requests for slider and reset interaction. Temporary browser emulation was reset afterward. Physical touch, actual screen-reader announcements, print-device output and human aesthetics remain unverified. The browser accessibility tree exposes labelled slider, meters and status, which is not human certification.

A permitted read-only Sol reviewer checked the concrete disclosure and executable-content diff and found no disclosure or executable-content defect. Its nested-marker false positive and follow-up cross-heading fence validation gap were fixed with focused regressions. The review did not claim browser or full-suite coverage. The builder reran the final focused and lesson regression suites after these fixes.

`python3 scripts/preflight.py > /tmp/itembank-comparison-preflight.log 2>&1` completed all 118 Python scripts and the JavaScript suite. It returned 1 on `mirrors`, `tests` and `clean`. Of the Python scripts, 115 passed and three failed in that run. The final two lint-boundary fixes were followed by a fresh 12-test focused run and the full lesson regression, both passing. No second full preflight was run.

| Preflight finding | Disposition and evidence | Owner and next action |
| --- | --- | --- |
| Skill mirror mismatch | Existing `author-bank/_attempts` appears only under `.agents/skills`. The same failure is in prior prototype evidence. | Skill owner: reconcile attempts directory policy. Excluded from this slice. |
| Binding route test | `binding_roundtrip.py` received no status for its invalid-state request and its error formatting raised TypeError. A separate `python3 tests/binding_roundtrip.py` rerun passed. Cause of the first request failure is not established. | Binding test owner: investigate if it recurs. No deterministic comparison regression demonstrated. |
| Generated capability manifest | A fresh `python3 tools/capabilities_manifest.py /tmp/itembank-comparison-capabilities.json` differed only by the existing GET `/courses` route entry. This slice changes no routes or generator inputs. | Manifest owner: regenerate under that workstream. `capabilities.json` and its generator remain untouched. |
| Configuration fixture | A separate `python3 tests/config_roundtrip.py` rerun still fails `a rejected color still mutated accent.source`. `fresh_base()` copies the pre-existing local `#1e46c8` accent, but this assertion allows only absence or `#0e6e62`. This comparison edits no settings. | Configuration owner: reconcile fixture/default expectation. No unrelated repair here. |
| Dirty tree | Expected under the packet's explicit no-commit requirement and the recorded dirty baseline. | User owns later commit decisions. No commit or push performed. |

The JavaScript suite and remaining fast gates passed. Final fixture lint returned zero errors and five advisory warnings: no item ID, no subject prefix, no second-best explanation, and two intentionally untested reading headings. No evidence is recorded against that protocol-only item. The prior four-subject parity limitation is preserved as historical evidence. That script did not fail this particular run, which does not certify its deferred backend or human gates.

**F10, recovery and reuse:** the accepted synthetic input remains unchanged at SHA-256 `1390b17a901010d3ec747fda3d8aa3b3e850d1409ec37aa480ab79439eeeb008`. The native fixture after authoring is `b9c3dbb197c571f24769f60ac8f9b40be54137285ed405448516690a580dc41c`. Rendering and HTTP tests preserve input bytes and create no learner evidence. This does not prove import undo or clean-machine restore. R1, R2 and R3 remain with the source/recovery owner.

OpenMAIC's direct-manipulation pattern and LiaScript's enhancement-over-readable-text pattern informed this original native implementation. No upstream code, runtime, package or license text was copied into production. Existing pins and prototype notices remain unchanged. LiaScript staged progression remains a tested prototype, not a newly shipped native disclosure mode. All 20 landscape candidates retain their dispositions, owners and next triggers above. DeepTutor's bounded fixes, the two failed local generation trials, Phase 20 human debt and the separately owned parity issue remain explicit.

**Chain disposition:** stop after link two. The selected deterministic capability is integrated and its applicable gates pass. No successor was created. Human review and unrelated repository failures remain open with their named owners. Generation hardening is not a dependency and was not started.

## Native UI repair and capability reconciliation, 2026-09-08

This pass implements three concrete presentation repairs. It does not claim
that all desirable competitor capabilities have been absorbed. All 20 candidate
rows above remain retained. Their research evidence is not installation or
native integration evidence. No upstream code, license choice, dependency,
model call, or private-source upload changed, so upstream licensing was not
re-researched. Existing pins and trial limitations remain authoritative for
those historical trials.

### Repairs and observable evidence

| ID | Failure and repair | Verification and remaining boundary |
| --- | --- | --- |
| P-20260908-04 | Selected Learn and Practice labels computed to identical `#243a44` text/background, 1:1. Product CSS overrode only Neo's selected foreground. The product rule now owns both colors, using `--paper` on `--product-ink`. | Native Learn route visibly repaired. Selected contrast is 10.91:1. Underline, `aria-current`, and focus survive. No navigation-state mismatch was found. |
| P-20260908-04, nearby finding | Inactive 14px pill labels used `#65716f` on `#e6eade`, 4.15:1. Shared course-link text now uses existing product ink. | Browser confirms darker text on the same pill background. This fixes contrast without changing stored appearance settings or profile identity. |
| P-20260908-05 | Lesson Courses and course/help/recovery Back to courses links retained `/`, which now renders Your desk. Four destinations now use the existing `/courses` route. | Before repair, clicking the lesson link opened Your desk. After repair it opened Courses. The missing-course-metadata regression also verifies the correct fallback destination. |

Only `surfaces/presentation.py`, four navigation destinations and one comment
in `surfaces/daemon.py`, the new `tests/navigation_color_roundtrip.py`, two
related expectations in `tests/course_shell_roundtrip.py` and
`tests/presentation_profiles_roundtrip.py`, this owner, and
`PROBLEM-LEDGER.md` belong to this pass. The two production modules
were clean at collision checks. Both were read by relevant symbols rather than
in full. Earlier native-comparison edits, dirty settings, manifests, tests, and
Phase 20 files remain outside this pass's writes. No commit or push occurred.
Undo this pass by reversing only these reviewed hunks and removing its new test
file. Preserve all earlier dirty work.

The original server at 8767 reproduced the defect. A fresh, task-owned scoped
daemon at 8768 loaded the repaired code without stopping the other task's
server. Launch it with `python3 tests/navigation_color_roundtrip.py --serve`.
Its `/ui-state` route supplies synthetic configuration fixtures. Its native
course and lesson routes use the actual daemon and renderer, admitting only
the synthetic Unit 3 and comparison banks. The earlier empty Learn/Practice
observations were a restricted bank inventory, not evidence of missing course
content. Once Unit 3 was admitted, Learn displayed its real lesson link.
The old prototype port 8766 refused a connection in this pass. No generation
trial was restarted.

Browser checks covered 56 configurations: seven looks, light/dark/OLED/system
settings, and both presentation profiles. Each was checked in normal, hover,
focus-visible, active, and emulated visited states, totaling 280 selected-link
states. All retained the paired colors and underline. All focus-visible cases
had a solid outline. None overflowed at desktop width. Browser privacy limits
computed visited-style inspection, so this is cascade coverage, not a history
inspection. Primary links, pressed buttons, disabled buttons and a teaching
callout were also inspected in the configuration fixture. Disabled controls
retain their disabled state and existing opacity.

At 390px the real course navigation opens with Enter, wraps without horizontal
overflow, and provides 44px-high links. Doubling every computed text size in
the document retained 390px scroll width and readable selected text. This is
an emulated text-growth check, not human browser-zoom certification. Reduced
motion and increased-contrast preferences were emulated and navigation
transitions computed to zero. All temporary document and browser overrides
were reset. The existing product shell supplies its accepted fixed palette
across appearance settings. These checks do not claim that the learner shell
implements distinct dark or OLED palettes. That product decision remains with
Phase 20 and P-20260908-02/03.

Overview, Learn, Practice, Test and Sources were walked through their actual
links. The selected label and heading matched each route. Learn opened Unit 3,
whose glossary controls, key-point card, example, diagram, warning and source
citations remain present. The native rainfall lesson slider changed B to zero
with Home, Reset restored 18 with Enter, and its source link reached
`#source-rain-01`. At 390px it did not overflow. Physical touch, screen-reader
announcements, full 400 percent browser zoom, print-device output and human
aesthetic acceptance remain unverified. No sitting was submitted or source
import performed during the browser walkthrough.

### Capability matrix against the actual product

“Integrated” below is deliberately bounded to the named native behavior.
“Partial” means useful native foundations exist but the complete learner flow
or requested breadth has not passed. Test evidence is from the commands in the
verification record below, not merely the presence of a test file.

| Capability and learner value | Native evidence and observable flow | Disposition | Owner, dependency, next action and revisit trigger |
| --- | --- | --- | --- |
| Source fidelity and exact locators | `source_adapters.py` and `source_binding_surface_roundtrip.py` exercise locator sidecars and source-binding rights. Unit 3 visibly renders `[SRC: ...]` text without a source-opening link. The comparison fixture's explicit source anchor does work. | Partial native source support. DeepTutor selection grounding remains prototype. | Source/reader owner. Depends on canonical source-to-DOM offsets, rights and existing bindings. Next: one selection must resolve to an unchanged canonical passage and refuse a stale fingerprint. Revisit when implementing G1, not by accepting client text as source truth. |
| Direct reading instead of unnecessary rewriting | Unit 3 explicitly assigns the lagg-boundary source section without paraphrasing it, but does not provide an actionable source-opening link. `SOURCE-TO-READING-NEXT-PACKET-2026-09-08.md` owns the occurrence prototype and R1-R3. | Partial treatment support, integrated reader journey deferred. | Existing source-to-reading owner. Next: source-open, locator, occurrence and resume trial over an existing local source. Durable import depends on exact reversal, prior absence and sidecar recovery. Trigger: existing next packet, not a new source model. |
| Portable lessons, definitions and semantic teaching | `model.parse_lesson`, `surfaces.lesson.lesson_page`, glossary and callout rendering. Native Unit 3 displays seven sections, glossary buttons, a described diagram and semantic callouts. `lesson_roundtrip.py` exercises plain/rich contracts. | Integrated bounded native lesson foundation. Broader authoring convenience partial. | Lesson owner. Preserve single parser, static meaning and runtime disclosure. Next: author one missing objective treatment using existing roles. Revisit when a teaching need cannot be expressed, not merely because another renderer has a widget. |
| Readable emphasis | `surfaces/lesson_interaction.py` scopes yellow bold emphasis to explicit comparison. Native comparison displays it alongside synthesis labels and a static explanation. This pass fixes shared navigation contrast. | Integrated scoped emphasis. General passage emphasis registered. | Presentation/lesson owner. Depends on explicit teaching purpose and contrast/non-color meaning. Next: trial one authored emphasis case outside comparison before a grammar change. Trigger: G2 and an actual passage needing emphasis. |
| Progressive explanation | Existing `guided_stages` and `_stage_html` present semantic stages. LiaScript's two-step trial is recorded above. The rainfall native comparison does not implement new staged disclosure. | Partial existing guided reader. New progressive explanation remains prototype. | Lesson owner. Depends on disclosure tier and useful static fallback. Next: compare existing guided rendering with a bounded learner-controlled reveal over the same accepted prose. Promote only after keyboard, no-script, gate-truncation and human review. Trigger: G2. |
| Deterministic interaction | Example v2, shared `model.parse_lesson_comparison`, `lesson_interaction.py`. Native slider/reset/source flow was rechecked. `lesson_interaction_roundtrip.py` tests bounds, escaping, disclosure and no durable writes. | Integrated bounded comparison. H5P and broader diagrams remain prototype candidates. | Lesson/activity owner. Next: reuse this capability for a suitable objective. A new control needs its own finite declarative contract and runtime review. Trigger: a changed teaching demand that static examples and this comparison cannot meet. No generated executable lessons. |
| Learner notes and diagram construction | `notes.py` has anchored learner wording and separate artifact records. `note_outputs.py` projects notebook, Cornell and concept-map outputs from one parse. Note schema/trio/promotion tests exercise these foundations. The walked Unit 3 reader has no complete capture-to-reopen note workflow. | Partial native foundations. Excalidraw remains backburner, not absorbed. | Learner-artifact owner. Depends on paired-document recovery, source anchors and accessible construction. Next: capture one note, reopen at its exact passage and export its plain form without promotion to truth. Trigger: G3. Drawing follows a real diagram task and equivalent static representation. |
| Practice and formal assessment | Existing runtime and native lesson-to-practice link. `daemon_roundtrip.py` exercises served scoring, disclosure, PRG and session routes. No browser sitting was submitted here. | Integrated assessment foundation. Competitor activity-format breadth partial. | Runtime/activity owner. Preserve one scorer, pending prose and target blueprint. Next: use `author-bank` for a cited objective-aligned gap. Trigger: demonstrated format/construct need. No external grading or second evidence store. |
| Review scheduling and Anki interoperability | `retention.FSRSStrategy` already derives objective due state from settled-event replay. Retention UI tests exercise Today, report and Anki-unavailable states. `surfaces/anki.py` exports TSV, `import_anki.py` stages APKG, and Anki tests exercise stable IDs and separation. | Partial integrated review/export, correcting the earlier registered-only survey. Full upstream FSRS conformance and end-to-end course round trip unverified. | Review owner. Next: replay identical settled events against a pinned reference, then test one learner-owned export/import cycle and due-state separation. Trigger: G4. Do not call the bounded native strategy equivalent to current upstream FSRS without that comparison. |
| Extraction of PDFs and external formats | `source_adapters.py` and its roundtrip cover native PDF and additional format fixture families, with typed refusals and locators. Docling, MinerU, Marker and Unstructured have not been imported or benchmarked here. | Partial native extraction. Competitor adapters remain prototype/registered as above. | Source-adapter owner. Depends on source-specific fidelity and licensing/model/egress review. Next: same page/table/equation/image fixture with original bytes preserved and explicit losses. Trigger: a native extraction failure that warrants G1 extension. R1-R3 are not waived. |
| Source-grounded generation | Existing seed/audit-author contracts are separate from the isolated OpenMAIC outline/scene trial. Both recorded local generation attempts timed out. DeepTutor's successful chat was not successful reader assistance. | Prototype competitor generation, no validated native source-to-lesson generator claimed. | Course-authoring owner. Depends on one source, one objective, approved treatment, citations, plain Markdown, preview and recoverable acceptance. Next: produce one source-faithful draft with a replaceable backend only when model calls are authorized. Trigger: G5. No automatic acceptance. |
| Publishing, offline export and recovery | `course_package.py` exports manifests and restores supported payloads. `course_package_roundtrip.py` exercises a clean destination and named losses. This does not repair source-import undo or prove institutional publishing. | Partial native packaging. Institutional publishing remains registered/backburner. | Package owner. Depends on rights, supported-object coverage and offline restoration. Next: restore the selected learner course on an empty destination and inspect every loss before promising a backup. Trigger: a real export/delivery request. Retain Kolibri, Moodle, eXeLearning, Lumi, LearnHouse and Open edX references without importing their authority. |

### Skill-contract coverage

This is a contract comparison, not mechanical execution of six authoring
workflows. `absorb-book` requires objective-sized treatment selection, direct
reading when appropriate, citations and synthesis labels. `curriculum-design`
requires taught/tested/prerequisite separation and sourced target demand.
`author-bank` requires inventory, lint, distractor and blueprint review, and
runtime-owned results. Those conditions remain promotion gates in the matrix.

`legacy-upgrade` is shipped as a read-only baseline/diff audit. Its source,
rights and media stand-ins are explicitly not passes. No legacy artifact was
rewritten here. `media-intake` is a stub. `lesson-authoring` and
`discovery-and-binding` also remain stubs, so none can support a claim of a
complete authoring or intake workflow. Existing image/diagram rendering does
not itself provide per-asset rights and lifecycle management. Relevant
operation contracts remain required when those lanes become executable.

### Five useful remaining gaps, ranked

| Rank | Bounded next result | Gate and existing owner |
| --- | --- | --- |
| G1 | Open the assigned source passage from a course and resume the same reading occurrence. | Existing source-to-reading packet. Keep locator identity exact and preserve R1-R3 before durable import. |
| G2 | Add a justified progressive explanation over existing semantic prose. | Lesson owner. Keyboard reveal, static fallback, disclosure safety and human review. LiaScript prototype evidence is a starting point, not native completion. |
| G3 | Capture and reopen one anchored learner note in the normal reader. | Learner-artifact owner. Preserve learner ownership, exact passage, plain export and recovery. |
| G4 | Make the existing review schedule and Anki boundaries verifiable in one course flow. | Review owner. Deterministic replay, reference conformance and export/import evidence without score transfer. |
| G5 | Produce one source-faithful generated lesson draft. | Authoring owner. Authorized backend, complete citations/synthesis labels, deterministic validation and reviewable acceptance. Prior timeouts remain failed trials. |

These are bounded proposals, not newly accepted milestone expansion. No
successor task was created. Human Phase 20 review and prior four-subject parity
debt retain their existing owners.

### Verification record for this pass

`python3 scripts/preflight.py > /tmp/itembank-ui-absorption-preflight.log 2>&1`
completed all 119 Python scripts and the JavaScript suite. It returned 1 on
mirrors, tests and clean. There were 115 passing Python scripts and four
failures in that captured run. It includes passing native comparison, lesson,
source-adapter, source-binding, note schema/trio/promotion, retention/retention
UI, Anki import/export, legacy-upgrade and course-package checks. Their
synthetic coverage does not establish broader competitor conformance or human
acceptance. Binding passed this run. The earlier binding request failure was
not reproduced.

| Check or finding | Current result and disposition |
| --- | --- |
| `python3 tests/navigation_color_roundtrip.py` | Final run passes all 3 tests, including 56 appearance/profile combinations and the metadata-unavailable Courses link. Before repair, selected-style ownership and the old destination failed separately. |
| `python3 tests/course_shell_roundtrip.py` | Failed in full preflight because it counted the application current-page link together with the two course-menu links. Fixed to require exactly one current Learn link in each course menu. Final focused run passes. This was an assertion scope defect, not lost native selection. |
| `python3 tests/presentation_profiles_roundtrip.py` | Final run passes all checks after updating its expected Courses href to `/courses`. Both profiles retain public content, response fields and context. |
| `python3 tests/stylesheet_roundtrip.py` | Final run passes 27 stylesheet checks. Existing off-scale Settings/day/study typography and supplied-token notes remain reported limitations. |
| `python3 tests/daemon_roundtrip.py` | Separate post-navigation-repair run passes all 78 served checks. Transcript: `/tmp/itembank-ui-daemon.log`. |
| `python3 tests/capabilities_roundtrip.py` | Fails both broad and targeted runs with stale `capabilities.json`. Existing dirty manifest/generator remain with their owner. This pass adds no production route or capability. |
| `python3 tests/config_roundtrip.py` | Fails both broad and targeted runs with `a rejected color still mutated accent.source`. Existing custom accent fixture mismatch remains with the configuration owner. Settings were not changed. |
| `python3 tests/cross_subject_suite_tracer.py` | Broad run exited after its first scenario. Targeted rerun reports 8 passed, 1 failed: extended 16B settings-page baseline expected `bd95f46...`, actual `3c23e67...`. Reversing only this task's product CSS in memory leaves the actual hash unchanged, so the mismatch is not caused by this repair. Preserve the already-dirty mode-layer baseline and route this to its owner. This is distinct from prior four-subject backend availability debt. |
| Skill mirrors | Existing `.agents/skills/author-bank/_attempts` directory has no mirror. No skill files were changed. |
| Clean tree | Expected failure under the no-commit instruction and initial dirty checkout. No commit or push was made. |

The full run began with the color fix and completed while the stale course-link
repair was being verified. Final focused runs above cover that repair and its
two assertion updates. No second full suite is claimed. Final quick preflight
is recorded below after the last code and expectation changes. `git diff
--check` passes. Human acceptance remains open, not inferred from these checks.

Final `python3 scripts/preflight.py --quick` returned 1 solely on the existing
skill-mirror mismatch. Lint, broken fixture, build, guard, README, schemas,
vendored dependencies, path hygiene and summary checks passed. As designed,
quick mode skips Python suites, JavaScript and dirty-tree checks. Transcript:
`/tmp/itembank-ui-absorption-quick.log`. The task-owned 8768 preview is left
running for review. The pre-existing 8767 server still holds its older imports
and needs its owner's restart to display the new code.

### Authorized restart and publication follow-up, 2026-09-08

The user subsequently requested restart, commit and push. The original 8767
process was restarted with its existing
`python3 tests/lesson_interaction_roundtrip.py --serve` command. Browser
inspection on that port confirms Learn now uses light text on dark product
ink. Its comparison-only bank inventory remains unchanged. The populated
Unit 3 audit preview remains available on 8768.

The publication scope is the two repaired production modules, three UI test
files, problem ledger and this reconciliation owner. Earlier native-comparison
implementation, prototype/research inputs, settings, manifests and Phase 20
work remain separate local uncommitted work. Integration evidence above was
measured in that combined local checkout, not a claim that all those inputs
are included in the UI repair commit. The navigation, course-shell and
presentation-profile suites passed again after restart.

## Native reader absorption expansion, 2026-09-08

The user explicitly asked to absorb LiaScript highlighting and other platforms
as well. USER-VISION and IL-20260908-07 preserve both statements. This expands
the implementation scope beyond the two original comparison links. The full
20-candidate matrix above remains active. No whole-platform parity is claimed.

### Implemented reader slice

`surfaces/lesson_progressive.py` enhances the existing guided mode. The native
lesson route now exposes `Read step by step` and `Read continuously`. It uses
the existing parser, semantic roles, source excerpts and runtime truncation.

| Reference pattern | Native result | Evidence boundary |
| --- | --- | --- |
| LiaScript progressive explanations and visual emphasis | Next explanation, show all, restart, current-step border and a learner-controlled highlight toggle over authored bold wording. | Native implementation, not a LiaScript runtime import. Plain Markdown remains unchanged and readable. No new narration or model call. |
| H5P accordion-style optional detail | Existing optional Expert tip blocks become independently collapsible native details in guided mode. | Tips begin open. Required blocks, assessment checks and source excerpts are not collapsed by this rule. This is pattern reuse, not H5P package compatibility. |
| Source notebook citation navigation | A lesson outline opens permitted headings. A citation to one unambiguous rendered excerpt gets an inline source preview. | No new extraction, retrieval or remote assistance. Ambiguous and external source links retain their ordinary behavior. This does not close G1 or claim exact external-document reader integration. |
| OpenMAIC direct manipulation | The prior native rainfall comparison remains available alongside the new reading controls. | Existing bounded comparison only. Rich scene generation and other simulations remain separate. |

The H5P pattern was refreshed against its official
[Accordion description](https://h5p.org/accordion). The wider source-workspace
comparison was refreshed against [Open Notebook](https://github.com/lfnovo/open-notebook).
[LiaScript documentation](https://github.com/LiaScript/docs) and the earlier
live two-step trial remain the progression references. Original implementation
was written here. No third-party code or dependency was copied or installed.

### Broader absorption remains owned

| Lane | Platforms retained | Remaining concrete result |
| --- | --- | --- |
| Source reading and assistance | DeepTutor, Open Notebook, NotebookLM, OpenTutor | Exact external-source occurrence, source selection and anchored notes through canonical owners. Inline excerpt previews are a smaller completed step. G1 and G3 remain open. |
| Generation and authoring | OpenMAIC, OpenTutor, Lumi AI Editor, eXeLearning | One source-faithful editable lesson draft with citations, validation, revision and recovery. G5 remains open. |
| Rich teaching | LiaScript, H5P, Excalidraw | Broader diagrams and finite interaction types follow demonstrated objective needs. Guided progression is now implemented. External format compatibility and drawing remain unproved. |
| Review | Anki, FSRS | Pinned scheduling conformance and one course-level export/import flow. G4 remains open. |
| Extraction and delivery | Docling, MinerU, Marker, Unstructured, Kolibri, Moodle, Open edX, LearnHouse | Source-fidelity adapter trials and offline restoration before new dependency or package promises. Institutional delivery retains its existing disposition. |

### Authority and verification

Accepted lesson Markdown remains the source of truth. DOM state is disposable
and resets on reopening. The renderer owns presentation, while the runtime
owns checks, disclosure and scoring. No content write, model call, storage,
telemetry or accepted-evidence event is introduced. A required check truncates
content before enhancement, so show-all and source preview cannot fetch the
withheld remainder. Source excerpts are copied as text, never executable HTML.

Automated JavaScript checks use the real generated page to verify independent
stages, reveal/reset, highlight toggle, source jump, folded-tip print recovery,
unchanged authored wording and the no-script fallback. Python checks verify
required-check truncation and static content. The existing lesson suite passes
after correcting its obsolete Courses-link expectation from `/` to `/courses`.
An intermediate loopback timeout was retried successfully without loosening
the test. The 12-test comparison suite also passes.

Browser observation on the native route verified progression from 1/3 to 2/3,
highlight toggling and keyboard expansion of the optional tip. Human touch,
screen-reader, zoom and aesthetic review remain owed. The full preflight result
is recorded separately below when the run completes. No commit or push was
requested or performed by this pass. Large modules were sampled around the
guided renderer and lesson route, not read in full.

### Final reader expansion verification

The full preflight completed all 120 Python scripts and the JavaScript suite.
There were 116 passing Python scripts and four failures: the stale capability
manifest, rejected-color accent state, extended 16B theme-page baseline, and
the unavailable four-subject parity backend. These match previously recorded
findings outside this reader slice. Skill mirrors also fail on the existing
unmirrored `author-bank/_attempts` directory. Clean-tree fails with the shared
uncommitted changes. Transcript: `/tmp/itembank-progressive-full.log`.

The final quick preflight fails only on skill mirrors. Its other executed
gates pass. Transcript: `/tmp/itembank-progressive-final-quick.log`.
The final three JavaScript reader tests pass, including repeat citation clicks
after restarting with the same URL fragment. The two Python reader tests and
12 comparison tests pass. No second full run is claimed.

The final browser pass verified the inline quoted source preview, source jump,
restart and highlight toggle. A 390-pixel viewport had a 390-pixel document
scroll width. The highlighted text uses foreground RGB 24,37,27 on background
255,240,138 and an underline. Native shared button styles are used. The
temporary viewport override was reset. The scoped synthetic preview remains
available on port 8769 with `?view=guided`. Human accessibility and aesthetic
acceptance remain open.
