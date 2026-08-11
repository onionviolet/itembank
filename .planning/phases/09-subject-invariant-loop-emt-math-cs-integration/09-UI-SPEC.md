---
phase: 09
slug: subject-invariant-loop-emt-math-cs-integration
status: approved
reviewed: 2026-08-08
shadcn_initialized: false
preset: none
created: 2026-08-08
updated: 2026-08-08
---

# Phase 09 — UI Design Contract

> One learner loop, enhanced in place for EMT prose/tables, offline Math, and CS examples. The subject profile may enable a medium; it may never select a separate application, parser, scorer, runner, evidence writer, or teaching-state machine.

## Authority and decision legend

| Mark | Meaning |
|---|---|
| **LOCKED** | Binding decision in Phase 9 `CONTEXT.md`, requirements, or upstream contracts. Implementation may not reinterpret it. |
| **UPSTREAM** | Contract owned by an earlier phase and consumed here. Do not replace it. |
| **PHASE 9** | Precise presentation or interaction rule owned by this document. |
| **BACKSTOP** | Requires held-out visual, keyboard, or assistive-technology evidence in addition to structural tests. |

**Authority boundary — LOCKED.** One parser (Phase 3), one scorer (`runtime.score_response`), one teaching transition (Phase 6), one bounded runner (Phase 5), and one append-only evidence store remain authoritative. Profile selection is server/runtime policy persisted with the session. Browser adapters, raw source, model output, and Run observations are display inputs only. They cannot decide correctness, advance the cursor or hint tier, fabricate provenance, or write accepted evidence.

### Binding decisions and requirements

| Contract | UI consequence |
|---|---|
| D-01–04 / LOOP-01 | Persist one selected versioned profile. Keep shared document order and loop language; unknown capability requests are explicit, and mixed subjects require a profile choice before a session exists. |
| D-05–06 | Enhance Phase 3 semantic output in place. Unsupported media keeps escaped/source content visible with a durable notice. |
| D-07–08 / LOOP-02 | Render `$…$` and `$$…$$` locally only; raw TeX is the baseline/fallback and browser math is never assessment. |
| D-09–11 / LOOP-03 | Lesson Run reuses the Phase 5 runner/refusal path and returns observation only. It is not a check submission. |
| D-12–13 / LOOP-04 | EMT remains semantic shared prose and native tables; a table scroll region, not the page, owns horizontal overflow. |
| D-14–15 / LOOP-05 | One guided sequence and fixture driver serve EMT, Math, CS, and a configuration-only fourth subject. |

### Existing Phase 9 plan classifications

| Plan | Classification | UI execution boundary |
|---|---|---|
| 09-01 | **UPSTREAM-CONTRACT** | Profile/session/schema and shared-loop work may proceed. Its semantic table and narrow-container hooks must meet this contract. |
| 09-02 | **UPSTREAM-CONTRACT** | Registry/settings and configuration-only fourth-profile work may proceed. Public capability notices use this status and copy grammar. |
| 09-03 | **UI-INDEPENDENT** | KaTeX legitimacy, license, checksum, inventory, and human approval remain non-UI work. No asset is introduced before that gate. |
| 09-04 | **UI-BLOCKED** | Local math asset serving may proceed, but rendering, fallback, MathML, responsive overflow, and offline states must implement this spec. |
| 09-05 | **UI-BLOCKED** | Runner refactor may proceed; runnable blocks, profile notices, guided-discovery integration, keyboard/status behavior, and visual states must implement this spec. |

## Design system and tokens

| Property | Contract |
|---|---|
| Tool / component library | None. Stdlib server-rendered semantic HTML, CSS, and small vanilla-JS enhancement; no React and no `components.json`. |
| Renderer owner | Phase 3 `surfaces.lesson` is the only markdown/lesson parser. Phase 9 adds stable hooks only at its semantic output seam. |
| Theme owner | Phase 4 generated theme tokens and focus/status primitives. Phase 9 adds no literal palette or subject palette. |
| Prose / code | Phase 4 system prose stack; Phase 5 `ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace` for source and output. |
| Icons | None required. Text and structure convey every status. |

