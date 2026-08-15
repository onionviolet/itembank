# Which rules actually blocked past ideas: evidence sweep (2026-08-15)

Seed data for step 2 of `.planning/RULE-AUDIT-PLAN-2026-08-15.md`. Produced by
a read-only sweep of every disposition record in `.planning/` (synthesis 12.4
and 12.5, DECISIONS files, USER-VISION records, research briefs, the
2026-08-10 constraint audit, PROJECT.md out-of-scope, blocker and readiness
audits, notes, quick tasks). Per-item detail lives in those sources; this file
records the aggregate and the actionable flags.

## Tally: rules cited as rejection grounds, most-cited first

| Rank | Rule cited | Approx. count | Note |
| --- | --- | --- | --- |
| 1 | stdlib-only / no dependency / no build step | ~20 | A relaxed preference since 2026-08-09, yet the single largest veto source. The project's own `research/2026-08-10-constraint-audit.md` verdicts: 11 cargo-culted, 1 miscited, 4 overstated, 1 erosion-by-omission. |
| 2 | One parser, one scorer (Directive 4.2) | ~10 | Mostly legitimate: QTI second parser, Rust/Go port creating two scorers, branching lesson styles, tier-3 LLM judge. One overstated cite (F8), one cargo-culted cite that survived on a different rule (F1). |
| 3 | Truthful evidence | 6 | All in synthesis 12.4; all sound. |
| 4 | Accessibility gates (Directive 4.5 / UI-SPEC) | 6 | Includes one miscited case (explorable explanations, later re-grounded on VIS-01). |
| 5 | Data residency / no telemetry (Directive 4.3) | 5 | Caliper, webhooks, Arize Phoenix (half-valid), hosted storage, LAN default. |
| 6 | Runtime assessment authority (Directive 4.1) | 5 | All sound. |
| 7 | Cost, value, or scope with no named rule | ~8 | See flags below. |

Rules that were audited as misreadable on 2026-08-15 but have never actually
blocked anything: never-auto-grade-prose, accessibility self-certification,
dual daemon+CLI surface, additive format compatibility (zero rejection cites
each; additive-format has only ever been cited as a satisfied gate).

## Flags: rejections resting on cost, scope, or preference alone

The project standard (READINESS-AUDIT-14A A8) fails simplicity-only
rejections. A8 certified zero, but it audited only synthesis 12.4. Outside
that scope:

1. The 2026-08-10 constraint audit's 20 findings, of which the standouts are
   F10 (pywebview rejected "regardless of legitimacy"), F2 (CodeMirror, since
   reversed), F5 (zero-dependency treated as a security control).
2. Inline hint stack H3 (scope only), guided tour F3 (cost plus an unverified
   assumption), custom titlebar (maintenance cost), margin sidenote R3
   (layout preference), data-URL fonts (cost, honestly recorded), TanStack
   table (cost-shaped, disclosed), cookbook style (house preference).

Most of these are disclosed cost rejections rather than hidden ones; the
constraint-audit set is the real violation cluster.

## Still-standing rejections on dead grounds (revisit candidates)

From the constraint audit, rejections whose cited rule no longer binds and
which were not yet re-decided on merit:

- F4: PDF and DOCX parsing (rejected under stdlib-only). Directly gates the
  source-to-course milestone's book and syllabus intake.
- F3: non-stdlib Anki import (cargo-culted; the stdlib path may be
  unmeetable).
- F17: pytest / test-runner (cargo-culted; the audit notes it "is costing
  verification coverage").
- F5: supply-chain policy (a preference standing in as a security control;
  needs a real policy, not a dependency count).
- F7: third-party markdown/table renderer ("not evaluated further" at the
  time); F10 (pywebview, now a reversal-cost question); F15/F9 (packaging
  conflict owed reconciliation).

## Verdict on the friction question

Development friction from rules is real and measured, but the source is not
the runtime invariants. The one-scorer, assessment-authority, truthful-
evidence, and data-residency rules earned nearly all of their citations. The
friction came from a constraint that was retired on 2026-08-09 (stdlib-only)
continuing to do veto work downstream for another day-plus of research, and
from a minority of cost-only rejections outside the audited ledger. The five
rules clarified on 2026-08-15 were latent risks, not demonstrated blockers.
