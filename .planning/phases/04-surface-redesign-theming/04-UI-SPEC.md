---
phase: 04
slug: surface-redesign-theming
status: draft
shadcn_initialized: false
preset: none
created: 2026-08-08
---

# Phase 4 — UI Design Contract

> Canonical visual and interaction contract for Surface Redesign & Theming. This phase remains local-first, low-chrome, stdlib-only, and must not create a second scorer, parser, palette, or Markdown owner.

---

## Design System

| Property | Value |
|---|---|
| Tool | none — embedded HTML/CSS/vanilla JavaScript |
| Preset | not applicable |
| Component library | none; use native HTML controls and elements |
| Icon library | none; use short text labels and Unicode only as redundant decoration |
| Font | system-ui, `-apple-system`, `"Segoe UI"`, Roboto, sans-serif; monospace only for revisions, identifiers, and compact metadata |
| Palette owner | `surfaces/theme.py` is the only color-token producer; every rendered surface receives its generated CSS |

Use native `<button>`, `<input>`, `<label>`, `<fieldset>`, `<legend>`, `<details>/<summary>`, `<table>`, headings, and `role=status`/`aria-live` before custom ARIA. No external CSS, editor, diff, icon, or color package is allowed.

### Surface character

- Teach one thing at a time: quiet page background, one primary card/reading column, restrained borders, and no dashboard-like permanent chrome.
- Transfer proven patterns without borrowing brand identity: Anki-style one-card focus and keyboard honesty; Execute Program-style readable prose-to-practice flow; and calm productivity-tool recovery patterns (clear status, deliberate destructive actions, recoverable drafts). These patterns support the local-first teaching character rather than adding feeds, gamification, or dashboard density.
- The common visual primitives are `.surface`, `.context-line`, `.card`, `.chip`, `.action`, `.status`, `.explanation`, `.state-ok`, `.state-bad`, `.state-warn`, and native disclosure styles. Quiz and study share these primitives; their learning behavior does not merge.
- Browser pages are presentation clients. Quiz receives only public item data and server-issued verdict/explanation; study may deliberately receive the full explanation; day sends only revision plus changed structured cells.

---

## Spacing Scale

| Token | Value | Usage |
|---|---:|---|
| xs | 4px | Inline icon/label gap; status glyph gap |
| sm | 8px | Option-internal gaps; chips; compact metadata |
| md | 16px | Default control groups, card padding on narrow screens |
| lg | 24px | Card padding on wider screens; section gaps |
| xl | 32px | Major surface sections; conflict panes |
| 2xl | 48px | Page-level breaks after a completed task or report section |
| 3xl | 64px | Maximum page-end breathing room |

Exceptions: interactive controls have a minimum 44px target in either dimension; dense table cells may be 36px high only when their adjacent row/action has a 44px target. Sticky context line uses 8px vertical / 16px horizontal padding. Never use negative margins to create hierarchy.

---

## Typography

Exactly four sizes and two weights are used; italic is reserved for authored Markdown, not UI hierarchy.

| Role | Size | Weight | Line Height | Contract |
|---|---:|---:|---:|---|
| Metadata / label | 14px | 400 | 1.4 | Context-line values, chips, table headers, status detail; allow wrap, never truncate meaningfully |
| Body | 16px | 400 | 1.5 | Stem support text, option text, explanations, day tasks, settings help |
| Section heading | 20px | 600 | 1.2 | Page title, study answer heading, report/settings sections, conflict pane title |
| Stem / display | 28px | 600 | 1.2 | Quiz stem only; reduce to 20px at narrow width without changing DOM order |

Use `font-variant-numeric: tabular-nums` for progress and revision tokens. Long objective names wrap at spaces or safe punctuation; identifiers and SHA-256 revisions may horizontally scroll within their own code-like container instead of widening the page.

---

## Color

The 60/30/10 ratio is an allocation of visual attention, not a mandate to paint large blocks of color. Persist the learner's source choice; render only derived, contrast-checked tokens.