### Spacing

Use the inherited 4px scale: `4, 8, 16, 24, 32, 48, 64px`. New subject-media blocks use 16px internal gaps, 24px between block regions, and 32px between guided-discovery steps. Buttons and compact controls are at least 44px in both dimensions. Only `.lesson-table-scroll`, `.lesson-math-display`, code editors, and output panes may horizontally scroll; the viewport never does.

### Typography

Exactly four text sizes and two weights apply to Phase 9 additions.

| Role | Size / weight / line height | Use |
|---|---|---|
| State metadata | 14px / 400 / 1.4 | Language, output labels, capability and recovery notices. |
| Body | 16px / 400 / 1.5 | Prose, cells, instructions, output context, hint/explanation. |
| Section heading | 20px / 600 / 1.2 | Lesson subsections and result headings. |
| Page title | 28px / 600 / 1.2 | One `h1`; visually 20px at narrow width without changing DOM order. |

Code and raw formula source use the 14px code stack at 1.5. Rendered inline math follows surrounding text; display math never reduces readable body text.

### Color

Use only Phase 4 tokens. The existing page/background surfaces are the 60% dominant layer; cards, table/editor/output containers are the 30% secondary layer; `--accent` is the 10% accent. Reserve accent for links, visible focus, the enabled **Run example** action, and an active scroll-region focus boundary. `--warn` is capability/unavailable text and `--bad` is request failure; neither is sufficient without the prescribed text. Math, profile identity, exit status, assessment state, and subject type never rely on color. There is no destructive action in this phase.

## Goals, information architecture, and shared learner journey

### Phase goals

1. Preserve a calm, single-column lesson where subject media appears in the source location rather than as a subject-specific dashboard.
2. Make the next learning move clear: read context, make a prediction/action, receive runtime-gated feedback, retry, then read explanation.
3. Make unavailable media honest without making lessons inaccessible offline.
4. Keep exploratory execution subordinate to assessment and ensure a fourth subject needs configuration only.

### Information architecture

```text
Lesson page (one 720px reading column)
├─ h1 + existing lesson navigation
├─ #lesson-content — Phase 3 source order
│  ├─ EMT: headings, prose, lists, native table in scroll region
│  ├─ Math: raw TeX baseline → local KaTeX enhancement
│  ├─ CS: escaped fence → optional runnable example block
│  └─ guided discovery: context → prediction/action → feedback/hint → retry → explanation
├─ existing adjacent assessable item / Phase 6 controls
└─ persistent, local status or recovery copy beside the affected medium
```

There is no subject picker dashboard, media feed, progress score, streak, badge, leaderboard, model chat, or separate “Math/CS/EMT mode” chrome. An explicit `profile` value is a start/lesson request parameter where the runtime requires it; it is not a client-supplied capability object.

### Common journey

1. The learner opens a lesson or starts a sitting. Runtime chooses and persists exactly one profile from the objective/bank or a valid explicit id.
2. The common reader presents authored context in source order. The profile only enables semantic adapters.
3. The learner performs the authored prediction/action, not a media control. A wrong assessed response follows Phase 6’s held-cursor and bounded-hint state machine.
4. The learner retries and then reads the explanation. Only the normal submit/hint/retry path can score and append evidence.
5. A source-medium failure leaves the text/source and common journey usable. The learner can continue studying; media failure is not an assessment result.

## Annotated responsive wireframes

The lesson title establishes orientation; the next unread context or explicit learner move is the primary visual focal point. Media, capability notices, generated assistance, and runtime status remain subordinate.

### Desktop (≥ 960px)

```text
┌──────────── inherited shell / lesson navigation ────────────┐
│  Lesson title (h1)                                           │
│  ┌────────── #lesson-content, max 720px ──────────────────┐ │
│  │ Context prose / list                                    │ │
│  │ [native EMT table inside named scroll region]            │ │
│  │ Inline math stays in this sentence;                     │ │
│  │ [display math: contained horizontal scroll if required] │ │
│  │ Example code · Python                                    │ │
│  │ [editable monospace source                         ]     │ │
│  │ [Run example]  Tab inserts indentation…                  │ │
│  │ Status (polite, concise)                                 │ │
│  │ stdout [pre]     stderr [pre]                            │ │
│  │ Prediction / assessed item → hint → retry → explanation  │ │
│  └─────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────┘
```

