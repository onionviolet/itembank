---
phase: 16C-strategies-notes-prototype-convergence
plan: 04
type: execute
wave: 2
depends_on: ["16C-01"]
files_modified:
  - progress_claims.py
  - tests/progress_claim_roundtrip.py
autonomous: true
requirements: [GRAPH-03]
estimate:
  tokens: 65000
  raw_tokens: 65000
  tasks: 2
  confidence: low
must_haves:
  truths:
    - "Progress is reported only through the independent nine-field claim tuple (claim kind, scope and version, numerator, denominator or indeterminate, rule, snapshot or window, settled or pending or unknown, authority, uncertainty), and the seven dimensions render as seven separate rows that are never merged."
    - "A missing denominator reports indeterminate with the locked sentence, never an invented percent and never an empty bar."
    - "A pending prose mark stays pending in its own count, never folded into passes or failures; a version-split objective reads unknown on the new identity with the locked sentence."
    - "No aggregate completion, mastery, or readiness score appears anywhere in any rendered output, and Retrievability is never surfaced as a percentage: the rendered text contains no percent character at all."
    - "The per-objective display is the D-14A-3 self-adjustable fill state: discrete blocks that move up and down as evidence and retention change, carrying the locked legend, never a continuous bar and never a permanent grade."
    - "The claim builder reads evidence only through the one captured snapshot handed to it; it opens no file and never reads the log directly, so appending after capture cannot change claims already returned."
  prohibitions:
    - statement: "No single aggregate number, score, ring, or summary bar may be computed or rendered across dimensions; a summary may link to component claims, never replace them (Do-Not-Re-Open row 1)."
      status: kept
      verification: flagged-unverified
    - statement: "Viewed, clicks, elapsed time, streaks, percentile, engagement, note count, highlight count, and note length must never feed a claim as mastery (Do-Not-Re-Open row 2)."
      status: kept
      verification: flagged-unverified
    - statement: "Evidence must never transfer automatically across a renamed, split, or merged objective; unmigrated evidence reads unknown on the new identity (Do-Not-Re-Open row 9)."
      status: kept
      verification: flagged-unverified
  artifacts:
    - "progress_claims.py with CLAIM_DIMENSIONS, DIMENSION_LABELS, MEMBERSHIP_CLASSES, RETENTION_STATE_WORDS, the locked copy constants, ARIA_CONTRACT, claim, claim_text, claims_from_events, fill_state, render_claims_text"
    - "tests/progress_claim_roundtrip.py green with the missing-denominator, pending-mark, version-split, and no-aggregate checks"
  key_links:
    - "claims_from_events must consume a snapshot produced by evidence.capture_events and passed in as an argument; the moment it opens the log itself, two readers exist and a mid-render append can split the claims (the capture_events docstring names this exact hazard)."
    - "The claim tuple's shape is what the 16C-09 tracer and the eventual 17A rendering both read; a field added later is additive, a field renamed is breaking."
    - "render_claims_text is the no-aggregate enforcement point: the test scans its output, so every rendered surface must route through it or the scan proves nothing."
---

<objective>
Build the GRAPH-03 honest-progress contract: the nine-field claim tuple, the
seven separate dimensions, the indeterminate and unknown paths, the
D-14A-3 fill state, and the text rendering that provably contains no
aggregate and no percent.

Decisions already made, cited, and never re-derived here:

- **16C-DECISIONS.md `## D9` (UI-SPEC)**: one claim row per dimension,
  numerator and denominator always in text, separate denominators for
  required, required-choice, and enrichment, the discrete-block fill state
  with its fixed legend, no aggregate anywhere, Retrievability never a
  percentage.
- **16C-DECISIONS.md `## D10` (UI-SPEC)**: the ARIA contract, recorded here
  as data for 17A.
- **D-14A-3 (DECISIONS-PRE-14A-2026-08-14.md)**: the per-objective,
  self-adjustable fill state shown as filled-in blocks, able to move up and
  down as evidence and retention change; not a permanent knowledge claim.
- **REQUIREMENTS.md GRAPH-03** in full, including: separate denominators;
  adding enrichment can never lower completion; formal completion persists
  while retention may decay; degraded contract "a missing denominator
  reports indeterminate, never an invented percent."
- **16C-UI-SPEC.md Progress Comprehension Display Contract and Copywriting
  Contract**: every locked string transcribed below.
- **Shipped precedent `surfaces/retention_view.py`**: render-only functions
  over already-derived dicts, no arithmetic in the renderer, `unknown`
  instead of a fabricated number.

