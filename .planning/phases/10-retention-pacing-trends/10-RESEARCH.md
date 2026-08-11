# Phase 10: Retention, Pacing & Trends - Research

**Researched:** 2026-08-08
**Domain:** Evidence-derived objective scheduling, per-subject pacing, and longitudinal reporting in a stdlib-only local Python application
**Confidence:** MEDIUM

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

### One evidence snapshot and provenance
- **D-01:** Every `day`, report, and selection-weight calculation for a render uses one immutable evidence snapshot marker. All displayed claims name the window, event count, and objective/subject filter behind them.
- **D-02:** Derived scheduling/trend state is disposable and reproducible from append-only evidence. Caches may accelerate reads but are never authoritative.
- **D-03:** Insufficient evidence is a first-class `unknown` state, not zero mastery, zero due, or a fabricated trend.

### Objective scheduling
- **D-04:** itembank schedules objectives, not cards. Each objective receives transparent signals for last successful evidence, recent accuracy, hint depth, pending review, and elapsed time; the planner/researcher chooses and documents the initial bounded formula.
- **D-05:** “Due today” is a labeled itembank recommendation with a reason and evidence basis. Anki due/new counts remain a separate labeled signal read in the same render snapshot; neither number is summed into the other.
- **D-06:** Objective states include due, at-risk, weak, stable, mastered, and unknown as derived labels over visible component signals. Thresholds live in settings with conservative defaults and schema bounds so later tuning does not require code changes.

### Daily cap and pacing
- **D-07:** `daily_cap` is enforced per subject using live evidence already recorded for the local day. Once reached, `day` blocks starting more ordinary work for that subject and explains the count.
- **D-08:** A deliberate override may coexist for exceptional use, but it must be explicit, time-limited to that launch/sitting, and recorded as an override event. There is no silent or persistent “ignore cap” toggle. This preserves user choice without making the cap cosmetic.
- **D-09:** Pending manual marks count as work attempted for pacing but not as success/mastery. Retracted responses disappear through the existing live-event filter.

### Selection feedback loop
- **D-10:** Phase 10 supplies a normalized objective-weight map and evidence snapshot to Phase 7's pure selector. It does not choose items directly or add another selector.
- **D-11:** Weak/missed objectives receive a bounded boost; mastered objectives receive a bounded reduction but do not become permanently unreachable. Recency/decay and difficulty-spread inputs compose with the Phase 7 trace so every chosen item can explain the influence.
- **D-12:** Changes are gradual and capped per snapshot to avoid one bad session causing an extreme next session. Exam selection remains evidence-neutral as Phase 7 decided.

### Trends and reports
- **D-13:** Longitudinal reports show accuracy by objective over selectable week windows, highest/average hint tier, attempts, pending manual review, last evidence date, and at-risk reason. Raw counts accompany rates.
- **D-14:** At-risk means previously demonstrated success plus a configurable period without confirming evidence; it is not predicted failure presented as fact.
- **D-15:** The report supports overview→subject→objective drill-down and a CLI JSON/plain-text twin. Visual chart form is delegated to UI planning; the underlying series and provenance contract are surface-neutral.
- **D-16:** Manual-review outcomes enter mastery only after accepted mark events. Model proposals from Phase 8 never affect scheduling until accepted.

### the agent's Discretion
The initial formula, thresholds, and chart choices require research and a stronger planning/UI model. They may expose multiple user-selectable profiles if comparisons show no single universally best pacing model; all must remain inspectable, bounded, and reproducible.

### Deferred Ideas (OUT OF SCOPE)
- Owning card intervals/ease or writing Anki schedules — out of scope for this milestone.
- Predictive ML mastery models — defer until evidence volume justifies them.
- Curriculum coverage auditing — Phase 11.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|---|---|---|
| SCHED-01 | The tool computes what is due today per objective from its own evidence | Pure derived schedule snapshot, objective signals, provenance contract |
| SCHED-02 | A daily cap prevents a course being binged, enforced through `day` | Local-day live-event count plus explicit one-sitting override event |
| SCHED-03 | Anki keeps owning card reviews; itembank never writes a card schedule | Reuse read-only `anki_read`; retain two labeled, unsummed signals |
| SCHED-04 | A completed lesson enters a transparent review queue | Objective schedule state is transparent and settings-bounded; lesson-completion event is a required integration seam |
| TREND-01 | Weak objective raises selection weight; mastered one drops out of rotation | Normalized bounded map passed to Phase 7 selector; re-enters on due/at-risk |
| TREND-02 | `day` load is evidence-backed and says when a plan needs re-cutting | Replace tick-derived lane load with subject pacing derived from the same snapshot |
| TREND-03 | Longitudinal report shows accuracy, hints, pending manual marking | Surface-neutral weekly series plus HTML and CLI render twins |
| TREND-04 | Untouched previously-correct objective is at-risk before failure | Last confirmed success and configurable silence interval; no failure prediction |
| TREND-05 | Every trend states its evidence | Immutable snapshot marker, filters, window, and counts in every output |
</phase_requirements>

