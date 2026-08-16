---
phase: 16C-strategies-notes-prototype-convergence
plan: 06
type: execute
wave: 3
depends_on: ["16C-02"]
files_modified:
  - evidence.py
  - notes.py
  - tests/note_promotion_roundtrip.py
autonomous: true
requirements: [NOTE-02, NOTE-03]
estimate:
  tokens: 75000
  raw_tokens: 75000
  tasks: 3
  confidence: low
must_haves:
  truths:
    - "The evidence store gains exactly two additive KNOWN_EVENT_TYPES members, activity_completed and activity_skipped, appended only through evidence.append_event, carrying at most a note ID reference and never note text; every other strategy event stays in the deletable note store."
    - "The additivity is proven, not promised: an evidence log written before 16C parses byte-identically and its captured view matches the baselines 16C-01 recorded, while a reader meeting an unknown event type still skip-and-warns."
    - "Source-backed review promotes one note as a cited derived copy with a derivation edge; the learner's original note is never mutated by acceptance, and an unreviewed note stays learner-private and non-authoritative forever by default."
    - "No silent path exists from a note to accepted source, lesson, key, score, or mastery: promotion requires an explicit reviewer acceptance, a keyed or factual claim without an accepted source blocks acceptance with the stated count, and a source conflict stops promotion with the locked sentence."
    - "A learner artifact carries a rubric and reads as pending evidence until a scripted human mark settles it; a non-human marker is refused by the shipped mark_event gate, and a model proposal settles nothing."
    - "Deletion removes the note and its private index and says honestly that evidence the runtime is required to keep is not affected."
  prohibitions:
    - statement: "Note text, learner wording, or selected content must never enter the append-only evidence log; the lifecycle event's key set is closed and contains no content-bearing field."
      status: kept
      verification: flagged-unverified
    - statement: "No personal note scorer: a draft question derived from a note runs normal bank lint, review, and runtime scoring, or it stays an unkeyed self-prompt; nothing here assigns a key or a score."
      status: kept
      verification: flagged-unverified
    - statement: "No second settlement mechanism: pending and settled states compose the shipped mark and mark_proposal machinery, and nothing else settles."
      status: kept
      verification: flagged-unverified
  artifacts:
    - "evidence.py KNOWN_EVENT_TYPES with exactly sixteen members, the two new ones commented with this plan number"
    - "notes.py gains strategy_lifecycle_event, request_review, review_promotion, delete_note, artifact_record, artifact_evidence_view, and the promotion, artifact, and deletion copy constants"
    - "tests/note_promotion_roundtrip.py green"
  key_links:
    - "strategy_lifecycle_event lives in notes.py and writes through evidence.append_event, the migrate.py precedent; evidence.py's only change is the two tuple members, so the one-writer discipline is structural."
    - "review_promotion's outcome vocabulary maps onto the reviewer-acceptance vocabulary (accept and decline onto applied and refused) per UI-SPEC D7, so no second review grammar exists for 14A journaling to reconcile later."
    - "artifact_evidence_view reads settlement only from mark events joined through marks_by_event; if it computed a verdict itself it would be a second settlement mechanism."
    - "The additivity check compares against the exact baseline lines recorded in 16C-PRECONDITION.md; a re-recorded baseline would make the proof circular."
---

<objective>
Close NOTE-02 and NOTE-03: the promotion and review contract that keeps note
error out of accepted truth, the learner-artifact pending-evidence record,
and the one additive evidence extension that carries strategy lifecycle
facts without carrying content.

Decisions already made, cited, and never re-derived here:

- **16C-DECISIONS.md `## D-16C-1`**: the evidence and note-state split, the
  two event types, the closed key set, EVENT_SCHEMA_VERSION unchanged.
- **16C-DECISIONS.md `## D7` (UI-SPEC)**: promotion reuses the
  reviewer-acceptance vocabulary; acceptance creates a cited derived copy
  with a derivation edge, never an in-place mutation; a decline records its
  reason and leaves the note unchanged.