Annotations: source order is tab order; table/math/code are not side panels; status is adjacent to its medium; output is not live; the assessment action remains visually and semantically distinct from **Run example**.

### Tablet (600–959px)

```text
┌──── 24px gutters; one reading column ──────────────────────┐
│ Title / prose / medium blocks retain desktop order          │
│ [table scroll region: focusable, labelled, max-width 100%] │
│ [display equation: local contained scroll]                 │
│ [code editor full width]                                    │
│ [Run example, 44px min]  status below                       │
│ [stdout] [stderr] stack vertically when narrow              │
└────────────────────────────────────────────────────────────┘
```

Annotations: no sticky headers or columns may cover data. Controls do not move before the source they operate. Horizontal movement is local to the labeled region.

### Narrow / zoomed (320 CSS px and 200%)

```text
┌─16px─┬───────────────────────────────────────────────────┬─16px─┐
│      │ h1 / body wrap                                    │      │
│      │ [Table: keyboard-focusable horizontal scroll →]   │      │
│      │ [Math display: horizontal scroll →]               │      │
│      │ Example code / language                            │      │
│      │ [textarea: contained code scroll →]               │      │
│      │ [Run example]                                      │      │
│      │ status; stdout then stderr, each contained         │      │
└──────┴───────────────────────────────────────────────────┴──────┘
```

Annotations: page-level horizontal scroll is prohibited; touch/keyboard scroll regions have an obvious visible focus boundary; long cells and prose wrap with `overflow-wrap:anywhere`; tables never become screenshots, cards, or hidden columns.

## Major interaction contracts

Every row is an implementation and test contract. “Model” always means an optional teaching/model adapter and never a source of authority.

