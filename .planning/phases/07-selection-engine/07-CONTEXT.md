# Phase 7: Selection Engine - Context

**Gathered:** 2026-08-08
**Status:** Ready for planning

<domain>
## Phase Boundary

This phase delivers four things and nothing else:

1. **One selector** — a pure, inspectable, rule-based function that turns a selection
   request plus the evidence history into an ordered item list. It replaces the inline
   `random.shuffle` + slice that `surfaces/session.py:do_start()` does today
   (lines ~68-74), and it becomes the only place an item is chosen.
2. **A selection request shape** expressible identically from the CLI, from
   `/api/start`, and from a named profile in settings — objective, prerequisite, item
   type, difficulty, mode, count, seed, exclusions.
3. **Four selection modes** — diagnostic, practice, remediation, exam — composed from
   the same primitive filters, producing visibly different sessions.
4. **A trace** — for every selected item, why it was chosen over a named alternative,
   in plain terms, printable on demand.

**Explicitly not in this phase:**

- **Evidence-driven weighting and decay** (TREND-01, SCHED-01). Phase 10 owns "a weak
  objective raises its weight" and "what is due today". This phase builds the seam the
  weight plugs into (D-08) and ships no weighting model.
- Anki's due counts, the daily cap, and anything scheduling (Phase 10).
- Model-assisted selection of any kind. The selector is rule-based and deterministic;
  SEL-05 is a requirement, not a stretch goal.
- Changing the hint ladder or feedback policy (Phase 6). Session `mode` in the feedback
  sense and selection `mode` in the composition sense are two different words that must
  not be conflated — see D-06.

</domain>

<decisions>
## Implementation Decisions

**All decisions in this section were delegated by the user.** Asked which of four gray
areas to discuss, Weibao selected "Delegate all" — the standing instruction from
`02.1-CONTEXT.md`: *"the most optimal solution that gives us the most options and
directions in the future."* Here that instruction bites hardest, because Phase 10 feeds
directly on what this phase builds. Every D-number is Claude's judgment resolved toward
optionality and inspectability. The planner may revise any with a stated reason.

### One selector

- **D-01:** A new `selection.py`, a **peer of `model.py` and `runtime.py`** — imports
  those two and stdlib, imports no surface and no server. It exposes one entry point:

  ```python
  select(questions, spec, history) -> (items, trace)
  ```

  pure, deterministic given its three inputs, with no file reads of its own. The CLI,
  `/api/start`, and Phase 10 are all callers. This is the one-scorer rule applied to
  selection: not "surfaces call the selector" but "there is nowhere else an item can be
  chosen from".
  `surfaces/session.py:do_start()`'s inline `rng.shuffle(candidates)` is deleted, not
  wrapped — its objective filter and count clamp move into `select()`.
  — **Reversibility:** costly — once `/api/start`, the CLI, and Phase 10 all call it,
  moving the boundary means touching every caller and re-verifying determinism.

### How a selection is requested

- **D-02:** The request is a **selection spec dict** with a published schema
  (`schemas/selection.schema.json`, versioned like the other five contracts), carrying:
  `objective`, `prerequisite`, `type`, `difficulty`, `mode`, `count`, `seed`,
  `exclude_item_ids`, `pair`. Three surfaces produce the same dict:
  - CLI flags on `itembank start` / a new `itembank select`,
  - `/api/start` JSON fields,
  - **named profiles** in settings under `selection.profiles.<name>`, expanded to the
    same dict by one function.
  Profiles cost one expansion function now and are the place Phase 10's weights, the
  daily cap, and per-subject defaults hang later without a second request shape.
  A profile and explicit flags compose: flags override profile keys, key by key.
- **D-03:** The **spec is recorded on the session** (and in the evidence event for the
  sitting), not just its results. A session that cannot say what it asked for cannot be
  reproduced, and SEL-05's "why this item" is only checkable against the request that
  produced it.

### Explainability