- **16C-DECISIONS.md `## D16` (UI-SPEC)**: the delete confirmation states
  the evidence boundary honestly.
- **REQUIREMENTS.md NOTE-02 and NOTE-03** in full, including the degraded
  contracts: an unreviewed note stays learner-private and non-authoritative;
  unreviewed artifacts read as pending, never as settled mastery.
- **Shipped `evidence.mark_event`** (evidence.py:1416): the human-only
  marker gate; `mark_proposal` and `proposal_ref` as the
  advisory-not-settling channel. 16C composes these and builds no new
  settlement.
- **16C-UI-SPEC.md Copywriting Contract**: every promotion, artifact, and
  deletion string transcribed below, verbatim.

Purpose: the authority boundary of the whole notes feature, provable today.
Output: two additive event types with a byte-identical proof, one promotion
contract, one artifact record, one green test.
</objective>

<context>
@.planning/phases/16C-strategies-notes-prototype-convergence/16C-DECISIONS.md
@.planning/phases/16C-strategies-notes-prototype-convergence/16C-PRECONDITION.md
@.planning/phases/16C-strategies-notes-prototype-convergence/16C-UI-SPEC.md
@.planning/phases/16C-strategies-notes-prototype-convergence/16C-RESEARCH.md
@.planning/REQUIREMENTS.md
@evidence.py
@notes.py
@surfaces/migrate.py
@tests/evidence_roundtrip.py
@fixtures/note_strategy_corpus.py
</context>

## Artifacts this phase produces (plan 16C-06 share)

New symbols introduced by this plan, and by nothing earlier:

- `evidence.py`: the `KNOWN_EVENT_TYPES` members `"activity_completed"` and
  `"activity_skipped"`.
- `notes.py`: `STRATEGY_LIFECYCLE_EVENT_TYPES`, `PROMOTION_STATES`,
  `ARTIFACT_KINDS`, `PROMOTION_COPY`, `ARTIFACT_COPY`, `DELETE_COPY`,
  `strategy_lifecycle_event`, `request_review`, `review_promotion`,
  `delete_note`, `artifact_record`, `artifact_evidence_view`.
- `tests/note_promotion_roundtrip.py` and its `check_*` functions.

The phase-wide symbol union is repeated in `16C-01-PLAN.md`.

<tasks>

<task type="auto">
  <name>Task 1: two additive event types, proven additive</name>
  <files>evidence.py, notes.py, tests/note_promotion_roundtrip.py</files>
  <read_first>
- `evidence.py` lines 42 to 55: the per-plan comment convention above
  `KNOWN_EVENT_TYPES` and the tuple itself.
- `evidence.py` `append_event` (line 735), `events` (line 755, the
  skip-and-warn), `live_events` (line 1355), `capture_events` (line 1373),
  `new_event_id`, `utc_now`.
- `surfaces/migrate.py` lines 1 to 26: the one-writer rule and the
  builder-outside-evidence precedent this task copies.
- `16C-PRECONDITION.md`, the Additivity baseline section, all five recorded
  lines.
- `16C-DECISIONS.md` `## D-16C-1`.
  </read_first>
  <action>
1. In `evidence.py`, extend `KNOWN_EVENT_TYPES` with exactly two members,
   `"activity_completed"` and `"activity_skipped"`, appended at the end of
   the tuple, and extend the comment block above it with one sentence in the
   established shape: `"activity_completed" / "activity_skipped" by plan
   16C-06: strategy lifecycle facts carrying at most a note ID, never note
   content.` Change nothing else in `evidence.py`: no schema version bump
   (D-16C-1), no new function, no reader change.

2. In `notes.py`, add `import evidence` (the module now mirrors
   `subjects.py`'s import posture; it still imports no `runtime` and nothing
   from `surfaces/`). Add:

```
STRATEGY_LIFECYCLE_EVENT_TYPES = ("activity_completed", "activity_skipped")
```

   and `strategy_lifecycle_event(log, event_type, session_id, strategy_id,
   action_state, note_ref="")`:
   - Validates `event_type` against `STRATEGY_LIFECYCLE_EVENT_TYPES`,
     `strategy_id` against the four registry ids (validate against a local
     tuple constant equal to the registry ids; a comment names
     `strategies.STRATEGY_IDS` as the source of truth and 16C-09's tracer as
     the equality check, so notes.py does not import strategies),
     `action_state` against `STRATEGY_ACTION_STATES`, raising `ValueError`
     naming any unknown member.
   - Builds the event dict with exactly the keys `schema_version`
     (`evidence.EVENT_SCHEMA_VERSION`), `event_id` (`evidence.new_event_id()`),
     `event_type`, `ts` (`evidence.utc_now()`), `session_id`, `strategy_id`,
     `action_state`, `note_ref`, `dedupe_key` (a sha256 hex digest over
     `session_id|strategy_id|action_state|note_ref|event_type`), and no
     other key. A comment cites D-16C-1: no content-bearing field exists on
     this event, at most a note ID.
   - Appends through `evidence.append_event(log, event)` only, and returns
     its result unchanged (`recorded` or `already_recorded`).

3. Create `tests/note_promotion_roundtrip.py` in the shipped
   direct-execution shape with a local `fail(msg)`. First checks:
   - `check_lifecycle_event`: in a temp evidence log, append an
     `activity_completed` and an `activity_skipped` event; assert
     `append_event` reports `recorded`, an identical replay reports
     `already_recorded`, `live_events` yields both, and each stored event's
     key set is exactly the nine keys from step 2 (no content-bearing field:
     assert `learner_wording` and any key containing `wording`, `text`, or
     `content` is absent). Assert unknown `event_type`, `strategy_id`, and
     `action_state` each raise `ValueError`.
   - `check_additivity`: recompute the three fixture SHA-256 lines and the
     two captured-view lines with the exact commands from 16C-01 step 10 and
     assert every value equals the baseline recorded in
     `16C-PRECONDITION.md` (read the file, parse the five lines, compare).
     Then prove the degrade path still holds: write a temp log containing
     one event whose `event_type` is `"not_a_type"` and assert
     `list(evidence.events(path))` is empty while the process prints a
     `warn` line containing `unknown event_type`, the D-09 skip-and-warn.
   - `main()` prints `NOTE PROMOTION: 2 passed, 0 failed` for now.

4. Run:

```
python tests/note_promotion_roundtrip.py
python tests/evidence_roundtrip.py
```

   Expected: final line `NOTE PROMOTION: 2 passed, 0 failed`, exit 0; then
   exit 0 (the shipped evidence suite is the regression net for the tuple
   change).

   No em dash characters in any file this task writes.
  </action>
  <verify>
  <automated>python tests/note_promotion_roundtrip.py && python tests/evidence_roundtrip.py</automated>
Expected: `NOTE PROMOTION: 2 passed, 0 failed` then exit 0 from the shipped
suite. The degraded state this task proves is the old-build path: a reader
meeting an unknown event type skip-and-warns rather than failing, and the
pre-16C logs parse to byte-identical captured views against the recorded
baselines.
  </verify>
  <acceptance_criteria>
- `KNOWN_EVENT_TYPES` has exactly sixteen members, the two new ones last,
  with the plan-numbered comment; `git diff evidence.py` shows only the
  tuple and comment hunk.
- The lifecycle event's stored key set is exactly the nine named keys, with
  no content-bearing field.
- Every additivity baseline value matches `16C-PRECONDITION.md` exactly.
- `python tests/evidence_roundtrip.py` exits 0 unchanged.
- No file this task writes contains an em dash character, verified with the
  `chr(0x2014)` form.
  </acceptance_criteria>
  <reversibility rating="one-way">An event type, once written into a real
  append-only log, exists forever; that is why the key set is closed, the
  content prohibition is structural, and the additivity is proven against
  pre-change baselines before anything ships.</reversibility>
  <done>Strategy lifecycle facts flow through the one evidence writer as two
  additive, content-free event types, with the old world provably
  unchanged.</done>
</task>