| Interaction | Goal / state / learner action | Response and evidence | Model and deterministic enforcement | Failure / accessibility / acceptance |
|---|---|---|---|---|
| **Profile start or resume** | Start a common lesson/sitting; `unresolved → persisted` or `legacy → one-time persisted`; learner may provide only a profile id where needed. | Render current profile’s allowed enhancements; record selected subject/profile snapshot in session through existing session path. No media click creates evidence. | Model has no role. Server validates registry, subject and explicit id once; resume reads stored snapshot, never current registry/bank inference. | Unknown uses conservative plain-markdown profile with named unavailable capabilities; mixed subjects stop before session/evidence creation and require an explicit known id. Expose no absolute path. **Accept:** resume-drift and mixed/unknown tests pass. |
| **Guided discovery / assessment** | Learn in `context → prediction/action → wrong → hint eligible → retry → explanation`; learner answers the explicit assessed item or requests a permitted hint. | Phase 6 renders targeted authored/runtime-gated feedback and holds/advances cursor; standard response/hint events are the only learning evidence. | A model can propose a hint only behind the existing tier gate; runtime transition/scorer decide what appears and evidence shape. Media does not trigger a transition. | If model/provider fails, keep authored context and permitted authored hint path; announce provider unavailability only if shown, never a score. Keyboard reaches the assessed control after media in source order. **Accept:** identical transition/evidence keys across EMT/Math/CS/fourth and no leaked answer before the allowed tier. |
| **EMT semantic table** | Read clinical prose/table; `populated` or `narrow-overflow`; learner focuses the named region and scrolls it. | Preserve caption/nearest-heading name, native `<table><thead><tbody><th><td>` order and cell text. Table interaction creates no evidence. | No model role. Shared Phase 3 renderer is the sole parser; CSS wrapper deterministically owns overflow. | Long cells wrap; long unbreakable identifiers may break; no clipping/tooltips/screenshots. Native headers have `scope`; wrapper is focusable without replacing table roles. **Accept:** 320px/200%, keyboard/SR header-cell navigation, then next content; no page overflow. |
| **Offline Math enhancement** | Read authored formula; `source baseline → enhanced` when profile/local assets are valid. No learner action is required. | Local CSS/JS/fonts enhance only `#lesson-content`; inline stays inline, display uses `.lesson-math-display`; successful output retains MathML. No score/cursor/evidence change. | Model has no role. Profile and closed local asset map gate enhancement; `$$…$$` delimiter precedes `$…$`; adapter excludes `pre`/`code`, uses `trust:false`, `throwOnError:false`, `maxExpand:1000`, `maxSize:50`. | Parse failure leaves exact source and “Math could not be rendered. Formula source is shown.” Asset failure has one lesson-level “Math unavailable. Formula source is shown.” No CDN fallback. Raw TeX is readable without JS; wide formula scrolls locally. **Accept:** unplugged packaged page, inline/display/wide/malformed/code-fence cases, MathML/fallback and zero scoring/evidence delta. |
| **Runnable code example** | Explore code; `ready → running → completed / timed-out / truncated / request-error`, independently per block; learner edits then presses **Run example**. | Keep edits and previous bounded output. One block’s button changes to **Running example…**; concise status is persistent; stdout/stderr are separately labelled non-live `<pre>` regions. Run produces observation only. | Model has no role. Daemon validates stored profile, stable block id, language, settings, LAN policy and source-size limit, then calls Phase 5 `run_source()` exactly once. No `score_response`, hint transition, cursor update, or evidence write. | Refused/static states retain escaped source and omit dead button. Focus stays on Run; Tab/Shift+Tab edit; Escape then Tab exits editor. Status uses polite live region, never raw output. **Accept:** all state copy, zero session/evidence delta, one-runner proof, independent blocks, 320px/200%, keyboard-only flow. |
| **Capability/media unavailable** | Continue the lesson when profile, daemon, language, asset, or network capability is absent. | Keep source/readable semantic content and a durable adjacent notice. The common assessment flow remains available when its normal requirements are met. | Model cannot enable a capability. Runtime/daemon validates capabilities server-side; browser attributes are advisory only. | Notices are text plus token, not a toast or color-only. **Accept:** unknown-profile, disabled-language, static, LAN, missing/corrupt asset, and provider-failure fixtures preserve reading order and do not leak answer material. |
| **Fourth subject** | Add/select a configured subject and complete the common loop. | Same shell, components, statuses, evidence shape and guided sequence; only configured medium/allowed types/verifier vary. | No model role. Settings schema/profile loader validates configuration; source guard rejects subject-name dispatch in production surfaces. | Malformed profile fails closed before a session; the UI never needs a fourth template. **Accept:** temporary config entry completes shared driver without application-code edit. |

## Subject-medium contracts

### EMT prose and tables

- Use ordinary shared headings, paragraphs, ordered/unordered lists, links, and native table output; no medical vocabulary branches, cards, icons, or secondary renderer.
- Each table is inside `.lesson-table-scroll` with `overflow-x:auto`, `max-width:100%`, visible focus, and an accessible name from a caption or nearest heading. Header cells use `scope="col"`; genuine row headers use `scope="row"`.
- Keep source and document order. Cells wrap; values never elide, flatten, or become images. The next document element remains reachable after the wrapper.

### Math

- Published syntax: `$...$` inline and `$$...$$` display. Match display delimiters first. Do not add alternate delimiters in this phase.
- Semantic raw source renders first. A stored Math-capable profile may load only locally served approved KaTeX CSS, core, auto-render script, and matched fonts. Target only `#lesson-content`; ignore `pre` and `code`.
- A display wrapper owns formula overflow. The lesson does not blank while loading. One malformed formula leaves other lesson content and successful formulas intact.
- KaTeX is a vendored browser asset, not an npm/runtime dependency. Its immutable 09-03 approval and 09-04 closed allowlist are prerequisites.

### CS runnable prose