Purpose: the progress display 16C-09's tracer asserts and 17A renders, built
so dishonesty is structurally unavailable.
Output: one pure claim module and one green test.
</objective>

<context>
@.planning/phases/16C-strategies-notes-prototype-convergence/16C-DECISIONS.md
@.planning/phases/16C-strategies-notes-prototype-convergence/16C-UI-SPEC.md
@.planning/phases/16C-strategies-notes-prototype-convergence/16C-RESEARCH.md
@.planning/REQUIREMENTS.md
@.planning/DECISIONS-PRE-14A-2026-08-14.md
@evidence.py
@retention.py
@surfaces/retention_view.py
@tests/retention_roundtrip.py
</context>

## Artifacts this phase produces (plan 16C-04 share)

New symbols introduced by this plan, and by nothing earlier:

- `progress_claims.py`: `CLAIM_FIELDS`, `CLAIM_DIMENSIONS`,
  `DIMENSION_LABELS`, `MEMBERSHIP_CLASSES`, `RETENTION_STATE_WORDS`,
  `INDETERMINATE_COPY`, `PENDING_COPY`, `VERSION_SPLIT_COPY`,
  `FILL_STATE_LEGEND`, `ARIA_CONTRACT`, `claim`, `claim_text`,
  `claims_from_events`, `fill_state`, `render_claims_text`.
- `tests/progress_claim_roundtrip.py` and its `check_*` functions.

The phase-wide symbol union is repeated in `16C-01-PLAN.md`.

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: the claim tuple, the seven dimensions, and the honest paths</name>
  <files>progress_claims.py, tests/progress_claim_roundtrip.py</files>
  <behavior>
    - `claim("count", "emt_respiratory.obj.1@v1", 9, 12, "required activities submitted", "as of snapshot s1", "settled", "evidence store", "")` returns a dict with exactly the nine `CLAIM_FIELDS` keys.
    - `claim_text` of that claim is `9 of 12 required activities submitted`.
    - `claim(..., numerator=3, denominator=None, ...)` renders
      `Indeterminate: {scope name} has no fixed denominator.` with the scope
      name substituted, and its `denominator` field reads `"indeterminate"`.
    - A pending claim of 2 renders `2 pending review`.
    - A version-split objective claim with settlement `"unknown"` renders
      `Unknown for this version of {objective name}. Earlier evidence stays
      with the earlier version.` with the name substituted.
    - `claim` with a settlement outside `("settled", "pending", "unknown")`
      raises `ValueError` naming it.
    - `fill_state` returns an integer count of filled blocks out of a stated
      total, and feeding it weaker retention evidence returns a lower count
      than stronger evidence: it moves both directions.
  </behavior>
  <read_first>
- `16C-DECISIONS.md` `## D9` and `## D10`, in full.
- `16C-UI-SPEC.md`, the Progress Comprehension Display Contract, all seven
  structure items and the ARIA rules.
- `surfaces/retention_view.py` lines 1 to 30, the render-only and
  unknown-not-fabricated precedent.
- `evidence.py` `capture_events` (line 1373) docstring, the snapshot
  contract `claims_from_events` must honor.
- `retention.py` lines 1 to 45, for the shipped retention state derivation
  the retention dimension summarizes.
  </read_first>
  <action>
1. Create `progress_claims.py` at the repository root, importing nothing
   beyond the standard library. It must not import `runtime` and must not
   open any file: every function is pure over its arguments (the
   selection.py everything-arrives-as-an-argument shape). Module docstring:
   progress is claims, never a score; the runtime and course records own
   their dimensions (GRAPH-03 authority split); no aggregate exists here and
   none may be added.

2. Define, transcribed verbatim where quoted:

```
CLAIM_FIELDS = ("claim_kind", "scope", "numerator", "denominator", "rule",
                "window", "settlement", "authority", "uncertainty")
CLAIM_DIMENSIONS = ("design_coverage", "participation", "settled_evidence",
                    "current_retention", "formal_completion",
                    "selected_enrichment", "open_uncertainty")
DIMENSION_LABELS = {
    "design_coverage": "Design coverage",
    "participation": "Participation",
    "settled_evidence": "Settled evidence",
    "current_retention": "Current retention",
    "formal_completion": "Formal completion",
    "selected_enrichment": "Selected enrichment",
    "open_uncertainty": "Open uncertainty",
}
MEMBERSHIP_CLASSES = ("required", "required_choice", "enrichment")
RETENTION_STATE_WORDS = ("due", "stable", "weak", "at risk", "unknown")
INDETERMINATE_COPY = "Indeterminate: {scope} has no fixed denominator."
PENDING_COPY = "{n} pending review"
VERSION_SPLIT_COPY = "Unknown for this version of {objective}. Earlier evidence stays with the earlier version."
FILL_STATE_LEGEND = "Filled blocks show current standing for this objective. They move up and down as evidence and retention change. This is not a permanent grade."
```

