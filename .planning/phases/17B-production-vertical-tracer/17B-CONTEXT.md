# Phase 17B context: production vertical tracer

- **Gathered:** 2026-08-17, planning-only session (PROMPT-plan-the-rest),
  autonomous under PLANNING-DIRECTIVES section 2; decisions recorded here are
  binding on the 17B plan set and are not re-litigated at execution.
- **Phase entry:** ROADMAP.md "Phase 17B: Production Vertical Tracer (details
  added 2026-08-17)", which enumerates gates G1 through G11 against
  `research/phase-16/14-synthesis.md` section 16.1.

## Domain

17B is the milestone's exit proof, not a feature phase. It takes one course
unit through the whole source-to-course loop at production quality and
verifies the eleven exit gates end to end on served bytes and recorded
evidence. It builds no new subsystem: every capability it exercises was
frozen by 14A through 17A. Where the tracer finds a gap, the gap is a
defect against the owning subphase's contract, never a 17B invention.

## Decisions

- **D-01 Precondition halt.** Plan 17B-01's first task verifies, by file
  presence and recorded freeze/summary artifacts, that 14A, 14B, 15A, 15B,
  16A, 16B, 16C are executed, 17A's freeze record exists
  (`17A-FREEZE.md` with a freeze, not a withholding), and the Phase 13.9
  walking-skeleton summaries exist. Any missing precondition halts the wave
  with the exact missing artifact named (16C-01 precedent). Handing the
  plan set to an executor early is safe; it will correctly refuse.
- **D-02 Fixture rule.** All gate evidence comes from a realistic synthetic
  fixture course kept in this repository and `itembank guard` clean:
  invented subject matter at real production depth (one unit of a fictional
  field), never AAOS-derivative or other real course content. Weibao may
  additionally run the same flow on a real course outside the repository;
  that evidence is supplementary, and repo-side records carry pointers,
  counts, and hashes only.
- **D-03 Scope tree and rollup (IL-20260817-01).** The fixture carries a
  minimal scope tree: one open field scope containing one bounded course
  scope containing the unit. Both registered rollup models render over the
  same GRAPH-03 tuples: ROLLUP-DIM (dimension-wise, stated denominators)
  and ROLLUP-MAP (one-level map view). The bounded course completes under
  its named predicate during the tracer; the open field never shows
  complete and states its scope version on every claim. Weibao picks the
  default rollup at a checkpoint from the rendered screens; the choice is
  a per-scope setting with a global default.
- **D-04 Gate evidence record.** `17B-GATES.md` is the acceptance record:
  one row per gate G1 through G11, each row naming its concrete check (from
  the ROADMAP details block), the command or fixture that proves it, the
  evidence pointer, and pass, fail, or human-pending state. Human
  checkpoints are mandatory for the G4 screen-reader item and the final
  visual acceptance; an agent never self-certifies those (17A D-09
  precedent, AGENTS.md authored-output accessibility rule).
- **D-05 Legacy upgrade audit.** One legacy lesson and one legacy question
  artifact (chosen from the repository's synthetic fixtures, not real
  banks) pass the upgrade audit: baseline audit before edit, learning-value
  delta stated, identity and assessment meaning preserved, bounded diff
  presented, fallbacks retained. This exercises the legacy-upgrade skill
  contract; if that skill is still a stub at execution time, the audit is
  performed against the operation contract directly and the skill gap is
  recorded as a defect, not silently filled in.
- **D-06 Defect handling.** A failed gate check becomes either an in-phase
  fix task (single-file, no contract change, no scorer or parser edit) or
  a recorded defect routed to the owning subphase's backlog with mechanism
  diagnosed (13.5 D1/D2 precedent). The tracer never widens into a repair
  phase; 17B closes with every gate either passed or carrying a named
  defect and a named owner, and the freeze record says which.
- **D-07 Restore drill mechanics (G10).** The drill runs on this Windows
  machine simulating a clean machine: a fresh clone of the repository at
  the tested commit into a temp directory, a fresh empty data directory,
  network access unavailable to the process under test, then restore of
  the exported course package and evidence, manifest validation, and a
  loss report listing every capability the restore could not carry. The
  drill is scripted so 17C can rerun it as a sweep.
- **D-08 No new dependencies.** 17B introduces no third-party artifact. Any
  driven-browser evidence reuses whatever 17A-04 approved under the
  supply-chain policy; if 17A-04 recorded none, the corresponding checks
  fall to the scripted human QA path.
- **D-09 Egress check scope (G11).** For any hosted-model call the tracer
  makes, the disclosed egress manifest must equal what was actually sent
  (IL-20260815-01's reconstructability question, checked at this one
  seam). If the tracer's run makes no hosted call, G11's egress row records
  not-applicable with that reason, and the rights-unknown refusal check
  still runs.
- **D-10 No new visual language.** 17B uses 17A's frozen tokens and
  primitives only. A missing component or token is a 17A-03 primitive gap
  handled under D-06; 17B invents nothing visual. The 17B UI-SPEC is an
  experience contract for the unit, not a token document.

## Canonical references

- `ROADMAP.md` 17B details block (gates, plan list, fixture rule).
- `research/phase-16/14-synthesis.md` section 16.1 (gate definitions).
- `SOURCE-TO-COURSE.md` preserved Phase 17 rationale and closing bar.
- `IDEABOARD-FIELD-2026-08-17.md` and IDEA-LEDGER IL-20260817-01 (scope,
  boundedness, rollup models).
- `.planning/UI-SPEC.md` section 8 (the nine accessibility gates).
- `PLAN-TEMPLATE.md` and PLANNING-DIRECTIVES section 5 (executor bar).

## Deferred

- Which real course Weibao supplements with (his choice at execution).
- The default rollup model (D-03 checkpoint).
- Any defect fixes beyond D-06's single-file bound (routed to owners).
- MCP, packaging, signing, onboarding (Phase 18 and 999.3 own these).