- Every fence gets a stable sequential `data-code-block` id without reparsing its source. A valid daemon-backed profile yields: language label, **Example code** label, visible textarea label, editable Phase 5-styled source, **Run example**, keyboard help, persistent status, and labelled `stdout`/`stderr` outputs.
- `Tab` inserts indentation, `Shift+Tab` dedents current line, and `Escape` arms the next `Tab` to leave the editor. The Run button follows the source in DOM/tab order and retains native Enter/Space behavior.
- Static/no-daemon, disabled-language, and LAN-refused blocks retain escaped source and do not render an enabled/deceptive control. Multiple blocks retain independent source/status/output/request state.

## State machines and exact copy

### Lesson-run state machine

```text
ready --Run--> running --response--> completed
                     ├--timeout--> timed_out
                     ├--capped output--> truncated (may also include completed/exit metadata)
                     └--transport/server error--> request_error
ready --policy/static--> unavailable
all terminal states --edit + Run--> running
```

Only the affected block transitions. `running` disables only its Run button; source and previous output remain. No state transition in this machine reaches assessment/evidence state.

| State | Visible/status copy | Recovery |
|---|---|---|
| Ready | **Run example**; empty status | Edit source and run. |
| Running | **Running example…** | Source and earlier output remain; avoid duplicate requests. |
| Completed | **Run finished (exit code {code}).** | Read labelled output or edit/run again. |
| Timed out | **Run stopped after the configured timeout.** | Edits and partial output remain. |
| Truncated | **Output was truncated at the configured limit.** | Available prefix remains labelled. |
| Request error | **Couldn’t run this example. Your edits are still here. Try again.** | Restore Run and retain source/output. |
| Disabled language | **Run unavailable: {language} is not enabled for this lesson.** | Read source; no Run button. |
| Static/no daemon | **Run this example in the local app. The source remains available here.** | Open local app; no Run button. |
| LAN refusal | **Run unavailable from this network view.** | Read source; use allowed local context. |

Math asset failure copy is **Math unavailable. Formula source is shown.** Math parse failure copy is **Math could not be rendered. Formula source is shown.** These are persistent adjacent statuses, not dismissible toasts. Do not use “correct,” “incorrect,” “passed,” “failed,” “score,” or “verdict” for Run output.

### Copy and error grammar

| Situation | Required message behavior |
|---|---|
| Unsupported profile capability | Name the unavailable capability, preserve source, and state what remains available. Do not invent profile data or path details. |
| Mixed subjects | Explain that an explicit profile is required before starting; do not create a session or evidence. |
| Provider/model failure | “Teaching assistance is unavailable. Continue with the lesson or use the available hint.” Only show this if a model-backed affordance exists; authored content continues. |
| No runnable blocks | Render no empty runner panel. |
| Empty stdout/stderr | Keep their labels and say “No output.”; this is neutral observation, not success/failure. |
| No destructive action | None in scope; no confirmation dialog is introduced. |

## Responsive and accessibility contract

- Native HTML first. ARIA supplements only names/statuses native elements cannot provide. Placeholder, color, hover, title, and an icon are never the sole label/state signal.
- `role="status"` / `aria-live="polite"` contains only concise run summaries. Request errors may announce once with `role="alert"`; stdout/stderr are never live.
- KaTeX success exposes MathML. Failure exposes raw TeX and exact explanatory copy. Do not use a canvas/image as the only formula representation.
- Use visible focus in light, dark, high-contrast, and reduced-motion modes. Animation is unnecessary; if added, it is opacity/border-only and removed under `prefers-reduced-motion`.
- Test keyboard-only behavior at 320 CSS px and 200% zoom: enter/focus/scroll table, navigate headers/cells, leave table, edit code, escape editor, run, hear summary, navigate outputs, reach assessment. No page-level horizontal scroll or focus loss is permitted.
- Unsupported media, math source, code source, and all capability notices remain in ordinary reading order with JavaScript disabled or failed enhancement.

## Evidence, deterministic-v-model, and integrity rules

