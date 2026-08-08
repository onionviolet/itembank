# Phase 4: Surface Redesign & Theming - Research

**Researched:** 2026-08-08  
**Domain:** Local-first vanilla HTML/CSS/JavaScript surfaces, accessible theming, and optimistic-concurrency editing  
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

### Question-screen hierarchy

- **D-01:** Replace the five chrome bands with one sticky, compact context line containing only orientation data needed while answering: bank/lesson context, objective, progress, and session mode. Secondary metadata belongs behind an accessible details disclosure, not in another persistent band.
- **D-02:** Make the stem the dominant element, keep the response control immediately adjacent, and reserve feedback space so submitting does not cause large layout shifts. Desktop and narrow/mobile widths must use the same information order.
- **D-03:** Preserve keyboard and screen-reader operation as a first-class contract: visible focus, semantic headings/status regions, no meaning conveyed by color alone, and reduced-motion support.

### Accent and OS theming

- **D-04:** Keep `surfaces/theme.py` as the single palette source. System light/dark mode remains automatic by default; the chosen accent is global to the local installation and shared by every surface.
- **D-05:** Use the native OS color picker through the existing Python/launcher boundary where supported, with an accessible browser fallback when native selection is unavailable. Persist the source accent, then deterministically derive light/dark accent tokens and soft variants.
- **D-06:** Contrast correction may adjust the rendered token while preserving the learner's source choice. Show the adjusted preview before save and explain the accessibility adjustment. Correct/incorrect/warning colors remain semantic, color-blind-safe, and independent of the custom accent.
- **D-07:** Include reset-to-system/default and live preview. Advanced manual light/dark token overrides may be retained only if they do not weaken contrast enforcement or complicate the default flow.

### In-page day editing

- **D-08:** Use an explicit edit mode with a structured row/cell editor matching the existing day-plan table, not a raw Markdown editor. Preserve unknown Markdown and surrounding prose byte-for-byte outside the edited row/cells.
- **D-09:** Save with optimistic concurrency against a strong representation of the bytes originally loaded (content hash, optionally paired with file metadata). The server re-reads immediately before replace; a mismatch never auto-overwrites.
- **D-10:** On conflict, show the learner's draft and the newly read file side by side with copy/download and reload/reapply actions. A force-overwrite action may exist only behind an explicit second confirmation; the normal path is reload and reapply.
- **D-11:** Writes use the project's atomic replace pattern and return the new revision token. Validation errors remain in the editor with the draft intact. Navigation away with unsaved changes warns.

### Study explanations

- **D-12:** After reveal, organize explanation content progressively: answer and concise why first; per-option rationales beside their options; second-best, discriminator/trap, and notes in labeled expandable sections. Nothing currently present in the runtime explanation payload is silently discarded.
- **D-13:** Default expansion should follow relevance: the chosen option and correct option open; other option rationales remain available but collapsed. Keyboard and screen-reader users receive the same information and state.
- **D-14:** Quiz and study share explanation presentation primitives/tokens where practical, but keep their different learning intent: quiz feedback is response-driven; study permits deliberate reveal and review.

### the agent's Discretion

- Exact spacing, typography scale, breakpoints, iconography, transition timing, native picker implementation, conflict-diff presentation, and naming of disclosure controls.
- The planner may preserve multiple reversible presentation variants when this improves future optionality, but must select one polished default and verify it end to end.

### Deferred Ideas (OUT OF SCOPE)

None - discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|---|---|---|
| SURF-02 | The browser page is a client of the same JSON API an agent uses; it holds no key and implements no scoring | Keep quiz verdicts in `quiz.record_answer()` and the daemon; add API-shaped browser state only where needed. |
| SURF-05 | The question surface shows one sticky context line rather than five bands of chrome above the stem | Replace header/progress/tally treatment with one semantic sticky context component and an accessible secondary disclosure. |
| SURF-06 | `study` renders the per-option rationale, second-best, and notes it currently discards | Extend the narrow `study_item()` payload and render shared explanation primitives. |
| SURF-07 | The whole tool uses one palette; the `day` page stops being a third stylesheet in literal hex | Move day styles onto `THEME_CSS` custom properties and one shared surface stylesheet/token vocabulary. |
| SURF-08 | The accent colour is set from the OS colour picker with light and dark pairs computed from it, and correct/incorrect stay contrast-checked and colour-blind safe | Store source accent in validated settings; derive checked rendering tokens server-side or in the shared palette helper. |
| SURF-09 | `day` supports full in-page markdown editing with an optimistic-concurrency guard, so an edit cannot silently overwrite one made in Obsidian | Introduce a revision-bearing document read/save seam that narrowly patches only editable table cells and atomically replaces after a fresh-byte comparison. |

Requirement text is verbatim from `.planning/REQUIREMENTS.md:117-124`.
</phase_requirements>

## Summary

This is a surface-layer phase. It should change rendering, browser interaction, settings, and the daemon's narrow mutation routes, while leaving parsing, scoring, evidence, and answer-key boundaries in their existing owners. The quiz route already renders with `serve=True`, and its POST delegates scoring and persistence to `quiz.record_answer()`; preserve that route shape rather than teaching browser JavaScript to calculate a verdict. [VERIFIED: surfaces/daemon.py:473-542]

The recommended implementation is one shared visual primitive layer inside `surfaces/theme.py` plus small presentation helpers, a versioned theme-settings object, and a dedicated day-plan document adapter. The adapter must retain the initially-read raw bytes and editable-cell locations, validate a submitted cell model, re-read and compare raw bytes immediately before writing, then use the existing temp-file-plus-`os.replace` pattern. This is the only approach that satisfies D-08 through D-11 without treating human Markdown as an application-owned serialization format. [VERIFIED: surfaces/day.py:832-954]

The project remains stdlib-only. Do not introduce a color, accessibility, editor, diff, or CSS framework; the browser already receives embedded HTML/CSS/JS templates and the installed Python runtime includes Tk 8.6 for a native-picker spike. [VERIFIED: environment probe 2026-08-08]

**Primary recommendation:** Extend `surfaces/theme.py` into the one computed-token source, use a native-picker seam with labeled `<input type="color">` fallback, and implement day edits as revision-checked narrow byte patches through a new day document helper—not a Markdown rewriter. [CITED: https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/input/color]

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|---|---|---|---|
| Palette token derivation and settings persistence | API / Backend | Browser / Client | Python owns validated local configuration and serves one CSS token block; client only previews it. [VERIFIED: surfaces/settings.py:87-128] |
| Native-picker launch and browser fallback | Frontend Server (SSR) | Browser / Client | The launcher boundary can invoke a host picker; the page provides the standards-based fallback control. [VERIFIED: surfaces/launcher.py:1-94] [CITED: https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/input/color] |
| Quiz hierarchy and response interaction | Browser / Client | API / Backend | The browser renders input and feedback; server owns response scoring and explanation payload. [VERIFIED: surfaces/daemon.py:488-542] |
| Study progressive explanation display | Browser / Client | API / Backend | The study page deliberately reveals/reviews learning content, using a server-built safe payload. [VERIFIED: surfaces/study.py:9-13] |
| Day edit validation, revision comparison, and atomic replacement | API / Backend | Browser / Client | A client draft is not authoritative; the server must compare current disk bytes and own file replacement. [VERIFIED: surfaces/day.py:893-954] |
| Conflict recovery UI | Browser / Client | API / Backend | Client presents draft/current document and recovery actions; server returns conflict data without writing. [ASSUMED] |

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---|---|---|---|
| Python standard library | Python 3.13.5 available | HTTP routes, JSON settings, SHA-256, atomic file replacement, and optional Tk native-picker seam | Required project constraint; existing modules already use stdlib-only patterns. [VERIFIED: environment probe 2026-08-08] |
| Embedded HTML/CSS/vanilla JavaScript | Browser-provided | Rendering, color-input fallback, previews, disclosure controls, and editor state | Existing surface implementation convention; avoids a build/install step. [VERIFIED: surfaces/quiz_page.py:1-374] |