- **D-04:** `select()` returns a **trace** alongside the items — never a second
  derivation. Per chosen item: which filters admitted it, its score under the mode's
  ordering, and **the nearest rejected candidate with the reason it lost**. That last
  part is what makes SEL-05's "why it was chosen over another candidate" literal rather
  than a paraphrase.
  Surfaced as `itembank select <bank> --explain` (plain text, one item per block) and as
  a `trace` field on `/api/start` when requested. The report surface may render it
  later; this phase prints it.
- **D-05:** The trace is written in **plain terms, not rule ids** — "chosen because it
  is the only unanswered item on objective `emt:airway:opa`; the runner-up
  `q14` was answered correctly 3 responses ago and is inside the cooldown window" —
  because the audience is one learner reading it, and because a trace nobody can read
  fails SEL-05 while technically satisfying it.

### The four modes

- **D-06:** The four selection modes are **named compositions of the same primitive
  filters**, not four code paths. One table maps mode → (filter set, ordering, count
  policy):
  - **diagnostic** — maximum objective spread: at most one item per objective,
    difficulty ascending, cooldown ignored (a diagnostic is allowed to re-ask).
  - **practice** — weighted toward objectives with recorded misses, cooldown enforced,
    mixed difficulty.
  - **remediation** — drawn only from objectives with a recorded failure, plus each
    failed item's pair partners (D-07), hardest last.
  - **exam** — fixed count, difficulty-balanced, no repeats within the sitting, seed
    recorded, no evidence-derived reordering at all (an exam must not be easier because
    you have been studying).
  **Naming hazard the planner must handle explicitly:** `session.mode` already exists
  and means *feedback policy* (MODE-01..06, Phase 6: drill / practice / diagnostic /
  exam). These two vocabularies overlap in three words and are not the same axis. Pick
  one of: a distinct field name (`selection_mode`), or a documented rule that the two
  are set together. Do not let them silently alias.
  — **Reversibility:** one-way if aliased — once evidence records a conflated field,
  separating them later needs a migration over the event log.

### Discrimination pairs

- **D-07:** Pairs need a **new item tag, `[PAIR: <name>]`**. The obvious "derive it from
  the existing field" shortcut does not exist: `model.py:61` parses `conf` from
  `CONFIDENCE:`, which is the author's confidence in the item, **not** a confusion set.
  Nothing in the current format records which items are commonly confused.
  `[PAIR:]` is additive, repeatable-by-name across two or more items, and lint warns
  `item.pair_singleton` when a pair name appears on exactly one item — a pair of one is
  an authoring mistake, not a valid state.
  Requesting `pair: <name>` serves every item in that pair together, adjacently, in one
  session (SEL-04).

### Recent exposure