| Role | Light token | Dark token | Usage |
|---|---|---|---|
| Dominant (60%) | `--bg #f3f5f4`, `--ink #171d1c` | `--bg #0e1413`, `--ink #e4ebe9` | Page field, reading surface, main text |
| Secondary (30%) | `--card #ffffff`, `--chip #eef2f1`, `--line #dfe5e3` | `--card #161e1d`, `--chip #1d2726`, `--line #26312f` | Cards, sticky-line backing, disclosures, tables, navigation/tabs |
| Accent (10%) | derived `--accent`, `--accent-soft` | derived `--accent`, `--accent-soft` | Listed below only |
| Semantic success | `--ok #1b7a3d`, `--ok-bg #e8f4ec` | `--ok #4fbf74`, `--ok-bg #11291b` | Correct/server-issued success and completed state |
| Semantic error / destructive | `--bad #b4272b`, `--bad-bg #fbebeb` | `--bad #f0666a`, `--bad-bg #2b1416` | Incorrect/server-issued error, validation failure, destructive force action |
| Semantic warning | `--warn #8a5900` (≥4.5:1 on `--bg` and `--card`) | `--warn #e0a23a` | Adjustment notice, unavailable integration, unsaved changes |

Accent is reserved for: primary non-destructive action fill; selected but not graded response control border/background; focus outline; progress fill; active tab; links; current context/section marker; color-input preview; and decorative, non-semantic emphasis. It is never the only cue for correctness, an error, a warning, an unavailable state, or destructive force overwrite.

### Theme persistence and derivation

The persisted schema is additive and exact:

```json
{
  "theme": "system",
  "accent": { "source": "#0e6e62" }
}
```

- Keep the existing `theme` string unchanged: `system | light | dark`, default `system`.
- Add required top-level `accent` object with required opaque six-digit normalized hexadecimal `source`; its schema default is `#0e6e62`. Existing files without `accent` remain valid because settings loading merges schema defaults before validation/writing.
- Persist only `accent.source`; never persist derived light/dark accent, soft variants, contrast ratios, or manual per-mode overrides. This deliberately declines the optional advanced override path in D-07: a single source is reversible and cannot bypass contrast enforcement.
- `derive_theme(source)` normalizes source then deterministically derives each mode's `accent` and `accent-soft`; adjustment preserves hue/saturation where possible and chooses the nearest lightness meeting 4.5:1 for text/control pairings and 3:1 for focus/border pairings. `theme=system` emits both mode sets under `prefers-color-scheme`; forced modes emit the chosen set.
- `--ok`, `--bad`, and `--warn` are fixed per mode, independently contrast-tested, and never derived from the custom accent. Every semantic state pairs color with a textual label plus icon/border/pattern state; verdicts must be distinguishable under red/green color-vision deficiency.

### Accent-picker behavior

- Settings exposes a labeled browser `<input type="color">`, current source text, live side-by-side light/dark sample cards, contrast ratios, and an adjustment notice before save.
- `input` previews locally without writing; `change` marks the draft ready; **Save accent** persists the source and reports that other open pages change on refresh. **Reset to default** restores `#0e6e62` after confirmation only if a custom source is currently saved.
- **Choose with system picker** calls a lazy `tkinter.colorchooser` seam in packaged/local environments. It must create no Tk dependency at daemon startup; cancel, missing Tk, display failure, or package limitation returns `available:false`, preserves the draft/settings bytes, focuses the browser color input, and says: “System picker is unavailable here. Choose a color below instead.”
- Pick/save/reset are loopback-only same-origin JSON operations; a LAN client may preview but cannot open a host picker or mutate host settings. Requests accept action and source only—never CSS, derived tokens, a path, or a config object.

---

## Layout, Components, and Interaction

### Shared shell and responsive rules

