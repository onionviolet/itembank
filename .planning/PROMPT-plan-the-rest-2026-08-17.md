# Prompt: plan the rest of the milestone and close the open discussions

Paste this whole file as the opening message of a fresh planning session on a
capable model. It is self-contained; it does not depend on chat history.

---

You are running a planning-only session on `itembank`
(`C:\Users\wayba\Downloads\CTF\itembank`, branch `main`). Read
`.claude/CLAUDE.md`, `AGENTS.md`, `.planning/PLANNING-DIRECTIVES.md`,
`.planning/SOURCE-TO-COURSE.md`, and `.planning/STATE.md` before you write
anything. Your job is to leave the milestone with zero unplanned subphases and
zero open discussions, so that a lesser model (Codex plus DeepSeek) can execute
every remaining piece without a design question ever reaching it.

## Operating rules, in force for the whole session

1. **Keep going.** PLANNING-DIRECTIVES section 2 is the autonomy rule. Do not
   stop to ask a question you can answer from the codebase, the research
   artifacts, or a defensible default. Record the assumption and continue. Stop
   only for a hard-to-reverse action, a choice that lowers quality whichever way
   you guess with no research verdict, or a conflict with the five
   non-negotiables in section 4. Nothing else earns a stop.
2. **When two designs both look defensible, build both.** PLANNING-DIRECTIVES
   section 3: implement both behind one interface and make the choice a setting,
   so Weibao picks later from real options instead of from a description. The
   2026-08-13 qualification binds: a second design is registrable only when it
   shares the canonical objects, authority, accessibility, permission, recovery,
   and maintenance contracts, and states purpose, eligibility, required and
   optional learner actions, skip and resume, evidence effects, accommodations,
   offline behavior, and tests. When two options need two parsers, two scorers,
   or two evidence stores, pick one and write down why.
3. **Prefer the more comprehensive consideration.** Where a discussion offers a
   narrow reading and a broad one, and the broad one costs no extra authority
   surface, take the broad one and record its cost honestly.
4. **Plan only. Do not execute.** This session writes planning artifacts and
   commits them. Codex executes. Every plan is written to the
   PLANNING-DIRECTIVES section 5 lesser-model executor bar, all six legibility
   requirements.
5. **No em dash characters** anywhere you write, including plans, prose, and
   comments. Use commas, parentheses, colons, semicolons, or separate sentences.
6. **A concurrent Codex track shares this working tree.** The GSD `query commit`
   helper sweeps every dirty tracked file. Use pathspec-limited
   `git commit -- <paths>` for everything you commit. Do not touch
   `scripts/preflight.py`, `tests/preflight_roundtrip.py`, `AGENTS.md`,
   `.gitattributes`, or anything under `fixtures/`, which are another agent's
   in-flight work as of 2026-08-17.
7. **The rejection and supersession ledger is append-only.** Every idea you
   settle gets a durable disposition (core, registered, prototype, backburner,
   deferred, superseded, rejected) with evidence, reason, retained alternative,
   date, and reconsideration condition. Untimely is not rejected, and simplicity
   alone is never a rejection reason.

## Part A: close the five open discussions first

Planning depends on these, so do them first. Each one ends as an
`.planning/IDEA-LEDGER.md` disposition update plus, where it changes scope, a
ROADMAP edit. Apply rules 2 and 3 to each.

- **A1. What counts as "an entire field."** Weibao's 2026-08-13 vision entry
  (`.planning/USER-VISION-INBOX.md`, promoted to `USER-VISION.md`) asks for
  courses that nest into subcourses, semesters, and concepts that build up a
  whole field, with completion and progress across that whole field, and it says
  explicitly that what counts as a field needs more ideaboarding. This is the
  largest undischarged product question in the milestone and it shapes 17B's
  tracer scope. Produce a bounded ideaboard, then a recorded model of hierarchy
  depth, completion semantics, and progress rollup that does not reduce progress
  to a single percentage (the bake-in gate in GRAPH-03 forbids retrievability as
  a percentage, and GRAPH-03 already names seven progress dimensions). Where two
  completion models both defend themselves, register both.
- **A2. IL-20260815-09, real supply-chain policy.** Marked registered and
  blocking for dependency adoption. Settle it now, because 17B and 18 both make
  dependency decisions and currently argue from an unwritten rule.