| Concern | Deterministic owner | Model/browser role | Prohibited result |
|---|---|---|---|
| Profile and capability | `subjects`/session/daemon validation | Client sends profile id only; model has none | Client capability object, UI subject dispatch, or registry re-resolution on resume. |
| Lesson structure | Phase 3 parser | Browser enhances emitted nodes | Subject parser fork, code reparse, deleted escaped source. |
| Assessment/hints | Phase 6 transition + runtime scorer | Model output is tier-gated content only | Media click/Run decides correctness, tier, cursor, or answer disclosure. |
| Code execution | Phase 5 runner/refusal policy | Browser shows observation | Second executor, client-side authorization, unbounded process/output. |
| Evidence | Existing append-only writer | Browser displays state | Run/Math/table/media event written as response/hint/correctness evidence. |
| Offline assets | 09-03 approval + 09-04 closed local map | Browser uses approved local resources | CDN, external URL, path traversal, network fallback, runtime package install. |

Integrity acceptance: compare before/after session cursor, teaching state, hint tier, response count, and evidence bytes for a Run-only interaction; all are unchanged. Reject server requests with unknown session/block/language, overlarge source, authority-shaped fields, or profile/capability/verifier/path fields. Capability/refusal payloads disclose a named reason, never absolute bank paths or hidden key/rationale material.

## UI considerations

Applicable state considerations resolved: 15 covered, 3 backstops, 0 unresolved.

| Category | Element(s) | Status | Resolution / verification |
|---|---|---|---|
| populated | EMT prose/table | covered | Shared semantic source order is the normal state; no template selection. |
| overflow | EMT table | covered | Named focusable wrapper owns horizontal scroll; cells wrap and viewport stays fixed. |
| long-text | EMT prose/table | BACKSTOP | Hold out long headers, URL-like values and prose at 320px/200%. |
| loading | Math | covered | Raw source remains readable during enhancement; no blank loading state. |
| error / partial | Math | covered | Parse/asset failure retains source; one bad formula does not remove surrounding/successful lesson content. |
| overflow | Display math | BACKSTOP | Hold out a deliberately wide expression; verify contained keyboard-accessible scroll. |
| empty / populated | Code source/output | covered | Empty output remains labelled “No output.”; editable source is an ordinary input. |
| loading | Runnable code | covered | Only requested block disables and announces running; previous state persists. |
| error / partial | Runnable code | covered | Request error, timeout, truncation and nonzero exit retain source/available bounded output. |
| zero-one-many | Runnable blocks | covered | Zero produces no panel; one/many retain stable independent ids and states. |
| overflow / long-text | Source/output | BACKSTOP | Hold out 500 lines, long line, and max output; verify internal scroll, labels, gutter, no excessive announcement. |
| unavailable | Math/code/profile | covered | Distinct local-asset/language/static/LAN/provider notices retain source and recovery. |
| long-text | Capability/error notices | covered | Wrap without truncation and preserve recovery action at narrow/zoomed view. |
| error | Guided-loop media | covered | Media failure leaves context → action → hint → retry → explanation readable and runtime-owned. |

## Acceptance and test strategy

### Required automated evidence

| Surface | Command(s) | Contract evidence |
|---|---|---|
| Shared profile/EMT loop | `python tests/subject_loop_roundtrip.py`; `python tests/lesson_roundtrip.py`; `python tests/hint_roundtrip.py` | Stored profile, resume drift, unknown/mixed/disallowed behavior, semantic table hooks, shared wrong/hint/retry/evidence trace, fourth-profile matrix. |
| Offline Math | `python tests/math_offline_roundtrip.py`; `python tests/lesson_roundtrip.py`; `python tests/packaging_roundtrip.py` | Local-only resource graph, approved package parity, ordered delimiters, code-fence immunity, safe options, MathML/source fallback, no scorer/evidence path. |
| Runnable code | `python tests/lesson_code_roundtrip.py`; `python tests/check_roundtrip.py`; `python tests/scoring_roundtrip.py`; `python tests/daemon_roundtrip.py` | One runner, server-side validation, exact state/copy/DOM hooks, independent blocks, zero cursor/hint/evidence delta. |
| Phase boundary | Focused Phase 9 command in `09-VALIDATION.md`, then full `tests/*.py` suite | All media and subject cases retain one transition/evidence shape and no regression of upstream contracts. |