| Area | Desktop (≥ 768px) | Narrow (< 768px) | Non-negotiable behavior |
|---|---|---|---|
| Main reading column | 720px max for study/settings/day, 800px max for quiz; centered | Full width with 16px gutters | Same DOM/information order; no horizontal page scroll |
| Sticky context line | Single compact flex row; wraps within line | Two visual rows inside the one line | Remains one sticky region; `top:0`, opaque card/background, visible bottom border |
| Quiz response controls | Full-width vertically stacked controls | Same stack | Stem → response → reserved feedback order never changes |
| Day editor | Semantic table/form with labels in header | Labels precede controls; fields stack | Table values remain structured cells, never raw Markdown textarea |
| Conflict recovery | Two equal panes side by side | Draft pane then current pane | Pane labels, revisions, copy/download/reload/reapply precede force action |
| Settings preview | Light and dark cards side by side | Cards stack light then dark | Each card names its mode and shows normal, focus, selected, success, error, warning samples |
| Reports / empty pages | Section cards in one reading column | Same | Metrics wrap, labels stay attached to values, no data tables force viewport width |

At `prefers-reduced-motion: reduce`, remove transform/flip and progress transitions; state changes are immediate. Otherwise motion may be opacity/background/border transitions ≤150ms; do not animate layout, feedback height, or conflict panes.

### Quiz / question hierarchy (SURF-02, SURF-05)

1. The sticky `.context-line` contains exactly bank or lesson context, objective, progress (`item N of M`), and session mode. It is a semantic `nav` or labeled region, not a second heading. Secondary metadata lives in one `<details><summary>Session details</summary>…</details>` below the line.
2. The active stem is the page’s single, dominant 28px `h1`; bank/session identity remains in the context line, not a competing heading. Keep response controls immediately after it; no intervening dashboard band, score tally, or repeated title.
3. Use native radio/checkbox inputs in a fieldset for choices, native select/inputs for other established item schemas, with labels covering the full control row. Selection is accent-marked but has an explicit selected state and programmatic checked state.
4. Reserve a feedback/status region directly below the response control (`min-height: 96px` desktop, `120px` narrow) before submit. Submitting disables the action and announces “Checking answer…”; server response replaces that state without moving the stem or controls.
5. Server-issued feedback begins with text “Correct”, “Incorrect”, or mode-appropriate neutral result; it may show semantic color, icon, and border as reinforcement. It renders only from the response payload, never browser scoring, a hidden key, or inferred client verdict.
6. Empty/completed state replaces the response area with the documented completion copy and a **View report** action. API/session unavailable state retains the current public item, disables submit, and offers **Try again** without converting to an offline-scored page.

### Study explanation presentation (SURF-06)

- Before reveal, display stem and, for choice items, local-recall option controls marked “Your recall choice — not graded.” The choice neither calls a scorer nor receives a correctness verdict.
- **Reveal explanation** is an explicit native button. After reveal: answer first; concise why second; then every option once with its rationale adjacent in a native `<details>` element. Correct and learner-selected rationales begin open; all other rationales begin closed but keyboard reachable.
- Place **Second-best answer**, **Discriminator**, **Common trap**, and **Notes** below option rationales as individually labeled `<details>` blocks. Render all non-empty fields from `runtime.explain_payload()`; type-specific answer/model/rubric content retains its canonical order. Do not fabricate empty sections.
- Flashcards, Learn, previous/next, **Got it**, and **Missed** are native buttons. A live status region announces card number and reveal/queue updates. Their local state must never use “correct”/“incorrect” copy unless it is a runtime response result.

### Lesson, reports, and settings consistency

- The Phase 3 lesson reader uses the same shell, typography, context-line/chip/disclosure primitives, generated theme block, 720px reading measure, and responsive gutter rules. Lesson headings remain document hierarchy rather than being converted into dashboard cards; links to tested items use the accent primary action style.
- Reports use 20px section headings, plain-language metric labels, tabular numerals, evidence/provenance text below claims, and `--ok/--bad/--warn` only alongside textual labels. Empty reports retain the shared empty card rather than an empty chart frame.
- Settings is a quiet form with one visible theme section. Advanced implementation data (ratios, rendered values, adjustment reason) is in an open-by-request `<details>` labeled **Accessibility details**; it is not a persistent control panel.

### Day cockpit and structured editing (SURF-09)