3. Define `claim(claim_kind, scope, numerator, denominator, rule, window,
   settlement, authority, uncertainty)`:
   - Validates `settlement` against `("settled", "pending", "unknown")`,
     raising `ValueError` naming an unknown value.
   - A `denominator` of `None` is stored as the string `"indeterminate"`.
   - Returns a dict with exactly the nine `CLAIM_FIELDS` keys.

4. Define `claim_text(c, scope_name="")`:
   - Determinate settled claim: `"{numerator} of {denominator} {rule}"`, the
     UI-SPEC pattern, where `rule` is the specific metric name; a comment
     states the metric name is never the bare word progress.
   - Indeterminate denominator: `INDETERMINATE_COPY` with `{scope}` replaced
     by `scope_name` or the claim's scope.
   - Pending: `PENDING_COPY` with `{n}` replaced by the numerator.
   - Unknown: `"Unknown"` plus `": " + uncertainty` when the claim carries a
     stated reason; a version-split claim (see `claims_from_events`) uses
     `VERSION_SPLIT_COPY`.

5. Define `claims_from_events(snapshot, course_records)`:
   - `snapshot` is the tuple `evidence.capture_events` returns, passed in by
     the caller; `course_records` is a dict of synthetic course-record
     stand-ins (named as such in the docstring per 16C-RESEARCH Assumption
     A4: the 14B graph feeds this for real once wired, and the signature
     does not change).
   - Returns a dict over `CLAIM_DIMENSIONS`, one list of claims per
     dimension, computed only from the arguments:
     - `design_coverage` from `course_records` (authority: course records).
     - `participation` from lifecycle facts in the snapshot (event types
       `activity_completed` and `activity_skipped` counted separately;
       docstring notes these types land in plan 16C-06 and are counted here
       by name only).
     - `settled_evidence` from response events joined with settled marks;
       responses whose mark is absent contribute to a pending claim, never
       to passes or failures.
     - `current_retention` as a state distribution over
       `RETENTION_STATE_WORDS` with the snapshot window named; never a
       probability or percentage.
     - `formal_completion` from `course_records` predicates; persists
       regardless of retention decay.
     - `selected_enrichment` with its own denominator; a comment cites
       GRAPH-03: adding enrichment can never lower a required denominator's
       completion.
     - `open_uncertainty` counting pending marks and unknown states.
   - Membership classes keep separate denominators: a required claim, a
     required-choice claim, and an enrichment claim are three claims, never
     summed.
   - A `course_records` entry carrying `"version_split": True` for an
     objective yields an unknown claim for the new identity using
     `VERSION_SPLIT_COPY`, and the old identity's evidence is never
     transferred.

6. Define `fill_state(objective_id, settled_count, retention_state)`:
   returns `{"objective_id": ..., "filled": <int 0..4>, "total": 4,
   "legend": FILL_STATE_LEGEND}` where `filled` derives from settled
   evidence stepped down by weaker retention states (`"due"`, `"weak"`,
   `"at risk"` each cap or reduce it) so the same objective can move down as
   retention decays and up as it recovers. Blocks are discrete integers,
   never a float, never a percent.

7. Define `ARIA_CONTRACT`, a dict recording D10 as data for 17A:
   determinate rows use `role=progressbar` with `aria-valuemin`,
   `aria-valuemax`, `aria-valuenow`, and `aria-valuetext` set to the full
   claim text; the fill state uses `aria-valuetext` only; indeterminate
   rows use an indeterminate progressbar with visible text and never an
   unexplained spinner; state changes announce once through the single
   `role=status` region.

8. Create `tests/progress_claim_roundtrip.py` in the shipped
   direct-execution shape with a local `fail(msg)`. Checks:
   - `check_claim_shape`: every behavior-block assertion; the nine keys are
     exactly `CLAIM_FIELDS`; unknown settlement raises.
   - `check_missing_denominator`: `None` denominator renders the
     indeterminate sentence and stores `"indeterminate"`.
   - `check_pending_and_version_split`: a synthetic snapshot with one
     unmarked short response yields a pending claim rendering
     `1 pending review`; a version-split objective yields the unknown
     sentence and zero transferred evidence.
   - `check_fill_state`: moves up with more settled evidence and down when
     retention weakens; values are ints within 0..4; legend matches
     verbatim.
   - `main()` prints `PROGRESS CLAIMS: 4 passed, 0 failed`.