### Ten mandatory scenario outcomes

1. **EMT differential table:** read prose and wide differential table at 320px/200%; keyboard focus/scroll region, headers/cells and following content remain usable; no EMT renderer branch.
2. **Math intuition:** offline packaged Math lesson shows inline/display formulas and MathML; source remains readable before/without enhancement; no score/evidence changes.
3. **Math error and code immunity:** malformed TeX uses exact fallback; dollar syntax inside code fence is unchanged; no network request or page overflow.
4. **CS prediction-before-run:** context asks for a predicted observation before **Run example**; Run output is neutral observation and cannot advance the assessed flow.
5. **CS bounded states:** timeout, truncation, nonzero exit, request error, disabled language, static and LAN refusal retain edits/source/output as applicable and exact recovery text.
6. **Bounded hints:** wrong assessed response provides only the Phase 6 allowed targeted hint; keyboard/SR traversal of media/status never reveals the key or hidden higher tier.
7. **Keyboard/SR no leakage:** table, math fallback, editor exit, run status and outputs are navigable in order; raw output is not announced; no hidden answer/rationale enters labels, status, or DOM source.
8. **Provider failure:** optional model assistance fails visibly but calmly; authored lesson and allowed deterministic hint/retry loop continue without a false completion claim.
9. **Profile integrity/resume:** current registry mutation does not alter resumed profile behavior; unknown/mixed/disallowed cases fail or degrade before evidence, with no path disclosure.
10. **Fourth subject:** temporary settings-only profile completes the common guided loop using the same driver, shell, state terms, and evidence shape; source guard finds no production subject-name dispatch.

### Manual BACKSTOP matrix

- Open the packaged artifact with networking disabled; inspect inline, display, wide, malformed and code-fence Math in light/dark, 320px/200%, reduced motion, and high contrast.
- With Narrator/NVDA (or equivalent), navigate an EMT table and verify named wrapper, header association, cell order and ability to continue after it.
- Keyboard-only edit/Run/Escape a lesson block; verify focus remains on Run, the concise status is announced once, outputs are available but not announced, edits survive each terminal state, and each block remains independent.
- Complete the guided sequence once for EMT, Math, CS and fourth profile. Confirm that subject media remains subordinate and neither predicts/scorers nor media controls replace the common assessment action.

## Registry safety

| Registry / asset | Blocks used | Safety gate evidence |
|---|---|---|
| shadcn official | none | Not applicable: non-React stdlib project, no `components.json`. |
| Third-party UI registry | none | Not applicable: no component/package install is allowed. |
| Vendored KaTeX browser asset | Approved immutable distribution only | 09-03 human ownership/license/checksum/inventory gate; 09-04 validates approved bytes, local fonts, package parity and closed allowlist. |

## Unresolved and do not build

No UI decision required for Phase 9 remains unresolved. The following are expressly out of scope:

- Subject dashboards, subject-specific templates, parser/scorer/runner/evidence forks, or a fourth surface.
- CDN/network fallbacks, external analytics/telemetry, npm install/build steps, a custom TeX parser, image/screenshot tables, or client-side capability authorization.
- Model chat as authority, model-selected hint tier, media-run correctness records, automatic completion/progress claims from code output, or any new gamification.
- Additional language runners, subject-specific authoring, scheduling/pacing (Phase 10), or destructive profile-management UI.

## Checker handoff

- [x] Copywriting is exact for Run, Math, unavailable and recovery states; no exploration copy claims assessment authority.
- [x] Visual/interaction contract defines one shell, source order, desktop/tablet/narrow layouts, components, states, and responsive overflow.
- [x] Color, typography and spacing consume Phase 4 tokens with no new palette or library.
- [x] Accessibility, offline degradation, integrity, deterministic-v-model boundary, and ten scenario acceptance evidence are explicit.
- [x] Registry safety records the vendor gate; no third-party component registry is introduced.

**Approval:** approved by `gsd-ui-checker` on 2026-08-08 (6/6 dimensions; visual focal-priority recommendation resolved).