- The cockpit preserves the existing daily orientation: date, floor/status, lane cards, streak/history, task text, and evidence badges. Its colors, buttons, forms, chips, focus treatment, and dark mode use shared tokens only; no literal local palette remains.
- **Edit plan** enters an explicit edit mode for the currently displayed dated row. Render a semantic form/table using actual parsed column labels; one labeled single-line control per editable cell. Do not expose the full Markdown document, a raw Markdown textarea, a file path input, or an arbitrary new column control.
- Display the loaded revision as “Plan version `abcdef12…`” in a copyable code element. Normal **Save changes** posts revision plus changed cells. It stays disabled until the form is dirty; the draft stays visible on invalid, unsupported, network-error, or conflict result.
- Validation errors appear next to their fields and in a persistent `role=status` summary: “Plan not saved. Fix the highlighted cells and try again.” Focus the summary after submit, then allow field navigation.
- A conflict is a warning/error state, never a passive toast: label it “Plan changed outside itembank — nothing was overwritten.” Show learner draft and fresh current plan in separately labeled regions with old/current revisions. Offer **Copy draft**, **Download draft**, **Copy current**, **Reload current**, and **Reapply draft**. Reload replaces the clean baseline but retains the old draft until explicitly discarded; reapply overlays the draft on the fresh baseline without saving.
- **Force overwrite** is absent before a conflict. After one conflict, it is visually destructive, follows recovery options, requires a checked statement “I understand this replaces these edited cells using the latest plan version” and a separate **Force overwrite** button. The request needs the server’s one-use, draft/revision-bound token; another conflict removes the old token and returns to recovery. A successful force still patches only requested cells against a fresh revision.
- Add `beforeunload` only while current field values differ from the latest clean baseline. Remove it after saved, reload-current, or explicit discard. Never rely on it for draft recovery.

### Supported day-table grammar

The editable subset is intentionally smaller than Markdown rendering:

| Form | Result |
|---|---|
| One unambiguous pipe table with header, delimiter/rule row, and exactly one matching dated data row | Supported |
| Header and target row with optional outer `|`, LF or CRLF, leading/trailing cell padding, unknown columns, surrounding prose, other tables | Supported and preserved byte-for-byte outside changed cell content spans |
| Escaped pipe `\\|` or inline-code pipe inside a target cell | Supported; scanner must not split it; an entered literal pipe is encoded safely in the changed cell |
| Duplicate matching date, missing delimiter/header, ambiguous matching table, missing column, or missing dated row | `invalid`; no write |
| Multiline cell/table extension, HTML table, colspan/rowspan, unclosed code span/escape that prevents an unambiguous span, newline/control character in edit input | `unsupported` or `invalid`; no write |

The adapter reads raw UTF-8 bytes, tracks editable content spans, applies replacements descending by byte offset, flushes/fsyncs a same-directory temporary file, then `os.replace`s only after a fresh SHA-256 byte comparison. It does not serialize Markdown. Every unsupported/invalid result retains submitted draft text verbatim and names a recovery path: “This table format is read-only here. Edit it in your Markdown editor, then reload.”

---

## Component / State Matrix

| Surface / component | Ready / populated | Empty / unavailable | Loading / in-flight | Error / conflict / partial |
|---|---|---|---|---|
| Served quiz | Sticky line, stem, response, reserved feedback | “This session has no question ready.” + **View report** | Submit disabled; “Checking answer…” in reserved region | “Couldn’t check that answer. Your selection is still here.” + **Try again**; no client verdict |
| Study | Stem, deliberate reveal, progressive explanations | “No study cards in this bank yet.” + **Choose another bank** | Card-change status update, no blocking spinner | “This card could not be shown. Move to the next card or reload.”; preserve queue where possible |
| Lesson reader | Document reading column, heading hierarchy, linked items | “This bank has no lesson yet.” + **Start studying questions** | Native document navigation only | Missing linked item shows non-color warning beside link; lesson remains readable |
| Day cockpit | Lane cards, status, edit button | Missing dated row: standing lanes + “No plan row for this date.” | Tick/save uses concise live status | Anki/notes unavailable are warnings with unaffected plan; edit invalid/unsupported retains form; conflict is side-by-side recovery |
| Settings | Source picker, previews, Save/Reset | No custom accent means default source shown | Live local preview; picker announces “Opening system picker…” | Picker unavailable retains browser fallback; save failure retains source draft and retry |
| Report / index | Evidence-backed metrics and links | “No recorded attempts yet.” + **Start a session** | Navigation/link busy state only | “Report could not be loaded. Try again.”; do not render invented zeroes |