9. Run:

```
python tests/progress_claim_roundtrip.py
```

   Expected: final line `PROGRESS CLAIMS: 4 passed, 0 failed`, exit 0.

   No em dash characters in any file this task writes.
  </action>
  <verify>
  <automated>python tests/progress_claim_roundtrip.py</automated>
Expected: final line `PROGRESS CLAIMS: 4 passed, 0 failed`, exit 0. The
degraded state this task proves is the missing denominator: an absent
denominator renders the locked indeterminate sentence, never an invented
percent and never an empty bar.
  </verify>
  <acceptance_criteria>
- `python tests/progress_claim_roundtrip.py` exits 0 with final line
  `PROGRESS CLAIMS: 4 passed, 0 failed`.
- The nine claim fields, seven dimensions, three membership classes, and
  five retention state words match this plan exactly.
- `progress_claims.py` opens no file and imports neither `runtime` nor
  `evidence` (the snapshot arrives as an argument), asserted via ast in the
  test.
- Every locked copy string matches the UI-SPEC verbatim.
- No file this task writes contains an em dash character, verified with the
  `chr(0x2014)` form.
  </acceptance_criteria>
  <reversibility rating="costly">The claim tuple and dimension ids are what
  the 16C-09 tracer and 17A rendering read; renaming a field after the
  freeze is a breaking change.</reversibility>
  <done>Progress exists only as separate honest claims with locked copy for
  every degraded case.</done>
</task>

<task type="auto">
  <name>Task 2: the text rendering that provably carries no aggregate</name>
  <files>progress_claims.py, tests/progress_claim_roundtrip.py</files>
  <read_first>
- `16C-UI-SPEC.md`, Progress Comprehension Display Contract structure items
  1, 2, 3, and 7, and the ARIA rules.
- `16C-RESEARCH.md` Pitfall 4, the aggregate-percent failure this task's
  scan exists to catch.
- `progress_claims.py` as written by Task 1.
  </read_first>
  <action>
1. Add `render_claims_text(claims_by_dimension, fill_states)` to
   `progress_claims.py`: returns one plain-text block, the contract-level
   projection 17A later styles. Layout, exactly:
   - One region per dimension in `CLAIM_DIMENSIONS` order, headed by its
     `DIMENSION_LABELS` value, each claim on its own line via `claim_text`.
   - Dimensions never merge; no totals row, no summary line, no overall
     heading beyond the per-dimension labels.
   - Retention renders as its state distribution: each of the five state
     words with its count and the snapshot window.
   - Each fill state renders as `filled`-many filled-block glyphs
     (`#` in this text projection) and the remainder as `.`, followed by
     the legend once at the end of the objectives region.
   - The function computes nothing: it formats already-derived claims (the
     retention_view discipline; state that in the docstring).

2. Extend `tests/progress_claim_roundtrip.py`:
   - `check_no_aggregate`: build the full synthetic scenario (all seven
     dimensions populated, one missing denominator, one pending mark, one
     version-split objective, three membership classes, two fill states),
     render it, and assert over the rendered text:
     - The percent character does not appear anywhere in the output, so
       neither an aggregate percent nor a Retrievability percentage can
       render.
     - Each of the seven `DIMENSION_LABELS` values appears exactly once.
     - No line contains more than one dimension's label, and no line
       matches the pattern of a total across dimensions (assert the label
       words `overall` and `readiness` are absent from the output,
       lowercase comparison).
     - The indeterminate sentence, the pending sentence, and the
       version-split sentence each appear exactly once.
     - The required and enrichment claims render with different
       denominators, and the required denominator is unchanged by the
       enrichment claim's presence (render twice, with and without the
       enrichment claim, and assert the required line is byte-identical).
   - `check_aria_contract`: `ARIA_CONTRACT` records `aria-valuetext` for
     the fill state without `aria-valuenow`, and the indeterminate rule
     names visible text.
   - Update `main()` to run six checks and print
     `PROGRESS CLAIMS: 6 passed, 0 failed`.

3. Run:

