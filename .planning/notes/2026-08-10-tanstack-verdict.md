# Note: TanStack — take the architecture, decline the bundle

- **Date:** 2026-08-10
- **Context:** `/gsd-explore` session. Question: "should we incorporate TanStack into graphing or other stuff?"
- **Status:** verdict recorded. One component held as a seed. No adoption.
- **Verification:** `tanstack.com` and jsDelivr package fetches, 2026-08-10.

---

## 1. Verdict in one line

**Adopt TanStack's architecture, which this project already has. Decline every
package except one, which becomes a seed with a measured trigger.**

Per Directive §4a, this is a **merit** rejection, not a dependency rejection.
Dependencies are permitted. Each package below is refused for a reason that would
still hold if `npm install` were free.

## 2. What TanStack is

Headless, framework-agnostic, TypeScript-first libraries. Verified from
`tanstack.com`, 2026-08-10: Start, Router, Query, DB, Store, AI, Table, Charts,
Form, Hotkeys, Markdown, Highlight, Virtual, Pacer, Devtools, Config, CLI, Intent.

Headless is the defining idea. Table computes row models, sorting, filtering and
grouping, and emits zero markup. Query owns a cache with staleness, retry and
invalidation, and owns no UI.

## 3. The part worth taking, which costs nothing

**TanStack validates two decisions already made here.** That is the actual value
of this exploration, and it is worth recording so neither gets softened later.

- **Headless separation.** Table decides what a row *is*; the caller decides what
  it looks like. itembank's runtime decides what a learner may see; the surfaces
  decide how it looks. Same shape. This is `CLAUDE.md`'s Core Value stated in a
  different vocabulary by a project with no stake in ours, which is mild external
  evidence the architecture is not idiosyncratic.
- **Invalidation over refresh.** Query does not tell the UI to re-render. It marks
  data stale and every consumer re-derives. `ROADMAP.md` Extensibility Rule 5
  already says "Derived, never stored... computed from the append-only log on
  demand. A cache is allowed only if it is disposable and its staleness is
  detectable." Same rule, and itembank's version is stricter.

Take the vocabulary. Cite it in review when someone proposes a stored coverage map.

## 4. The existing contract this collides with

`UI-SPEC.md:308-310`, an approved contract:

> | Tool | None — stdlib Python with embedded HTML/CSS/vanilla JS. No shadcn, registry, npm, or external component dependency. |
> | Component approach | Native semantic HTML first; inline SVG for initial visual items; vendored KaTeX only in Phase 9. |

Per Directive §4a this is **not** one of the five non-negotiables, so it informs
and does not veto. It is recorded here because citation discipline requires the
sentence, and because a future adoption argument has to beat it on merit rather
than pretend it is absent.

## 5. Package by package

Measured on jsDelivr, 2026-08-10.

| Package | Measured | Verdict | Reason on merit |
|---|---|---|---|
| `@tanstack/charts` | **0.9.0, pre-alpha**; pulls **17 d3 packages** (shape, scale, geo, sankey, force, …) | **Reject** | Unstable API and a 17-package transitive graph, for charts that are a handful of sparklines. Not vendorable as one file, so it drags in a bundler as a side effect rather than as a decision. |
| `@tanstack/table-core` | 9.1.2, **111 KB min**, now also needs `@tanstack/store` (+5.8 KB) | **Reject** | Its value is client-side sort, filter and group over thousands of rows the server never re-fetches. itembank renders tables server-side from Python against banks of a few hundred items. Paying 117 KB to move work *to* the client that is already done *on* the client's own machine is backwards. |
| `@tanstack/virtual-core` | 3.17.7, **23 KB min, zero imports, single vendorable ESM file, no bundler** | **Hold as seed** | The only one with a real future problem to solve, and the only one that vendors as cleanly as KaTeX did. See §7. |
| Query / Router / Start / Form | — | **Reject** | Presuppose a JS application shell. itembank's surfaces are server-rendered pages. Adopting these is adopting a frontend rewrite, which is Phase 13's question and not a library question. |

## 6. Graphing: the actual recommendation

Phase 10 (Retention, Pacing & Trends) is where charts land. The recommendation is
**generate `<polyline points="…">` inline SVG in Python**.

It wins on the criteria that bind here, not on frugality:

1. **Zero JavaScript**, so a trend renders in a `.pyz`, in the Tauri webview, in a
   `--lan` phone tab, and in the plain-HTML fallback, identically.
2. **`UI-SPEC.md` §8 gates are satisfiable.** An SVG generated server-side can carry
   `role`, a title, and a real `<table>` fallback in the same response. A canvas
   chart cannot, and a d3 chart only can if someone remembers to.
3. **It matches the existing precedent.** §310 already says "inline SVG for initial
   visual items." A trend line is that, with fewer requirements.
4. **`--pending` and the semantic tokens keep working**, because the SVG is styled
   by the same `SHARED_CSS` custom properties as everything else. A d3 chart brings
   its own color logic and would need the palette re-expressed.
5. It cannot render a mastery percentage by accident, which `UI-SPEC.md` §13 forbids
   outright.

`@fnando/sparkline` (vanilla, zero deps, SVG output) is the fallback if the Python
generator turns out awkward. It should not, since a polyline is a coordinate
transform and roughly 30 lines.

## 7. The one seed

`@tanstack/virtual-core`, 23 KB, zero dependencies, one vendorable file. Held
against a **measured** trigger, not a guessed one. See
`.planning/seeds/tanstack-virtual-core.md`. Do not adopt it pre-emptively: the
lists it would help (auditor coverage, evidence history, long lessons) do not exist
yet, and their real sizes are unknown.

## 8. Related

- `.planning/notes/2026-08-10-mcp-as-third-surface.md`
- `.planning/seeds/tanstack-virtual-core.md`
- `UI-SPEC.md` §7 System, §8 Accessibility, §13 Do Not Build Yet
- `ROADMAP.md` Extensibility Rule 5, Phase 10, Phase 13