---

## Copywriting Contract

| Element | Copy |
|---|---|
| Quiz primary CTA | **Submit answer** |
| Study primary CTA | **Reveal explanation** |
| Day primary CTA | **Save changes** |
| Theme primary CTA | **Save accent** |
| Empty state heading | **Nothing to show yet** |
| Empty state body | “Start a session or choose another bank to create something to review here.” |
| Quiz/API error | “Couldn’t check that answer. Your selection is still here. Try again.” |
| General page error | “This page could not be loaded. Try again; your local files were not changed.” |
| Accent adjustment | “Adjusted for readable contrast. Your chosen color is saved; this preview shows the accessible rendered color.” |
| Picker fallback | “System picker is unavailable here. Choose a color below instead.” |
| Unsupported day table | “This table format is read-only here. Edit it in your Markdown editor, then reload.” |
| Day validation | “Plan not saved. Fix the highlighted cells and try again.” |
| Day conflict | “Plan changed outside itembank — nothing was overwritten.” |
| Force confirmation | Checkbox: “I understand this replaces these edited cells using the latest plan version.” Button: **Force overwrite** |
| Reset confirmation | “Reset accent to the app default? Your current custom source color will be replaced.” |

Never say “saved” before the server returns `saved` and the new revision. Never call a study-local choice correct/incorrect. Never disclose a quiz key or explanation beyond the server’s returned reveal policy.

---

## Accessibility and Keyboard Contract

- All actionable controls are reachable in logical visual order with Tab/Shift+Tab, activate with Enter/Space as native semantics provide, and show a 2px accent focus ring with 2px offset meeting 3:1 contrast in both modes. Focus is never removed without moving it to the resulting status/heading/control.
- Every page has one `h1`; on quiz that `h1` is the active stem, while other surfaces use their page title. Sections descend without skipped heading levels. Sticky context line has an accessible label; decorative icons are `aria-hidden`.
- Status/feedback is a persistent `role=status`/`aria-live=polite` container. Async errors use `role=alert` only for failure requiring immediate attention; do not announce every keystroke or preview update.
- Native `<details>` reports expanded/collapsed state to assistive technology. `summary` labels name the content, e.g. “Second-best answer” rather than “More.” Choice rationales retain correct/selected labels plus open state; visual color alone does not carry the relation.
- Keyboard: quiz radio/checkbox controls preserve native arrow/space behavior; study local choices/reveal/rating are buttons; day edit fields use labels and standard table/form navigation; copy/download/reload/reapply/force are buttons with explicit names. Escape does not silently discard an edit or close a conflict pane.
- Do not place essential help solely in placeholder text, title attributes, hover states, tooltips, color, or motion. Respect 200% browser zoom and 320 CSS-px width without loss of action or information.
- The focus target after quiz submit remains submit/status; after study reveal, it remains on Reveal explanation while status announces result; after day save/error/conflict, focus goes to the persistent status heading; after reload/reapply, focus goes to the first editable field.

---

## UI Considerations

Applicable state considerations resolved: 8 explicit coverage statements, 5 backstop checks, 0 unresolved.