### Supporting

| Library | Version | Purpose | When to Use |
|---|---|---|---|
| `tkinter` | Tk 8.6 available | Spike a host-native color selection dialog behind the launcher/Python seam | Use only when a display is available; failure must return control to the browser fallback. [VERIFIED: environment probe 2026-08-08] |
| `<input type="color">` | Browser-provided | Accessible fallback color selection and live preview | Use a real associated `<label>` and react to `input` for preview / `change` for confirmation. [CITED: https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/input/color] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|---|---|---|
| Narrow byte patcher | Full Markdown AST/parser rewrite | Rewriter cannot guarantee D-08 byte preservation of unknown prose and Markdown. [VERIFIED: surfaces/day.py:87-111] |
| Native picker + browser fallback | Browser-only custom palette | Violates the selected native-picker behavior and adds unnecessary accessibility surface area. [CITED: https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/input/color] |
| Derived semantic tokens | Applying custom accent to success/failure states | Violates D-06 and makes color-only errors more likely. [CITED: https://www.w3.org/WAI/WCAG22/Understanding/use-of-color] |

**Installation:** None—this phase must add no external package. [VERIFIED: .planning/PROJECT.md]

## Architecture Patterns

### System Architecture Diagram

```text
Learner / browser
  ├─ quiz interaction ─────► POST quiz answer ─► daemon ─► quiz.record_answer()
  │                              │                         └─ runtime scorer + explanation
  │                              └─ returned verdict/explanation ─► shared UI primitives
  ├─ study reveal ─────────► server-built study payload ──────────► shared UI primitives
  ├─ theme settings ───────► picker / color-input fallback ───────► validated local settings
  │                                                                    │
  │                                                                    └─ computed THEME_CSS tokens
  └─ day edit draft ───────► revision + edited cells ─────────────► day document adapter
                                                                        ├─ raw-byte comparison matches ─► atomic replace
                                                                        └─ mismatch ─► conflict payload, no write
```

### Recommended Project Structure

```text
surfaces/
├── theme.py            # palette input, token derivation, contrast enforcement, shared CSS
├── settings.py          # schema-validated persistence only
├── day.py               # day render/state plus document-edit integration point
├── day_document.py      # new: raw-byte snapshot, table-cell patch, revision comparison
├── quiz_page.py         # compact question shell and shared explanation hooks
├── study.py             # full explanation payload and deliberate reveal UI
└── daemon.py            # narrow JSON routes, no scoring or markup duplication
tests/
├── theme_roundtrip.py   # new: derivation, contrast, reset, settings persistence
├── day_edit_roundtrip.py# new: byte preservation, conflict, force confirmation, atomic update
└── daemon_roundtrip.py  # extend: no-key/API path and edit-route checks
```

### Pattern 1: Computed token source

**What:** Accept a source accent, derive each mode's accessible accent and soft surface deterministically, and produce CSS custom properties only from that result. Semantic `ok`, `bad`, and `warn` stay independently selected and never inherit the learner accent. The existing source already defines a light/dark custom-property pair and uses `prefers-color-scheme`. [VERIFIED: surfaces/theme.py:11-22]

**When to use:** Every HTML template must substitute the same computed theme block; do not carry per-surface color literals. The existing quiz and study templates already substitute `__THEME__`, while day carries an independent literal stylesheet. [VERIFIED: surfaces/quiz.py:32-38] [VERIFIED: surfaces/day.py:525-593]

**Implementation sketch:**

```python
# Design skeleton, not copied implementation.
source_accent -> normalize opaque color -> derive mode tokens
for each text/control/focus pairing:
    if contrast(pair) fails: adjust rendered token; preserve source_accent
return css_variables, adjustment_notice
```

### Pattern 2: Presentation consumes server authority

**What:** The served question page posts the answer and paints only the server-issued verdict/explanation. [VERIFIED: surfaces/daemon.py:488-542]

**When to use:** Rework the question hierarchy and explanation primitives without changing browser ownership of scoring. `page_for(..., serve=True)` already sends a non-offline item representation. [VERIFIED: surfaces/quiz.py:17-38]

### Pattern 3: Revision-checked narrow document patch

**What:** At render/edit-open time, read plan bytes, identify only the selected dated table row/cell ranges, and create a SHA-256 revision. On save, validate edited cells, re-read bytes, compare revision, then replace only those byte ranges in descending offset order; write with temp file then `os.replace`. Return a new revision after success. [ASSUMED]

**When to use:** Only for structured day table edits. Keep the existing tick/evidence mutation route separate, because it writes generated daily-log material rather than user-authored plan material. [VERIFIED: surfaces/day.py:893-954]

**Implementation sketch:**

```python
# Design skeleton, not copied implementation.
snapshot = read_plan_bytes_and_editable_cells()
if submitted_revision != snapshot.revision:
    return conflict(draft, snapshot.bytes)
patched = apply_validated_cell_replacements(snapshot.bytes, submitted_cells)
atomic_replace(plan_path, patched)
return success(new_revision_of(patched))
```

### Anti-Patterns to Avoid

- **Client-side verdict logic:** Do not move quiz canonicalization/scoring into the served page; `handle_quiz_answer()` must continue to use `quiz.record_answer()`. [VERIFIED: surfaces/daemon.py:488-542]
- **A third theme stylesheet:** Do not migrate day by copying current literal colors into a new `DAY_CSS`; make it consume shared variables. [VERIFIED: surfaces/day.py:525-593]
- **Whole-file Markdown serialization:** It will reorder or normalize non-table content and violate D-08. [ASSUMED]
- **Last-writer-wins plan saves:** Never write when the current raw-byte revision differs from the rendered revision. [ASSUMED]
- **Silent color adjustment:** Preview and explain adjustments before persistence, per D-06. [CITED: https://www.w3.org/TR/WCAG22/]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---|---|---|---|
| Browser color selection | Custom canvas/color-wheel picker | Native picker seam plus native `<input type="color">` fallback | The browser control can expose platform UI or text input and supports associated labels/events. [CITED: https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/input/color] |
| Settings validation | New theme-specific validator | Existing schema validation, `load_settings()`, and `write_settings()` path | Existing settings code merges defaults and validates known keys before callers consume them. [VERIFIED: surfaces/settings.py:87-128] |
| File replacement | In-place write | Existing temporary file then `os.replace` pattern | Existing day writes use that crash-safe replacement shape. [VERIFIED: surfaces/day.py:948-954] |
| Accessibility semantics | Decorative div/button substitutes | Native `<details>`, `<button>`, `<label>`, headings, and live/status regions | WCAG requires keyboard operation, visible focus, and meaning beyond color. [CITED: https://www.w3.org/TR/WCAG22/] |

**Key insight:** This phase's difficult parts are correctness boundaries, not visual polish: preserve server scoring authority and external Markdown bytes while making the UI simpler. [VERIFIED: surfaces/daemon.py:488-542] [VERIFIED: surfaces/day.py:893-954]

## Common Pitfalls

### Pitfall 1: Updating theme only in static outputs

**What goes wrong:** `THEME_CSS` is inserted when a page is generated, so an already-open daemon page will not reflect a new saved accent without an explicit refresh/reload or a client token update. [VERIFIED: surfaces/quiz.py:32-38]  
**How to avoid:** Make the preview local and immediate, show a saved-state/new-revision result, and reload only after save rather than promising universal live cross-tab propagation. [ASSUMED]

### Pitfall 2: Color becomes the only correctness cue

**What goes wrong:** Correct/incorrect styling can become inaccessible when the visual distinction is solely green/red or a customized accent alters contrast. [CITED: https://www.w3.org/WAI/WCAG22/Understanding/use-of-color]  
**How to avoid:** Keep textual verdicts and option labels, use checked/incorrect classes only as reinforcement, preserve `:focus-visible`, and test every derived token pairing. Existing quiz markup already has text verdicts plus semantic classes. [VERIFIED: surfaces/quiz_page.py:35-50]

### Pitfall 3: Study continues to drop explanation data

**What goes wrong:** The current `study_item()` returns only `why`, `disc`, and `trap`; it drops option rationale, `second`, and `notes`. Quote: `"why": q.get("why", ""), "disc": q.get("disc", ""), "trap": q.get("trap", "")`. [VERIFIED: surfaces/study.py:9-13]  
**How to avoid:** Make `study_item()` derive from `explain_payload()` or an equivalent shared projection so Phase 4 has a single complete explanation source. [ASSUMED]

### Pitfall 4: Day conflict detection protects the wrong thing

**What goes wrong:** The current day state contains parsed data and mutable tick state, not a plan-file revision; its POST writes `daily_log.md`, not the plan. [VERIFIED: surfaces/day.py:832-868] [VERIFIED: surfaces/day.py:893-954]  
**How to avoid:** Treat plan document snapshot/revision and tick/evidence state as separate resources/routes; a day-table save must compare plan bytes immediately before replacing that plan. [ASSUMED]

### Pitfall 5: Unsaved-change dialogs over-prompt or lose drafts

**What goes wrong:** Permanent `beforeunload` listeners are unreliable and can prevent normal browser behavior; a conflict response can otherwise erase the editor's work. [CITED: https://developer.mozilla.org/en-US/docs/Web/API/Window/beforeunload_event.]  
**How to avoid:** Attach unload warning only while dirty, retain the draft locally on validation/conflict error, and offer copy/download plus reload/reapply. [CITED: https://developer.mozilla.org/en-US/docs/Web/API/Window/beforeunload_event.]

### Pitfall 6: Route/CLI contract drift

**What goes wrong:** The daemon maintains an explicit `ROUTES`/`ROUTE_CLI` inventory, and tests assert it; adding an edit route without its CLI counterpart would regress SURF-04 even though this phase's primary scope is SURF-02/05-09. [VERIFIED: surfaces/daemon.py:56-103]  
**How to avoid:** Every new mutation must have a CLI twin or intentionally reuse the existing `day` command; extend the inventory test. [ASSUMED]

## Code Examples

Verified patterns from official sources and the codebase:

### Browser fallback with live preview

```html
<!-- A real associated label is mandatory. [CITED: MDN input docs] -->
<label for="accent-picker">Accent color</label>
<input id="accent-picker" type="color">
```

Use `input` for preview and `change` to enable the explicit save action. [CITED: https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/input/color]

### Atomic replacement seam

```python
# Reuse the existing sequence; do not write the target directly.
write_temporary_file(new_bytes)
replace_target_atomically()
```

The concrete existing sequence is temporary-path write followed by `os.replace(tmp, log_path)`. [VERIFIED: surfaces/day.py:948-954]

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|---|---|---|---|
| Separate literal palettes per surface | One CSS custom-property palette substituted by templates | Existing Phase 2 foundation | Phase 4 must finish the migration by removing day literals rather than establish a competing token system. [VERIFIED: surfaces/theme.py:1-22] |
| Page submits directly to a one-bank route | Daemon route table with bank-scoped quiz/day routes and API session routes | Phase 2 | Preserve allowlisted identifiers and server-side scoring while redesigning the surface. [VERIFIED: surfaces/daemon.py:43-103] |
| Day screen only ticks work | Phase 4 adds guarded plan-cell editing | Phase 4 scope | Requires a new document/revision seam; existing tick path is not a sufficient save implementation. [VERIFIED: surfaces/day.py:893-954] |

**Deprecated/outdated:** `DAY_CSS` as a literal-color surface is explicitly replaced by shared theme tokens in this phase. [VERIFIED: surfaces/day.py:525-593]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|---|---|---|
| A1 | A raw-byte cell patcher can map and replace parsed day-table cells without changing surrounding Markdown. | Architecture Patterns | Parser edge cases may require a narrowly scoped human decision on supported table syntax. |
| A2 | `study_item()` should consume a shared explanation projection rather than duplicate fields. | Common Pitfalls | A small runtime/presentation boundary may need a different helper shape. |
| A3 | The native-picker seam can use the available Tk runtime and degrade to browser fallback in every packaged target. | Standard Stack | Packaged environments without Tk need the fallback as the primary path. |
| A4 | New day edit route(s) need a CLI equivalent through either a new command or the existing `day` command. | Common Pitfalls | Planner must choose a concrete CLI contract before implementation. |

## Open Questions (RESOLVED)

The uncertainty statements and original recommendations below are preserved as the research record. The added **Binding resolution** lines are the approved plan-time contracts and supersede the uncertainty for Phase 4 execution.

1. **What is the exact persisted `theme` schema shape?**
   - What we know: The existing source-of-truth schema currently defines the exact theme union as `"enum": ["system", "light", "dark"]` and default `"system"`. [VERIFIED: schemas/settings.schema.json:11-16]
   - What's unclear: The additive object/key structure for source accent and derived override provenance.
   - Recommendation: Add a backward-compatible theme object only after a schema/test task defines defaults and migration/merge behavior; do not overload the current string silently. [ASSUMED]
   - **Binding resolution:** Keep the existing top-level `theme` string and its `system|light|dark` enum/default unchanged. Add required top-level `accent: {"source":"#RRGGBB"}` with source default `#0e6e62`; validate after merging schema defaults so older files remain loadable; persist only the normalized source and never derived pairs, ratios, correction notices, or per-mode overrides. Plan 04-03 proves this with `tests/config_roundtrip.py` and `tests/theme_roundtrip.py` before browser consumption.

2. **Which native picker implementation should ship?**
   - What we know: Tk 8.6 imports in the target environment, and `surfaces/launcher.py` already concentrates host-container decisions. [VERIFIED: environment probe 2026-08-08] [VERIFIED: surfaces/launcher.py:1-94]
   - What's unclear: Tk availability in all `.pyz` target installations and whether it opens the desired native dialog on macOS/Linux.
   - Recommendation: Make this a Wave 0 spike with an explicit fallback result; browser `<input type="color">` must independently meet the feature. [CITED: https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/input/color]
   - **Binding resolution:** `itembank theme pick --json --initial COLOR` lazily invokes `tkinter.colorchooser` on its process main thread. The local browser route spawns the current source script or `.pyz` with fixed no-shell argv, validates the structured child result, and never constructs Tk in a threaded HTTP handler. Selection is preview-only until explicit save. Cancel, missing Tk, display/package/spawn failure, or malformed output returns `available:false`, preserves settings/draft, focuses the browser color input, and uses the exact UI copy `System picker is unavailable here. Choose a color below instead.` Plans 04-03/04-04 prove direct picker and source/`.pyz` child/fallback branches in `tests/theme_roundtrip.py` and `tests/daemon_roundtrip.py`.

3. **What table syntax can the cell editor safely edit?**
   - What we know: `parse_plan()` detects pipe rows and splits cells using `line.strip().strip("|").split("|")`. [VERIFIED: surfaces/day.py:65-111]
   - What's unclear: Whether user plan cells contain escaped pipes or multiline table extensions.
   - Recommendation: The byte-patch adapter must either preserve those forms correctly or refuse editing with a clear non-destructive message; test the supported grammar before enabling save. [ASSUMED]
   - **Binding resolution:** Support exactly one unambiguous pipe table with header, delimiter/rule row, and exactly one matching dated row; optional outer pipes, LF/CRLF, leading/trailing padding, unknown columns, surrounding prose/unrelated tables, escaped `\|`, and closed inline-code pipes are preserved. Safely encode an entered literal pipe. Refuse with no write: duplicate matching dates, missing header/rule, ambiguous candidate table, missing column/date row, multiline extensions, HTML tables, colspan/rowspan, unclosed code/escape ambiguity, and newline/control input. Compute the revision from complete raw UTF-8 bytes, patch cell spans in descending order, re-read/compare immediately before same-directory fsync plus `os.replace`, and retain draft/current on conflict. Plans 04-02/04-06 prove every accepted/refused form, byte preservation, and concurrency recovery in `tests/day_edit_roundtrip.py` and `tests/daemon_roundtrip.py`.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|---|---|---|---|---|
| Python | daemon, settings, hashes, file writes | ✓ | 3.13.5 | — [VERIFIED: environment probe 2026-08-08] |
| Tk | native picker spike | ✓ | 8.6 | Browser color input [VERIFIED: environment probe 2026-08-08] |
| Chrome | browser/UI UAT | ✓ via launcher registry discovery | local installed path discovered | ordinary system-browser opening [VERIFIED: environment probe 2026-08-08] |
| External package manager/package | Phase implementation | Not required | — | stdlib-only design [VERIFIED: .planning/PROJECT.md] |

**Missing dependencies with no fallback:** None.  
**Missing dependencies with fallback:** None detected; the original Tk packaging uncertainty is resolved by the main-thread source/`.pyz` child contract plus independent browser color-input fallback recorded under **Open Questions (RESOLVED)**. [PLANNED]

## Validation Architecture

### Test Framework

| Property | Value |
|---|---|
| Framework | Standalone standard-library Python roundtrip scripts | [VERIFIED: .planning/codebase/TESTING.md] |
| Config file | none | [VERIFIED: .planning/codebase/TESTING.md] |
| Quick run command | `python tests/daemon_roundtrip.py` | [VERIFIED: .planning/codebase/TESTING.md] |
| Full suite command | `for t in tests/*.py; do python "$t" || exit 1; done` (GitHub Actions form) | [VERIFIED: .github/workflows/ci.yml] |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|---|---|---|---|---|
| SURF-02 | Served quiz contains no key/scorer and returned verdict is server-issued | integration | `python tests/daemon_roundtrip.py` | ✅ extend existing checks [VERIFIED: tests/daemon_roundtrip.py:255-282] |
| SURF-05 | One sticky context line, DOM order/focus/reduced-motion hooks | template/structural + manual browser | `python tests/surface_roundtrip.py` | ❌ Wave 0 extension |
| SURF-06 | Study data includes option rationale, second-best, notes; expanded/collapsed semantics | unit/template | `python tests/surface_roundtrip.py` | ❌ Wave 0 extension |
| SURF-07 | Quiz/study/day substitute one token block; no day literal hex palette | structural | `python tests/theme_roundtrip.py` | ❌ Wave 0 |
| SURF-08 | Derivation is deterministic, compliant/adjusted preview is explicit, semantic tokens unchanged | unit + manual picker | `python tests/theme_roundtrip.py` | ❌ Wave 0 |
| SURF-09 | Byte preservation, stale revision conflict/no write, successful atomic replacement/new revision | integration | `python tests/day_edit_roundtrip.py` | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** relevant roundtrip script plus `python tests/surface_roundtrip.py`.
- **Per wave merge:** CI-equivalent full suite.
- **Phase gate:** Full suite green plus manual Chrome UAT for color picker, narrow viewport, keyboard/screen-reader semantics, and two-editor conflict recovery.

### Wave 0 Gaps

- [ ] `tests/theme_roundtrip.py` — theme schema compatibility, deterministic derivation, contrast correction disclosure, semantic-state token independence, and reset.
- [ ] `tests/day_edit_roundtrip.py` — raw-byte preservation outside changed cells, stale revision rejection, draft retention response, explicit force confirmation, returned revision, and atomic replacement.
- [ ] Extend `tests/surface_roundtrip.py` / `tests/daemon_roundtrip.py` — study explanation completeness, shared token inclusion, no-key/scorer invariant, and route/CLI inventory.

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---|---|---|
| V2 Authentication | no | Local single-user tool; no account/session authentication change in scope. [VERIFIED: .planning/codebase/INTEGRATIONS.md] |
| V3 Session Management | yes | Do not change runtime session authority; browser page posts to server route and receives server verdict. [VERIFIED: surfaces/daemon.py:488-542] |
| V4 Access Control | yes | Continue startup allowlisted bank/plan stems; never accept a client filesystem path for plan editing. [VERIFIED: surfaces/daemon.py:43-103] |
| V5 Input Validation | yes | Validate theme settings via existing schema; validate structured edited cells before a document patch. [VERIFIED: surfaces/settings.py:87-128] [ASSUMED] |
| V6 Cryptography | yes | Use standard-library SHA-256 only as an integrity revision, not as access control or encryption. [ASSUMED] |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---|---|---|
| Browser sends a hidden-key/verdict claim | Tampering | Ignore client verdicts; calculate via server route and existing scorer. [VERIFIED: surfaces/daemon.py:488-542] |
| Path traversal through plan/bank identifier | Tampering / Information disclosure | Resolve only daemon-scanned stems, not client paths. [VERIFIED: surfaces/daemon.py:43-103] |
| Obsidian edit overwritten by stale browser save | Tampering / Data loss | Raw-byte revision compare immediately before replacement; conflict returns no write. [ASSUMED] |
| Theme/config malformed input | Denial of service | Existing settings schema validation before consumption. [VERIFIED: surfaces/settings.py:87-128] |
| Color-only feedback excludes users | Accessibility / Integrity of feedback | Textual state, semantic roles, contrast checks, and focus visibility. [CITED: https://www.w3.org/TR/WCAG22/] |

## Sources

### Primary (HIGH confidence)

- `surfaces/theme.py:1-22` — current palette ownership and mode tokens.
- `surfaces/daemon.py:43-103,473-556` — route table, no-key served quiz, server-owned response handling, and study route.
- `surfaces/day.py:525-648,832-954` — independent day palette and existing tick persistence seam.
- `surfaces/settings.py:87-128` and `schemas/settings.schema.json:11-16` — validated settings behavior and current theme union.
- `tests/daemon_roundtrip.py:255-282,433-580` and `.github/workflows/ci.yml` — integration and CI validation patterns.

### Secondary (MEDIUM confidence)

- [MDN `<input type="color">`](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/input/color) — native/control fallback behavior, labels, and change events.
- [MDN `beforeunload`](https://developer.mozilla.org/en-US/docs/Web/API/Window/beforeunload_event.) — dirty-state warning lifecycle and state-loss caveats.
- [W3C WCAG 2.2](https://www.w3.org/TR/WCAG22/) — contrast, keyboard, focus, motion, and interaction requirements.
- [W3C Understanding Use of Color](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color) — non-color cues for meaning.

### Tertiary (LOW confidence)

- None.

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH — no external dependency is needed; project patterns and target environment were inspected.
- Architecture: HIGH — the theme, route, scoring, settings, and day persistence source seams were read directly; the raw-byte patch helper is explicitly marked assumed pending Wave 0 validation.
- Pitfalls: HIGH — derived from current omitted study fields, literal day palette, server ownership path, and authoritative accessibility docs.

**Research date:** 2026-08-08  
**Valid until:** 2026-09-07 for codebase findings; recheck browser accessibility docs before implementation if the phase is delayed.