```
python tests/progress_claim_roundtrip.py
python itembank.py guard .
```

   Expected: final line `PROGRESS CLAIMS: 6 passed, 0 failed`, exit 0;
   `0 offending files`.

   No em dash characters in any file this task writes.
  </action>
  <verify>
  <automated>python tests/progress_claim_roundtrip.py</automated>
Expected: final line `PROGRESS CLAIMS: 6 passed, 0 failed`, exit 0. The
degraded state this task proves is honesty under sparse data: the full
scenario renders every degraded case with its locked sentence and the scan
finds no percent character and no aggregate row anywhere in the output.
  </verify>
  <acceptance_criteria>
- `python tests/progress_claim_roundtrip.py` exits 0 with final line
  `PROGRESS CLAIMS: 6 passed, 0 failed`.
- The rendered output contains no percent character, all seven labels
  exactly once, and the three degraded sentences exactly once each.
- The required denominator is byte-identical with and without enrichment.
- `render_claims_text` performs no arithmetic beyond formatting counts it
  was handed.
- No file this task writes contains an em dash character, verified with the
  `chr(0x2014)` form.
  </acceptance_criteria>
  <reversibility rating="reversible">A text projection; 17A restyles it
  freely while the scan keeps the honesty rules enforced.</reversibility>
  <done>The whole display renders from claims alone, and dishonesty (a
  percent, an aggregate, a merged dimension) fails a test by name.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| evidence snapshot to claims | Claims must derive from one captured snapshot; a second reader lets a mid-render append split the story. |
| claims to rendered text | The rendering is where an aggregate or a percent would sneak in; the scan guards this boundary. |
| objective identity to evidence | A version split must never inherit evidence automatically. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-16C-04-01 | Repudiation | an aggregate score or invented percent rendering as fact | high | mitigate | render_claims_text is the single projection and check_no_aggregate scans its output for the percent character, duplicate labels, and total rows. |
| T-16C-04-02 | Tampering | a second evidence reader inside the claim builder | medium | mitigate | claims_from_events takes the captured snapshot as an argument; the test asserts via ast that progress_claims.py imports no evidence module and opens no file. |
| T-16C-04-03 | Repudiation | pending prose folded into pass or fail counts | medium | mitigate | Unmarked responses contribute only to pending claims, asserted by check_pending_and_version_split. |
| T-16C-04-04 | Spoofing | evidence silently transferred across a version-split objective | high | mitigate | The version-split path yields an unknown claim with the locked sentence and the test asserts zero transfer. |
| T-16C-04-05 | Tampering | supply chain: a third-party dependency introduced by this plan | high | mitigate | None is added; stdlib only. Per PLANNING-DIRECTIVES section 4a, any future dependency is vendored at a pinned version with a recorded checksum and a named license review. |
</threat_model>

<out_of_scope>
Refused by this plan, by name:

- No HTML, route, CLI command, or pixel rendering; the text projection is
  the 16C contract and 17A owns the visual form, including block glyphs and
  chip visuals.
- No real course records; the course-record argument is a named synthetic
  stand-in until 14B wiring, per 16C-RESEARCH Assumption A4, and the
  signature is built so wiring changes no caller.
- No retention arithmetic: the retention dimension summarizes states the
  shipped retention module derives; this plan recomputes nothing.
- No Anki, streak, points, target, or loss-state data anywhere
  (retention_view's own D-19/D-20 rule carried forward).
- No new evidence event types; participation counts the two D-16C-1 types
  by name and plan 16C-06 ships them.
</out_of_scope>

<flagged_assumptions>
- **The fill state's block total of 4 is this plan's concrete choice.**
  D-14A-3 fixes discrete blocks, self-adjustable, with the legend; it does
  not fix a count. Four keeps the text projection legible; 17A may rescale
  the visual count without touching the contract, and the test asserts
  integers and both-direction movement, not the total.
- **The participation dimension counts event types that ship in 16C-06.**
  Until that plan lands, the test feeds synthetic events carrying those
  type strings; the tracer in 16C-09 re-runs the check over real appended
  events.
</flagged_assumptions>

<summary_obligations>
`16C-04-SUMMARY.md` records: the final line of every verify command with
actual stdout; the rendered full-scenario text block quoted in full; the
fill-state values produced by the up and down cases; confirmation every
locked sentence matched the UI-SPEC verbatim; and any deviation from this
plan with its reason.
</summary_obligations>

<output>
Create
`.planning/phases/16C-strategies-notes-prototype-convergence/16C-04-SUMMARY.md`
when done.
</output>