- **D-08:** Exposure is read from the **evidence store** (`_evidence/evidence.jsonl`,
  Phase 1's unified store), never from session JSON. SEL-03's "verified across a resumed
  session" is only true if the memory outlives the session file, and Phase 1 exists
  precisely so there is one place to ask.
  Two rules, two settings keys:
  - **Hard exclusion** — items answered in the current sitting, and anything answered
    within the last `selection.cooldown_responses` responses (default 20).
  - **Soft penalty** — beyond the cooldown, recency lowers an item's ordering score
    rather than removing it, so a small bank does not run out of items.
  Splitting hard from soft is what stops a 30-item bank from returning nothing, and the
  soft half is the seam Phase 10's decay weight plugs into without a redesign.
- **D-09:** `select()` takes `history` as an **argument**, not as a file it opens. The
  caller reads the evidence snapshot and passes it. This keeps the selector pure and
  testable against a synthetic history, and it is what lets a trace record which
  evidence snapshot it rested on (D-04, and TREND-05's "every trend states the evidence
  it rests on").
- **D-10:** Determinism is a stated property: **same bank + same spec + same evidence
  snapshot + same seed ⇒ same items in the same order.** The seed is recorded on the
  session already; the trace records the snapshot marker. A test asserts it, because a
  selector that quietly drifts is unfalsifiable.

### Claude's Discretion

Every decision above (D-01 through D-10) is Claude's discretion under the delegated
instruction. Three specifically invite the planner to overrule:

- D-02's published `selection.schema.json`. If a sixth contract is more ceremony than
  the request shape earns, keep the dict and document it in `SPEC` instead — but say so
  rather than letting it drift undocumented.
- D-06's field-naming resolution. Either answer is defensible; leaving it ambiguous is
  not.
- D-08's default cooldown of 20. It is a guess, not a measurement. If the fixture banks
  are small enough that 20 starves practice mode, pick a fraction of bank size and say
  why.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements and roadmap

- `.planning/ROADMAP.md` § "Phase 7: Selection Engine" — goal, the five success
  criteria, and `Depends on: Phase 1` (complete, so this phase is unblocked).
- `.planning/REQUIREMENTS.md` § "Selection" — SEL-01 through SEL-05.
- `.planning/REQUIREMENTS.md` § "Trends" TREND-01 and § "Scheduling" SCHED-01 — the
  Phase 10 consumers of D-08's soft-penalty seam and D-02's profiles. Read them to know
  what **not** to build here.
- `.planning/REQUIREMENTS.md` § "Modes" MODE-01 through MODE-06 — the *feedback* mode
  vocabulary D-06 must not collide with.
- `.planning/PROJECT.md` — the core value ("the runtime, not the model, decides what
  reaches the learner") that makes a rule-based, inspectable first selector the correct
  shape rather than a stepping stone to a model-driven one.

### Prior phase context that still binds

- `.planning/phases/01-evidence-spine-protocol-foundation/01-CONTEXT.md` — the evidence
  store's shape, the item-identity scheme (`[ID:]` opaque hex + `[HASH:]` fingerprint),
  and the objective-query path D-08 reads through. `exclude_item_ids` uses `[ID:]`
  values, never item numbers, because numbers move when a bank is edited.
- `.planning/phases/02.1-packaging-self-update-interop-export/02.1-CONTEXT.md` — the
  steering instruction and the settings conventions any `selection.*` key follows.
- `.planning/phases/02-daemon-consolidation-settings-foundation/02-CONTEXT.md` — the
  `/api/*` conventions, `SystemExit` containment, and the every-route-has-a-CLI-twin
  rule that `itembank select` satisfies.

### Existing code this phase extends

- `surfaces/session.py:60-85` `do_start()` — the inline objective filter, `rng.shuffle`,
  and count clamp that D-01 replaces. Read the comment at lines 55-59 explaining why a
  non-positive count is rejected before the slice; that guard moves with the code.
- `runtime.py:1-11` module docstring — the one-scorer rule `selection.py` is modelled on.
- `runtime.py:133-160` `session_path` / `SESSION_UPGRADES` — the versioned-contract and
  forward-upgrade pattern a new session field (D-03's recorded spec) must respect.
- `evidence.py` — the append-only event log and its reader; D-08/D-09's history comes
  from here, and the disposable sqlite3 index from plan 01-08 is the fast path.
- `model.py:53-54` (`difficulty`, `objective`) and `model.py:61` (`conf` = CONFIDENCE,
  **not** confusion — the fact D-07 turns on).
- `schemas/session.schema.json` — where D-03's recorded spec lands.
- `surfaces/settings.py` / `schemas/settings.schema.json` — the `selection` group
  (`profiles`, `cooldown_responses`, and the recency-penalty knob), `x-itembank-phase: 7`.

### Codebase maps

- `.planning/codebase/ARCHITECTURE.md` — the four layers, and why `selection.py` sits
  beside `runtime.py` rather than inside a surface.
- `.planning/codebase/TESTING.md` — `tests/*_roundtrip.py`, direct execution.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `random.Random(seed)` seeding, already used in `do_start()` and in
  `runtime.public_item()`'s `build` shuffle — the determinism idiom exists; reuse it
  rather than inventing a second one.
- The Phase 1 sqlite3 index (plan 01-08) — the cross-subject objective query. D-08's
  history read should go through it rather than scanning the JSONL when the index is
  present, and degrade to the JSONL when it is not, matching the project's
  degrade-never-block rule.
- `surfaces/settings.py`'s bounded numeric validator — `selection.cooldown_responses`
  gets bounds there.
- `surfaces/protocol_cli.py` / `itembank schema` — the published-contract surface a new
  `selection.schema.json` would join.

### Established Patterns

- **One of each thing.** One parser, one scorer, one evidence store — and now one
  selector. The phrasing in `runtime.py`'s docstring ("what stops the CLI, the JSON
  session interface and the quiz page from quietly disagreeing") is the argument to
  reuse verbatim in `selection.py`'s docstring.
- **Pure functions with state passed in.** D-09 follows `score_response(q, answer)`:
  everything the function needs arrives as an argument.
- **Versioned published contracts** with a forward-upgrade registry.
- **Identifier-addressed, not index-addressed** — Phase 1 made `[ID:]` the stable
  handle. Exclusions and traces use it.
- **Degrade, never block** — no network anywhere in this phase, and a missing evidence
  store means "no history", not an error.

### Integration Points

- `selection.py` (new) — `select()`, the mode table, the trace builder.
- `surfaces/session.py` — `do_start()` becomes a caller; `--objective` joins a wider
  flag set.
- `surfaces/cli.py` — `itembank select` (new, with `--explain`), plus new `start` flags.
- `surfaces/daemon.py` — `/api/start` accepts the spec and can return the trace.
- `model.py` — the `[PAIR:]` tag, its stem-terminator alternation entry, and
  `item.pair_singleton`.
- `schemas/session.schema.json`, `schemas/settings.schema.json`, and possibly
  `schemas/selection.schema.json` (new).
- `tests/selection_roundtrip.py` (new) — the four modes producing visibly different
  compositions, the cooldown across a **resumed** session (SC3's actual wording), the
  pair request, the trace's runner-up field, and D-10's determinism assertion.

</code_context>

<specifics>
## Specific Ideas

- The standing steering instruction lands on three specific doors held open here:
  profiles (D-02) as the place Phase 10's weights attach, the hard/soft exposure split
  (D-08) as the place decay attaches, and `history` as an argument (D-09) so the
  selector never has to learn where evidence lives.
- SEL-05 — "it can explain why it chose each item" — is the requirement that most
  easily degrades into a checkbox. D-04's *named runner-up with the reason it lost* is
  the version of it that cannot be faked, and it is worth the planner treating as the
  phase's hardest deliverable rather than its last one.
- PROJECT.md's core value is that the runtime decides what reaches the learner. A
  rule-based selector is not a placeholder for a smarter model-driven one — it is the
  mechanism that keeps the guarantee true, and Phase 8's model never gets a vote here.

</specifics>

<deferred>
## Deferred Ideas

- **Evidence-driven selection weight and mastery drop-out** — TREND-01, Phase 10. The
  seam is D-08's soft penalty; the model is not built here.
- **What is due today / the daily cap** — SCHED-01, SCHED-02, Phase 10.
- **Trend-flagged at-risk objectives feeding selection** — TREND-04, Phase 10.
- **Rendering the trace in `/report` or `day`** — a later surface question. This phase
  prints it from the CLI and returns it from `/api/start`.
- **Authoring `[PAIR:]` tags across the real EMT/CS banks** — an authoring task, not a
  code task; possibly Phase 11's auditor territory.
- **Adaptive or IRT-style selection** — not in this milestone. SEL-05 says the *first*
  selector is rule-based and inspectable, which is a deliberate statement about what
  comes first, not a promise about what comes second.

</deferred>

---

*Phase: 7-selection-engine*
*Context gathered: 2026-08-08*