<task type="auto">
  <name>Task 2: the promotion and review contract (NOTE-02)</name>
  <files>notes.py, tests/note_promotion_roundtrip.py</files>
  <read_first>
- `16C-UI-SPEC.md`, the Promotion Review Flow Contract in full, and the
  Copywriting Contract rows for review, conflict, accept, decline, and
  badges.
- `16C-DECISIONS.md` `## D7` and `## D3`.
- `16C-RESEARCH.md`, the report 12 section 7.2 eight-point
  silent-promotion-prevention list quoted under NOTE-02.
- `notes.py` as it stands after Task 1.
  </read_first>
  <action>
1. Add to `notes.py`, transcribed verbatim from the UI-SPEC:

```
PROMOTION_STATES = ("private", "review_requested", "accepted", "declined")
PROMOTION_COPY = {
    "private_badge": "Private note. Not part of the course.",
    "requested_badge": "Review requested. Awaiting source-backed review.",
    "request_control": "Request review for course use",
    "flow_heading": "Review for course use",
    "source_check": "Every keyed or factual claim needs an accepted source. {N} claims have no accepted source yet.",
    "conflict_stop": "A source conflict was found. Promotion is stopped until the conflict is resolved.",
    "accept_control": "Accept into course",
    "accept_confirmation": "Accept this note into the course? The original note stays yours; the course gets a cited copy with its derivation recorded.",
    "decline_control": "Decline",
    "decline_reason_label": "Reason (recorded with the decision)",
    "accepted_badge": "Accepted into the course on {date}.",
    "declined_badge": "Not accepted: {reason}. Your note is unchanged.",
}
```

2. Add `request_review(note)`: returns a copy of the note with a
   `promotion_state` of `"review_requested"`; every note without the field
   reads `"private"`; nothing else changes; a comment cites the NOTE-02
   degraded contract and D3 (the state changes the badge and nothing else).

3. Add `review_promotion(note, claims, accepted_sources,
   conflicts, decision, reviewer, reason="")`:
   - `claims` is a list of claim dicts each carrying `text` and
     `source_id` (empty when unsupported); `accepted_sources` is the set of
     accepted source ids; `conflicts` is a list of source-conflict
     descriptions.
   - Gate 1: `unsupported = [c for c in claims if c["source_id"] not in
     accepted_sources]`; when non-empty, acceptance is blocked: return
     `{"outcome": "blocked", "copy": PROMOTION_COPY["source_check"]}` with
     `{N}` replaced by the count. A comment cites UI-SPEC gate 9: never a
     silently disabled accept.
   - Gate 2: when `conflicts` is non-empty, return
     `{"outcome": "conflict_stop", "copy":
     PROMOTION_COPY["conflict_stop"]}`; promotion never proceeds by picking
     the note, the newest source, or a model output silently.
   - `decision="accept"` (only reachable past both gates): returns
     `{"outcome": "applied", "derived": <a NEW note record via note_record
     with status "learner_accepted", derivations [{"from_note_revision":
     original revision_id}], owner unchanged>, "note": <the original,
     untouched>, "badge": accepted badge with the date substituted}`. The
     original note object is asserted unchanged by identity comparison in
     the test; acceptance is a distinct derived artifact with a derivation
     edge, never an in-place mutation.
   - `decision="decline"`: requires a non-empty `reason` (ValueError
     otherwise, because the reason field is required by the UI-SPEC), and
     returns `{"outcome": "refused", "note": <untouched>, "badge": declined
     badge with the reason substituted}`.
   - The outcome vocabulary `("blocked", "conflict_stop", "applied",
     "refused")` maps accept and decline onto the journal's applied and
     refused (D7); a comment says so.
   - `reviewer` must be a non-empty human name string; a model may annotate
     (a labeled `"Generated synthesis"` string may ride in an optional
     `annotations` argument) but never decides: there is no code path from
     an annotation to an outcome.