## Summary

Build one pure `retention.py` derivation layer beside `evidence.py`, not a second store or a scheduler inside a surface. It receives a caller-captured list of live evidence plus an explicit local-day/window policy and produces serializable objective summaries, a normalized weight map, cap decisions, and provenance. This matches the existing architecture: the log is authoritative while the SQLite index is disposable, and `objective_history()` already returns only live response events. [VERIFIED: evidence.py:613-650]

The initial model should be deliberately conservative: absent or insufficient settled evidence remains `unknown`; pending manual responses count only toward pacing; and a mastered objective is temporarily deprioritized, never erased. The available learning research supports spacing/retrieval but does not identify a universally correct adaptive formula, making visible configurable thresholds safer than fitted mastery or ML. [CITED: https://pubmed.ncbi.nlm.nih.gov/21707204/] [CITED: https://pubmed.ncbi.nlm.nih.gov/24744260/]

**Primary recommendation:** Implement a single snapshot-to-derivation contract first, then attach it to `day`, Phase 7 selection, and `/report`; preserve Anki as a read-only external signal.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|---|---|---|---|
| Evidence snapshot and objective derivation | API / Backend | Database / Storage | Runtime code derives views from append-only local evidence; index remains a cache. [VERIFIED: evidence.py:613-650] |
| Daily cap gate and override recording | API / Backend | Frontend Server (SSR) | The runtime must decide a cap before ordinary work starts; `day` presents the decision. [ASSUMED] |
| Trend/report series | API / Backend | Frontend Server (SSR) | One surface-neutral report payload feeds CLI JSON/text and daemon HTML. [ASSUMED] |
| Anki due/new display | Frontend Server (SSR) | API / Backend | Existing day surface obtains optional local AnkiConnect counts and degrades to a note. [VERIFIED: surfaces/day.py:370-395] |
| Selection weighting | API / Backend | — | Phase 10 supplies weights and snapshot; Phase 7 owns the pure item choice. [VERIFIED: .planning/phases/07-selection-engine/07-CONTEXT.md] |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---|---:|---|---|
| Python standard library | 3.11 CI baseline | `datetime`, `json`, `sqlite3`, pure functions | The repository declares “Python standard library only” and CI uses `python-version: "3.11"`. [VERIFIED: itembank.py:39-40] [VERIFIED: .github/workflows/ci.yml:10-12] |

### Supporting
| Library | Version | Purpose | When to Use |
|---|---:|---|---|
| Existing AnkiConnect HTTP reader | existing | Separate optional due/new count | Read-only presentation signal only; closed Anki degrades rather than blocks. [VERIFIED: surfaces/day.py:370-395] |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|---|---|---|
| Transparent rule model | Fitted/ML mastery model | Deferred by locked scope; cannot be audited from sparse evidence. [ASSUMED] |
| Objective scheduling | Anki card scheduling | Violates SCHED-03 and mixes unrelated ownership. [VERIFIED: surfaces/day.py:370-395] |

**Installation:** No package installation. [VERIFIED: itembank.py:39-40]

## Architecture Patterns

### System Architecture Diagram
```text
append-only evidence.jsonl
        │ live_events() / accepted marks
        ▼
immutable snapshot {cutoff, byte/event count, filters, local day}
        ▼
retention.py (pure derivation)
 ├─ objective states + provenance ──► report payload ──► CLI /report HTML
 ├─ subject pacing + cap decision ──► day ──► start guard / explicit override event
 └─ normalized weights + snapshot ──► Phase 7 select() trace ──► session

AnkiConnect read-only due/new ───────► day snapshot display (separate, never summed)
```

### Recommended Project Structure
```text
retention.py                 # pure snapshot, objective summaries, weights, pacing
surfaces/day.py              # one snapshot render and cap presentation/gate
surfaces/session.py          # ordinary-start gate and one-sitting override plumbing
surfaces/daemon.py           # identifier-addressed report/start API twins
schemas/settings.schema.json # bounded scheduling/trend settings
schemas/report.schema.json   # additive longitudinal payload/provenance contract
tests/retention_roundtrip.py # synthetic, timestamp-controlled behavioral suite
```

### Pattern 1: Capture once, derive many
**What:** Capture the live events and snapshot metadata once per render/request, then pass immutable data to all derived functions. [ASSUMED]

**When to use:** Every `day`, report, selector weight, and cap evaluation. [VERIFIED: .planning/phases/10-retention-pacing-trends/10-CONTEXT.md]

**Example:**
```python
# Existing evidence contract: live events exclude retractions.
snapshot = retention.snapshot(evidence.live_events(log), now_utc, local_day, filters)
summary = retention.derive(snapshot, settings)
weights = retention.objective_weights(summary, settings)
```

### Pattern 2: Settled-result projection
**What:** Treat `True`/`False` auto scores and the latest live accepted mark as settled outcomes; retain `None` without a live mark as pending. [VERIFIED: runtime.py:120-130] [VERIFIED: evidence.py:1116-1137]

**Anti-Patterns to Avoid**
- **A per-surface recomputation:** It can produce report/day/selector disagreement after an append. Pass the same snapshot. [ASSUMED]
- **Using raw `events()` for learner counts:** Retracted responses would leak back into pacing and trends; use `live_events()`. [VERIFIED: evidence.py:996-1011]
- **Treating `None` as false:** Constructed responses are not-yet-marked, not wrong. [VERIFIED: runtime.py:120-130]
- **Combining Anki and itembank counts:** They represent distinct scheduling owners. [VERIFIED: surfaces/day.py:370-395]

## Initial Formula and Settings Contract

Use a one-profile, transparent initial model; do not add competing profiles until actual evidence shows a need. [ASSUMED]

1. `unknown`: fewer than `min_settled_attempts` settled outcomes for an objective, or no objective evidence. Pending events do not satisfy the minimum. [ASSUMED]
2. `weak`: enough settled outcomes and recent settled accuracy below `weak_accuracy`. [ASSUMED]
3. `mastered`: enough settled outcomes, recent accuracy at/above `mastery_accuracy`, and at least `mastery_successes` confirmed successes across distinct local days. [ASSUMED]
4. `at-risk`: at least one prior confirmed success, no later confirming evidence, and elapsed days above `at_risk_after_days`; it is a retention flag, not a predicted failure. [VERIFIED: .planning/phases/10-retention-pacing-trends/10-CONTEXT.md]
5. `due`: a labeled recommendation when the state is weak/at-risk or the configured objective review interval has elapsed since its latest settled evidence. [ASSUMED]
6. `stable`: enough settled evidence but none of the above escalation/reduction states. [ASSUMED]

Recommended conservative defaults are `min_settled_attempts=3`, `weak_accuracy=0.60`, `mastery_accuracy=0.85`, `mastery_successes=3`, `at_risk_after_days=28`, and bounded weight multipliers `0.75..1.25`. These are explicit starting assumptions, not evidence-backed universal cutoffs; expose them in schema with bounds and provenance. [ASSUMED]

For each ordinary objective, form `raw = 1 + weak_boost + due_boost + at_risk_boost - mastery_reduction`, clamp it to the configured multiplier range, then normalize across currently eligible objectives. Cap the absolute change from the prior snapshot. Exam requests receive no evidence-derived ordering change. [ASSUMED] The existing settings already reserve a bounded `selection_weights` object with exactly `"objective_miss_rate"`, `"difficulty_spread"`, and `"recency_decay"`; extend or reconcile it rather than creating a second recency control. [VERIFIED: schemas/settings.schema.json:26-62]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---|---|---|---|
| Evidence authority | Mutable mastery database | Append-only evidence plus disposable projection | Retractions and re-marking retain auditability. [VERIFIED: evidence.py:943-1011] |
| Manual-mark state | Separate pending ledger | `marks_by_event()` joined to live responses | Latest live mark is already the accepted correction model. [VERIFIED: evidence.py:1116-1137] |
| Anki scheduling | Card interval/ease writer | Existing read-only AnkiConnect count reader | Preserves Anki ownership and graceful degradation. [VERIFIED: surfaces/day.py:370-395] |
| Date arithmetic | String slicing / fixed 24-hour timestamps | `datetime.date` local-day boundary plus UTC-aware event parsing | Python documents aware datetimes for unambiguous instants. [CITED: https://docs.python.org/3/library/datetime.html] |

**Key insight:** This phase is an evidence projection and control signal, not a second scheduler. [ASSUMED]

## Common Pitfalls

### Pitfall 1: Snapshot drift
**What goes wrong:** The page shows a due count derived before an append but a selection trace after it. [ASSUMED]

**How to avoid:** Materialize one snapshot marker containing cutoff, event count, log bytes/hash-or-sequence, filters, local-day zone, and window; render every claim from it. [ASSUMED]

### Pitfall 2: Pending work contaminates mastery
**What goes wrong:** A short answer waiting for a person looks incorrect or correct before a mark. [ASSUMED]

**How to avoid:** Count it for the daily cap only; use the latest live mark for mastery. [VERIFIED: runtime.py:120-130] [VERIFIED: evidence.py:1116-1137]

### Pitfall 3: Cap bypass becomes persistent
**What goes wrong:** A UI toggle silently suppresses the cap forever. [ASSUMED]

**How to avoid:** Require an explicit override argument/action, attach it to one launch/session, append an auditable event, and never persist it in settings. [VERIFIED: .planning/phases/10-retention-pacing-trends/10-CONTEXT.md]

### Pitfall 4: Local-day ambiguity
**What goes wrong:** UTC timestamps around midnight are counted in the wrong learner day. [ASSUMED]

**How to avoid:** Make the local-day timezone/boundary an input to the snapshot and include it in provenance; retain evidence timestamps as UTC-aware instants. [CITED: https://docs.python.org/3/library/datetime.html]

### Pitfall 5: Reimplementing selection
**What goes wrong:** Day/report chooses items separately from the selector and traces cannot explain the choice. [ASSUMED]

**How to avoid:** Phase 10 passes only weights plus snapshot to Phase 7's pure selector. [VERIFIED: .planning/phases/10-retention-pacing-trends/10-CONTEXT.md]

## Code Examples

### Live evidence query with correct retraction semantics
```python
# Source: existing evidence.py contract
rows = evidence.objective_history(log, objective, subject=subject, since=window_start)
```
`objective_history()` is specified to return live matching response events, use the index when possible, and fall back to an equivalent live scan. [VERIFIED: evidence.py:613-650]

### Separate Anki signal
```python
# Source: existing surfaces/day.py contract
counts, deck_names = anki_read(decks)
# Render counts[deck] as "Anki: due/new"; never add it to itembank due objectives.
```
The existing reader returns `(due, new)` per configured deck or `(None, None)` when Anki is unavailable. [VERIFIED: surfaces/day.py:370-395]

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|---|---|---|---|
| Tick-derived day lane load | Evidence-derived subject pacing | Phase 10 | `day` load reflects recorded attempts, not checkboxes. [ASSUMED] |
| Inline session shuffle | Phase 7 pure selector seam | Phase 7 | Phase 10 must weight the selector, not bypass it. [VERIFIED: surfaces/session.py:54-84] |

**Deprecated/outdated:** Treating a raw JSONL line count as learner history is invalid because retractions are compensating events. [VERIFIED: evidence.py:943-1011]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|---|---|---|
| A1 | The recommended numeric defaults are appropriate starting points. | Initial Formula | Over/under-scheduling; mitigate by bounds and visible provenance. |
| A2 | A snapshot should include a local-day zone/boundary field. | Architecture Patterns | Midnight pacing disagreement. |
| A3 | Lesson completion needs a new or confirmed evidence integration seam for SCHED-04. | Open Questions | Queue may lack a reliable entry event. |
| A4 | `retention.py` is the best new module name/boundary. | Recommended Project Structure | Low; can be renamed before implementation. |

## Open Questions — RESOLVED during planning

1. **What exact evidence event proves a lesson was completed for SCHED-04?**
   - What we know: Existing response events expose objective, timestamp, score, and `review_state`; current event types are `"response"`, `"retraction"`, `"mark"`, and `"day_tick"`. [VERIFIED: evidence.py:35-43] [VERIFIED: evidence.py:371-395]
   - What's unclear: No read source established a lesson-completion event or lesson/objective mapping.
   - Recommendation: Plan a small additive, versioned completion/review-queue event only after Phase 3 defines the lesson contract; do not infer completion from a page view. [ASSUMED]
   - **RESOLVED — planning lock (2026-08-08):** Plan 10-02 adds explicit `itembank lesson BANK --ref HEADING --complete`. Phase 3's `model.parse_lesson`, `model.lesson_slug`, and item `lesson_slug` resolve the heading to sorted unique namespaced objectives; the action appends one versioned `lesson_complete` event only through `evidence.append_event`. A view, render, or scroll writes nothing. `retention.py` consumes the captured live event, derives `next_review_date` from bounded `lesson_review_after_days`, carries the snapshot claim into the queue row/reason, and loses the row on a fresh capture after compensating retraction. No queue store or inferred completion is introduced. [LOCKED: 10-02-PLAN.md]
2. **How will Phase 7 expose the explicit history/weight seam?**
   - What we know: Its locked context calls for `select(questions, spec, history) -> (items, trace)` and Phase 10 weights. [VERIFIED: .planning/phases/07-selection-engine/07-CONTEXT.md]
   - What's unclear: `selection.py` is not present in the current worktree. [VERIFIED: filesystem check 2026-08-08]
   - Recommendation: Make the Phase 10 plan depend on the finalized Phase 7 public signature and trace schema; do not guess a parallel interface. [ASSUMED]
   - **RESOLVED — planning lock (2026-08-08):** Phase 7 plan 07-06 owns `selection.select(questions, spec, history) -> (items, trace)` and its selection event. Plan 10-03 preserves all three-argument callers and adds only optional keyword-only `retention_context=None`; `surfaces.session` captures evidence server-side and passes the normalized bounded objective map plus snapshot, while `selection.select` remains the sole item chooser and records component influence/snapshot in its existing trace/event. Practice/remediation consume the context, diagnostic preserves Phase 7 coverage policy, and exam ignores it. No parallel selector, client-supplied weights, or mutable weight cache is introduced. [LOCKED: 07-06-PLAN.md, 10-03-PLAN.md]

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|---|---|---:|---|---|
| Python | derivation and tests | ✓ | 3.13.5 local; 3.11 CI | CI baseline is 3.11. [VERIFIED: .github/workflows/ci.yml:10-12] |
| Anki Desktop + AnkiConnect | optional due/new signal | ✗ not probed as service | — | Omit counts with existing explanatory note. [VERIFIED: surfaces/day.py:778-781] |
| Git | optional current day evidence | ✓ | 2.54.0 | Existing surface degrades to no touched-file evidence. [VERIFIED: surfaces/day.py:403-419] |

**Missing dependencies with no fallback:** None. [VERIFIED: surfaces/day.py:370-395]

**Missing dependencies with fallback:** AnkiConnect is optional and already degrades. [VERIFIED: surfaces/day.py:778-781]

## Validation Architecture

### Test Framework
| Property | Value |
|---|---|
| Framework | Standalone stdlib Python roundtrip scripts. [VERIFIED: .github/workflows/ci.yml:69-70] |
| Config file | none |
| Quick run command | `python tests/retention_roundtrip.py` [ASSUMED] |
| Full suite command | `for t in tests/*.py; do python "$t" || exit 1; done` [VERIFIED: .github/workflows/ci.yml:69-70] |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|---|---|---|---|---|
| SCHED-01 | objective due state/provenance from synthetic live events | unit/roundtrip | `python tests/retention_roundtrip.py` | ❌ Wave 0 |
| SCHED-02 | per-subject local-day cap, block, scoped override event | integration | `python tests/retention_roundtrip.py` | ❌ Wave 0 |
| SCHED-03 | separate optional Anki signal; no write API | integration | `python tests/retention_roundtrip.py` | ❌ Wave 0 |
| SCHED-04 | completed lesson enters transparent review queue | integration | `python tests/retention_roundtrip.py` | ❌ Wave 0 |
| TREND-01 | bounded normalized weights passed to selector seam | unit | `python tests/retention_roundtrip.py` | ❌ Wave 0 |
| TREND-02 | day load derives from evidence and re-cut reason | integration | `python tests/retention_roundtrip.py` | ❌ Wave 0 |
| TREND-03 | weekly series, pending/hints, report twins | integration | `python tests/retention_roundtrip.py` | ❌ Wave 0 |
| TREND-04 | prior success then silence becomes at-risk | unit | `python tests/retention_roundtrip.py` | ❌ Wave 0 |
| TREND-05 | every row/weight has same snapshot provenance | unit | `python tests/retention_roundtrip.py` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `python tests/retention_roundtrip.py` [ASSUMED]
- **Per wave merge:** full CI-equivalent test loop. [VERIFIED: .github/workflows/ci.yml:69-70]
- **Phase gate:** full suite green and a manual `day --check` / report snapshot inspection. [ASSUMED]

### Wave 0 Gaps
- [ ] `tests/retention_roundtrip.py` — synthetic UTC/local-day data, retractions, marks, pending, no-evidence, bounded updates, and provenance.
- [ ] Report fixture with multiple objectives and week boundaries.
- [ ] Lesson-completion evidence fixture after SCHED-04 seam is resolved.

## Security Domain

### Applicable ASVS Categories
| ASVS Category | Applies | Standard Control |
|---|---|---|
| V2 Authentication | no | Local single-user tool; no auth scope. [VERIFIED: itembank.py:39-40] |
| V3 Session Management | yes | Identifier-addressed sessions; reject client path fields. [VERIFIED: surfaces/daemon.py:680-760] |
| V4 Access Control | yes | Daemon resolves only scanned bank stems/session IDs. [VERIFIED: surfaces/daemon.py:763-813] |
| V5 Input Validation | yes | Existing schema validator plus bounded settings and typed API input. [VERIFIED: surfaces/settings.py:86-125] |
| V6 Cryptography | no | No new secrecy/cryptographic operation is in scope. [ASSUMED] |

### Known Threat Patterns for this stack
| Pattern | STRIDE | Standard Mitigation |
|---|---|---|
| Client uses a filesystem path in start/report request | Tampering | Preserve `API_FORBIDDEN_FIELDS` rejection and server-side paths. [VERIFIED: surfaces/daemon.py:680-813] |
| Crafted settings disables schedule bounds | Tampering | Add every new threshold to schema bounds; settings load validates known keys. [VERIFIED: surfaces/settings.py:86-125] |
| Retraction ignored in a trend | Integrity | Derive solely from `live_events()` / `objective_history()`. [VERIFIED: evidence.py:613-650] |
| Anki unavailable or returns an error | Availability | Preserve optional omission rather than blocking `day`. [VERIFIED: surfaces/day.py:370-395] |

## Sources

### Primary (HIGH confidence)
- In-repo source: `evidence.py`, `surfaces/day.py`, `surfaces/session.py`, `surfaces/daemon.py`, `schemas/settings.schema.json`, and CI workflow — current ownership, event, settings, route, and test contracts. [VERIFIED: source files opened this session]

### Secondary (MEDIUM confidence)
- [Python datetime documentation](https://docs.python.org/3/library/datetime.html) — aware/naive time semantics and ISO formatting. [CITED: https://docs.python.org/3/library/datetime.html]
- [AnkiConnect documentation](https://github.com/amikey/anki-connect) — deck discovery/read API. [CITED: https://github.com/amikey/anki-connect]
- [Kang et al. on spaced retrieval](https://pubmed.ncbi.nlm.nih.gov/24744260/) and [Rawson & Dunlosky on retrieval scheduling](https://pubmed.ncbi.nlm.nih.gov/21707204/) — support spacing but not a universal fitted formula. [CITED: https://pubmed.ncbi.nlm.nih.gov/24744260/] [CITED: https://pubmed.ncbi.nlm.nih.gov/21707204/]

### Tertiary (LOW confidence)
- No external package recommendations; numeric starting thresholds are explicitly assumptions.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — current project and CI contracts are direct source evidence.
- Architecture: HIGH — authoritative in-repo evidence/days/surface seams; MEDIUM for new module boundary.
- Pitfalls: MEDIUM — code contracts verify retraction/pending/Anki behaviors; snapshot and cutoff design is a new explicit recommendation.

**Research date:** 2026-08-08
**Valid until:** 2026-09-07 for in-repo contracts; reassess external AnkiConnect behavior before implementation.