| Category | Element(s) | Status | Resolution / reason |
|---|---|---|---|
| empty | quiz/session, study cards, reports, day row | ✅ covered | Explicit empty/unavailable rows in the component matrix retain an action or standing-lane fallback. |
| loading | quiz submit, theme picker/save, day save/recovery | ✅ covered | Buttons disable only for active request; persistent live status states the operation and preserves draft/selection. |
| error | API quiz, theme save/picker, report, day editor | ✅ covered | Copywriting rows specify retry/recovery; no error fabricates success or clears user input. |
| populated | quiz, study, lesson, day, settings, report | ✅ covered | Matrix and layout contracts define one-column low-chrome happy paths with shared tokens. |
| partial | explanation optional fields, day/Anki/notes integrations, conflict snapshots | ✅ covered | Omit empty explanation sections; show integration warning without blocking the day; label both conflict versions. |
| overflow | sticky context, objectives, revisions, tables, conflict documents | 🧪 backstop | Wrap meaningful labels; independently scroll long revision/document regions; hold out a 320px and long-text browser test. |
| zero-one-many | study cards, reports, day plans / conflict cells | ✅ covered | Singular/plural status uses actual counts; no-card/no-row copy is distinct; long lists remain vertically stacked. |
| long-text | stems, options, explanation, plan cells, setting/help labels | 🧪 backstop | Normal prose wraps; controls expand vertically; use an automated long-text fixture plus manual zoom/320px test. |
| loading | navigation/link actions | 🧪 backstop | Native navigation keeps browser behavior; test that busy state does not trap focus or duplicate requests. |
| error | concurrent third edit / expired force token | ✅ covered | Return another no-write conflict, invalidate token, preserve draft, and restart recovery rather than forcing. |
| partial | unsupported Markdown grammar | ✅ covered | Explicit read-only/unsupported state names external-editor recovery and writes nothing. |
| overflow | reports metrics and lesson headings | 🧪 backstop | Tabular figures retain label/value pairing; headings wrap before viewport overflow. |
| long-text | conflict copy/download documents | 🧪 backstop | Render escaped text in labeled scrollable panes; copy/download receives full text without clipping. |

---

## Verification-Ready Contracts

| Contract | Automated evidence | Manual browser evidence |
|---|---|---|
| Shared palette / accent | `python tests/theme_roundtrip.py`: schema compatibility, deterministic derived pairs, pairwise ratios, adjustment notice, semantic independence, reset, picker fallback, all rendered token blocks | System/light/dark, custom source, adjusted source, deuteranopia-friendly verdict distinction |
| Quiz authority / hierarchy | `python tests/daemon_roundtrip.py` and `python tests/surface_roundtrip.py`: no key/scorer in served page, API-issued verdict, one context line, focus/reduced-motion hooks | Keyboard submit and narrow viewport; reserved feedback produces no material layout shift |
| Study explanation | `python tests/surface_roundtrip.py`: canonical complete payload, option rationale order, chosen/correct open state, no scoring call | Keyboard reveal/disclosures and non-choice card review |
| Day editing and conflicts | `python tests/day_edit_roundtrip.py` + daemon extension: exact-byte preservation, grammar refusal, revision mismatch no-write, draft/current payload, force-token binding/replay refusal, atomic replacement | Two-editor Obsidian conflict: copy/download/reload/reapply then explicit force flow; dirty navigation warning |
| Cross-surface responsive/a11y | Structural tests for shared generated CSS and no `DAY_CSS` literal palette | 320px, 200% zoom, light/dark, keyboard-only, screen-reader status and details semantics |

Run the CI-equivalent suite before phase close. End-of-phase UAT must exercise quiz, study, lesson-compatible shell, settings, report/index empty state, and day conflict recovery in both color modes.

---

## Registry Safety

| Registry | Blocks used | Safety gate |
|---|---|---|
| shadcn official | none | not applicable — no React/shadcn project or `components.json` |
| Third-party | none | not applicable — no external registry/package/block is permitted for this stdlib-only phase |

---

## Checker Sign-Off

- [ ] Dimension 1 Copywriting: PASS
- [ ] Dimension 2 Visuals: PASS
- [ ] Dimension 3 Color: PASS
- [ ] Dimension 4 Typography: PASS
- [ ] Dimension 5 Spacing: PASS
- [ ] Dimension 6 Registry Safety: PASS

**Approval:** pending
