# Phase 4: Surface Redesign & Theming - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-08-08
**Phase:** 4-surface-redesign-theming
**Areas discussed:** Question-screen hierarchy, Accent and OS theming, In-page day editing, Study explanations

---

## Area selection

| Option | Description | Selected |
|--------|-------------|----------|
| Question-screen hierarchy | Sticky context line and stem hierarchy | |
| Accent and OS theming | Picker, persistence, contrast, and semantic colors | |
| In-page day editing | Editing, saves, and concurrent-file conflicts | |
| Study explanations | Progressive disclosure of all explanation fields | |
| All four | Discuss every identified gray area | Yes |

**User's choice:** All four.
**Notes:** The user delegated detailed choices to the planning model: choose the most useful and comprehensive defaults, preserve multiple approaches when they can safely coexist, and avoid human stoppage for reversible choices that do not risk lasting harm or lower quality.

---

## Question-screen hierarchy

| Option | Description | Selected |
|--------|-------------|----------|
| Compact context line | Keep only orientation data sticky; disclose secondary metadata | Yes |
| Persistent metadata bands | Keep several always-visible chrome regions | |
| Minimal stem only | Remove nearly all context from the answering view | |

**User's choice:** Delegated; recommended compact context line selected.
**Notes:** Optimize hierarchy and accessibility while preventing layout shift.

## Accent and OS theming

| Option | Description | Selected |
|--------|-------------|----------|
| One source accent with derived accessible pairs | Persist the chosen color and compute checked light/dark tokens | Yes |
| Independent light/dark manual colors | Maximum control but higher complexity and easier contrast failure | |
| Fixed curated accents only | Strong safety but does not meet the OS-picker intent fully | |

**User's choice:** Delegated; derived accessible pairs selected, with advanced overrides left to planner discretion.

## In-page day editing

| Option | Description | Selected |
|--------|-------------|----------|
| Structured editor plus strong revision guard | Preserve surrounding Markdown and surface conflicts | Yes |
| Raw Markdown editor | Flexible but exposes the whole file and increases accidental damage | |
| Last-writer-wins cells | Simple but can silently destroy concurrent Obsidian edits | |

**User's choice:** Delegated; structured guarded editing selected.

## Study explanations

| Option | Description | Selected |
|--------|-------------|----------|
| Progressive disclosure by relevance | Open chosen/correct rationale first; retain all other fields | Yes |
| Show everything at once | Complete but visually overwhelming | |
| Concise answer only | Clean but continues discarding authored teaching content | |

**User's choice:** Delegated; progressive disclosure selected.

## the agent's Discretion

- Detailed visual design, responsive breakpoints, picker mechanics, diff UI, animation, and optional advanced controls.
- Planner may refine any reversible choice when research or code constraints show a stronger implementation.

## Deferred Ideas

None.