- **A3. IL-20260815-07, PDF and DOCX source intake.** Marked as needing one
  bounded research pass, do not adopt yet. Run that pass. Source intake is the
  front door of the source-to-course milestone.
- **A4. IL-20260816-01, plugins as the feature-delivery mechanism at named
  seams.** The newest open idea, and it interacts with IL-20260815-02 capability
  seams. Its rejected sibling IL-20260815-04 (plugin-first core, swappable
  scorer) is already settled and stays rejected, so the remaining question is
  bounded to seams that do not touch the one scorer.
- **A5. Backlog phases 999.2 (bilingual reader) and 999.3 (MCP surface).** Last
  reviewed 2026-08-10, before the source-to-course reframe. Re-argue both
  against current scope and record promote, keep, or supersede with reasons.

## Part B: plan every remaining piece

Per PLANNING-DIRECTIVES section 6, each phase owes discuss, then ui-phase if it
has a learner-facing surface, then plan-phase. Follow that order. Write plans to
the section 5 executor bar.

- **B1. Phase 17B, production vertical tracer.** The only subphase with no phase
  directory. Scope in `ROADMAP.md`: a polished unit from discovery through
  restore, gates G1 through G11. It has a learner-facing surface, so it owes a
  UI-SPEC. Fold in A1's field-completion model.
- **B2. Phase 18, external-user v1.** Scope in `ROADMAP.md` line 114 and the A10
  bar in `READINESS-AUDIT-14A.md`. No phase directory. It carries three named
  sub-decisions: code signing (which fires V2-DEL-01), the agent-facing update
  and capability disclosure manifest, and the packaging conflict IL-20260815-11
  that was explicitly deferred to this phase. The cold-agent onboarding
  transcript is this phase's owed fixture. The shell question is already closed:
  17A-CONTEXT D-08 makes the browser-served UI the single canonical shell, so
  ROADMAP line 114's "decided at 16B/17A planning" is stale text to fix.
- **B3. Post-Phase-17 maintenance and restore audit.** Registered around
  `ROADMAP.md` line 2282 as owed after 17B, with no phase, no plan, and no
  owner. Give it one.
- **B4. 13.5 defects D1 and D2.** Currently Backlog rows with the mechanism
  already diagnosed in `13.5-GATES.md`. D1: `--measure-prose:59ch` resolves
  against the 16px `.wrap` font instead of the 18px reading face and `.card`
  padding eats 48px more, so the measure renders 422px against a contracted
  531px, and D1 blocks the RTS-04 gate from closing. D2: `span#tot` is
  server-rendered as 0, so the quiz band paints "Item 1 of 0" until the first
  interaction. Turn both into one executable plan or quick task with the test
  pins named (`stylesheet_roundtrip` for D1, a `daemon_roundtrip` first-paint
  assertion for D2).
- **B5. OLED and true-black theme.** Backlogged since 2026-08-10 and fully
  scoped: one `theme` enum value plus a true-black token set with contrast
  re-verified, and the `/settings` option. Phase 17A is the theming-adjacent
  phase it was waiting for. Fold it into 17A or reject it explicitly in the
  ledger.

## Part C: two corrections to make while you are in there

- **C1.** `.planning/STATE.md` line 6 still says "17A and 17B are the remaining
  unplanned subphases." Commit `aa21ac1` landed four 17A plans on 2026-08-16.
  Only 17B is unplanned. Fix that status line in your first STATE update.
- **C2.** The four 17A plans carry no recorded plan-checker verdict, unlike 16C
  which recorded READY with all nine plans PASS. Run the plan-checker on 17A and
  record the verdict before 17A goes to Codex.

## What done looks like for this session

1. All five Part A discussions carry a durable ledger disposition, with both
   options registered wherever two defensible designs exist.
2. 17B, 18, and the post-17 maintenance audit each have a phase directory, the
   artifacts section 6 requires, and a checker-verified plan set at the executor
   bar.
3. B4 and B5 are each either a plan or a recorded rejection, not a backlog row.
4. 17A carries a plan-checker verdict.
5. `STATE.md` is accurate, and the ROADMAP progress table and subphase sequence
   match what is on disk.
6. Every commit is pathspec-limited and left the other agent's in-flight files
   untouched.

Report at the end: what you decided, what you registered as two options for
Weibao to choose between later, what you assumed and why, and anything you could
not settle without him.