4. Extend `tests/note_promotion_roundtrip.py`:
   - `check_promotion_gates`: an unsupported claim blocks with the exact
     sentence at N=2; a conflict stops with the exact sentence; both leave
     the note in `review_requested`.
   - `check_promotion_accept_decline`: a fully sourced, conflict-free note
     accepts: the outcome is `applied`, the derived record carries status
     `learner_accepted` and the derivation edge naming the original
     revision, and the original note dict is unchanged (compare against a
     deep copy taken before). A decline with reason `"needs a citation"`
     returns `refused` with the badge
     `Not accepted: needs a citation. Your note is unchanged.` and the
     note unchanged. A decline without a reason raises.
   - `check_unreviewed_stays_private` (the NOTE-02 fixture's second half):
     build two notes from the corpus; promote one through the full path;
     assert the second, never submitted for review, still reads
     `promotion_state` `"private"`, badge
     `Private note. Not part of the course.`, and appears in no derived
     artifact, no accepted output, and no evidence event (scan the temp log
     used in check_lifecycle_event's pattern: zero events reference its
     note_id).
   - Update `main()` to run five checks and print
     `NOTE PROMOTION: 5 passed, 0 failed`.

5. Run:

```
python tests/note_promotion_roundtrip.py
```

   Expected: final line `NOTE PROMOTION: 5 passed, 0 failed`, exit 0.

   No em dash characters in any file this task writes.
  </action>
  <verify>
  <automated>python tests/note_promotion_roundtrip.py</automated>
Expected: final line `NOTE PROMOTION: 5 passed, 0 failed`, exit 0. The
degraded state this task proves is the unreviewed default: a note nobody
reviews stays learner-private and non-authoritative forever, with zero paths
into accepted truth or evidence.
  </verify>
  <acceptance_criteria>
- `python tests/note_promotion_roundtrip.py` exits 0 with final line
  `NOTE PROMOTION: 5 passed, 0 failed`.
- Every promotion copy string matches the UI-SPEC verbatim.
- Acceptance produces a derived record with a derivation edge and never
  mutates the original, asserted by deep-copy comparison.
- The unsupported-claim and conflict gates block with their exact sentences.
- No file this task writes contains an em dash character, verified with the
  `chr(0x2014)` form.
  </acceptance_criteria>
  <reversibility rating="costly">The promotion outcome vocabulary is the
  seam 14A journaling reconciles with; renaming an outcome after records
  exist is a migrate operation.</reversibility>
  <done>Promotion is explicit, source-backed, reviewer-settled, and
  derivation-edged; unreviewed notes are structurally inert.</done>
</task>

<task type="auto">
  <name>Task 3: the learner artifact (NOTE-03) and honest deletion</name>
  <files>notes.py, tests/note_promotion_roundtrip.py</files>
  <read_first>
- `evidence.py` `mark_event` (line 1416) in full, including the
  `marker="human"` ValueError and `proposal_ref`; `mark_proposal_event` if
  present near it; `marks_by_event`.
- `16C-UI-SPEC.md`, the Learner-Artifact Record View Contract table and the
  Copywriting Contract rows for the artifact and deletion.
- `16C-DECISIONS.md` `## D16`.
- `REQUIREMENTS.md` NOTE-03.
  </read_first>
  <action>
1. Add to `notes.py`, transcribed verbatim:

```
ARTIFACT_KINDS = ("proof", "program", "diagram", "explanation", "project",
                  "observation")
ARTIFACT_COPY = {
    "pending_badge": "Pending review",
    "pending_explainer": "Recorded as pending by itembank. A reviewer settles this. A model never settles it.",
    "proposal_line": "A model has proposed a mark. It settles nothing until a reviewer accepts it.",
    "settled_line": "Reviewed by {reviewer} on {date}.",
}
DELETE_COPY = {
    "confirmation": "Delete this note? This removes the note and its private index. Evidence the runtime is required to keep is not affected.",
    "confirm_button": "Delete note",
}
```

2. Add `artifact_record(kind, course_id, objective_ids, rubric,
   content_path="")`: validates `kind` against `ARTIFACT_KINDS` (ValueError
   naming unknown kinds); `rubric` is a list of criterion strings (may be
   empty; an artifact without a rubric still records, per the UI-SPEC empty
   state); returns a dict with `artifact_id` (`new_note_id()`), `kind`,
   `course_id`, `objective_ids`, `rubric`, `content_path`, `submitted_at`.
   The artifact file itself is learner-owned and lives in the note root;
   this record is its machine descriptor.

3. Add `artifact_evidence_view(artifact, response_event_id, log)`:
   - Reads marks joined to `response_event_id` through
     `evidence.marks_by_event(log)` and any proposals referencing it.
   - Returns `{"state": "pending" | "settled", "badge": ..., "lines":
     [...]}`: pending until a human mark settles; a present proposal adds
     `ARTIFACT_COPY["proposal_line"]` while state stays `"pending"`; a
     settling human mark yields `"settled"` with
     `ARTIFACT_COPY["settled_line"]` substituted. Per-criterion states
     render separately and are never summed into a number or grade (the
     GRAPH-03 no-aggregate rule applied locally; comment says so).
   - The function computes no verdict: settlement is read from mark events
     only.

4. Add `delete_note(sidecar, note_id)`: returns a new sidecar with the note
   removed and a `deleted` tombstone status recorded per NOTE_STATUS, plus
   the confirmation copy pair for the surface. Docstring cites D16 and
   report 12 section 11.2: deletion covers the note and its private index;
   lifecycle facts already in the append-only evidence store are not clawed
   back, and the copy says so rather than implying total erasure.

5. Extend `tests/note_promotion_roundtrip.py`:
   - `check_artifact_pending` (the NOTE-03 fixture): build a fictional
     proof artifact with a three-criterion rubric from the corpus's math
     subject; in a temp log, append a `response` event for it (shape from
     `tests/evidence_roundtrip.py`), then:
     - assert the view reads `pending` with the exact pending badge and
       explainer;
     - append a `mark_proposal` event referencing the response and assert
       the view still reads `pending` and now carries the exact proposal
       line;
     - assert `evidence.mark_event(..., marker="model")` raises
       `ValueError` (the shipped gate, re-proven here at the artifact
       boundary);
     - append a human `mark_event` with a per-criterion rubric and assert
       the view reads `settled` with
       `Reviewed by {reviewer} on {date}.` substituted, and that no
       aggregate number appears in any line (scan for the percent
       character and digit-slash-digit totals across criteria).
   - `check_delete_honesty`: delete a note from a written document; assert
     the note is gone from the re-read sidecar, the confirmation string
     matches verbatim, and the temp evidence log's bytes are unchanged by
     the deletion.
   - Update `main()` to run seven checks and print
     `NOTE PROMOTION: 7 passed, 0 failed`.

6. Run:

```
python tests/note_promotion_roundtrip.py
python tests/evidence_roundtrip.py
python itembank.py guard .
```

   Expected: `NOTE PROMOTION: 7 passed, 0 failed`, exit 0; exit 0;
   `0 offending files`.

   No em dash characters in any file this task writes.
  </action>
  <verify>
  <automated>python tests/note_promotion_roundtrip.py && python tests/evidence_roundtrip.py</automated>
Expected: `NOTE PROMOTION: 7 passed, 0 failed` then exit 0. The degraded
state this task proves is pending-forever: an artifact nobody reviews reads
pending with the exact explainer, a model proposal changes nothing, and only
a human mark settles.
  </verify>
  <acceptance_criteria>
- `python tests/note_promotion_roundtrip.py` exits 0 with final line
  `NOTE PROMOTION: 7 passed, 0 failed`.
- The artifact view is pending until a human mark, a proposal never settles,
  and `marker="model"` raises through the shipped gate.
- No aggregate number renders across rubric criteria.
- Deletion removes the note from the sidecar, leaves the evidence log
  byte-identical, and carries the honest confirmation verbatim.
- No file this task writes contains an em dash character, verified with the
  `chr(0x2014)` form.
  </acceptance_criteria>
  <reversibility rating="reversible">Composition over shipped settlement
  machinery plus copy constants; nothing new settles and nothing durable
  changes shape.</reversibility>
  <done>A learner artifact is pending until a human settles it, and deletion
  is honest about what it can and cannot remove.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| note store to evidence store | Deletable learner content must never cross into the append-only log; only content-free lifecycle facts may. |
| learner claim to accepted truth | Promotion is the only crossing, and it requires sources, no conflicts, and a human reviewer. |
| model proposal to settlement | A proposal is advisory forever; only the human-marker gate settles. |
| deletion promise to append-only reality | Copy that promised total erasure would be a lie; the honest boundary is stated. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-16C-06-01 | Information Disclosure | note text entering the append-only evidence log | high | mitigate | The lifecycle event's key set is closed at nine content-free keys, asserted per stored event; the builder validates and builds the whole dict itself. |
| T-16C-06-02 | Elevation of Privilege | a note laundering a key, score, or mastery through promotion | high | mitigate | The unsupported-claim gate blocks with a count, the conflict gate stops, acceptance requires a named human reviewer, and no code path exists from an annotation to an outcome. |
| T-16C-06-03 | Spoofing | a model verdict read as settlement | high | mitigate | Settlement is read only from mark events; mark_event's marker gate raises on non-human markers, re-proven at the artifact boundary. |
| T-16C-06-04 | Tampering | the evidence format drifting under the tuple change | high | mitigate | The byte and captured-view baselines from 16C-PRECONDITION.md are asserted equal, and the shipped evidence suite runs in both tasks' verify. |
| T-16C-06-05 | Repudiation | deletion silently failing to state what remains | medium | mitigate | The confirmation copy is locked to the honest sentence and the test asserts the log is byte-identical across a deletion. |
| T-16C-06-06 | Tampering | supply chain: a third-party dependency introduced by this plan | high | mitigate | None is added; stdlib only. Per PLANNING-DIRECTIVES section 4a, any future dependency is vendored at a pinned version with a recorded checksum and a named license review. |
</threat_model>

<out_of_scope>
Refused by this plan, by name:

- No promotion of note content into lesson or bank files; acceptance
  produces a derived note record with a derivation edge, and turning that
  into course material is the authoring path's job under its own review.
- No draft-question generation and no keying: a note-derived question is a
  future authoring flow that runs normal bank lint and runtime scoring, or
  stays an unkeyed self-prompt; nothing here touches keys.
- No `EVENT_SCHEMA_VERSION` bump and no reader change in `evidence.py`.
- No queued-model-input store: report 12 section 11.2's deletion scope names
  it, and none exists in this codebase to delete.
- No review UI, route, or CLI command; the flow is contract plus fixtures,
  rendered by 17A.
- No second settlement store, no rubric arithmetic, no artifact grading.
</out_of_scope>

<flagged_assumptions>
- **`marks_by_event` and the proposal event builder are shipped surface**
  (evidence.py's mark section); if the landed names differ from what
  `read_first` finds, the executor uses the landed names and records the
  deviation, because the contract (pending until human mark; proposal never
  settles) does not depend on the helper's name.
- **The strategy-id validation tuple in notes.py duplicates four strings
  from strategies.py by design**, to keep notes.py free of a strategies
  import; the 16C-09 tracer asserts the two tuples equal so drift is caught
  at the phase gate.
- **The corpus provides claims and sources as synthetic data**; accepted
  sources are fixture ids, not real source records, until 14B wiring, and
  the test names them as stand-ins.
</flagged_assumptions>

<summary_obligations>
`16C-06-SUMMARY.md` records: the final line of every verify command with
actual stdout; the additivity comparison table (baseline value beside found
value, all five lines); the stored lifecycle event's exact key set; the
promotion outcomes exercised with their rendered badges quoted; the artifact
view's three states with their lines quoted; the deletion honesty check
result; and any deviation from this plan with its reason.
</summary_obligations>

<output>
Create
`.planning/phases/16C-strategies-notes-prototype-convergence/16C-06-SUMMARY.md`
when done.
</output>
