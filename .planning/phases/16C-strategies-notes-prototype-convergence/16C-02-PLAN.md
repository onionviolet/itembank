---
phase: 16C-strategies-notes-prototype-convergence
plan: 02
type: execute
wave: 2
depends_on: ["16C-01"]
files_modified:
  - fixtures/note_strategy_corpus.py
  - notes.py
  - schemas/note.schema.json
  - tests/note_schema_roundtrip.py
  - surfaces/cli.py
autonomous: true
requirements: [NOTE-01]
estimate:
  tokens: 75000
  raw_tokens: 75000
  tasks: 3
  confidence: low
must_haves:
  truths:
    - "The four-subject synthetic corpus exists as a fixture builder whose content is fictional by construction, deterministic (building twice produces identical bytes), and written only to caller-supplied directories, never into the repository tree."
    - "A note record carries every NOTE-01 field: note ID, ownership, course and objective relation, multi-selector anchor with quoted-context hash, source or lesson revision, authorship type, strategy, wording, privacy, revision, and optional promotion or review state, validated against closed vocabularies that raise on an unknown member."
    - "A note whose anchor is invalidated by a lesson revision stays attached to its objective with the broken selector flagged through one of the four closed relocation states, and relocated_probable is never auto-applied."
    - "Authored pre-highlighting produces zero evidence events and zero note ownership: the authored record carries authorship type authored, an empty owner, and driving the authored path leaves a temporary evidence log byte-identical."
    - "All three capture paths produce the identical multi-selector target record; the interaction path is never recorded as a difference in the note."
    - "A stray note document pasted into the repository outside fixtures/ fails itembank guard through one additive corpus-marker check, and the repository itself stays guard-green."
    - "The note document is coherent Markdown plus a JSON sidecar, written with the compare-and-swap discipline, and readable through exactly one reader function."
  prohibitions:
    - statement: "No second parser: the sidecar is stdlib json, the note Markdown is read by one reader, and no new markdown grammar engine exists."
      status: kept
      verification: flagged-unverified
    - statement: "A probable relocation must never be auto-applied; resolve_anchor returns a state and candidates and mutates nothing."
      status: kept
      verification: flagged-unverified
    - statement: "Real learner or course content must never enter this repository; every fixture is generated fictional content and the guard run is the enforcement backstop."
      status: kept
      verification: flagged-unverified
  artifacts:
    - "fixtures/note_strategy_corpus.py with SEED, SUBJECTS, build_subject_bank, build_all, typed_relations, build_note_set, revise_lesson"
    - "notes.py with the closed vocabularies, note_record, target_record, resolve_anchor, authored_prehighlight, write_note_document, read_note_document, and the capture-panel copy constants"
    - "schemas/note.schema.json inside schema_validate.py's supported keyword subset"
    - "tests/note_schema_roundtrip.py green"
    - "surfaces/cli.py guard with one additive note-document corpus marker"
  key_links:
    - "resolve_anchor's quoted-context hash must use one hashing helper shared with the fixture generator, or the fixture and the resolver disagree about what identical content means and every relocation fixture is vacuous."
    - "The anchor stable_id is a heading slug from model.lesson_slug today; the D-14A-2 component-ID upgrade is a recorded integration seam (D-16C-7), so target_record must keep stable_id scheme-agnostic and no 16C code may parse meaning out of it."
    - "The guard marker must land inside the existing corpus-marker function, not as a second walker, or two guards exist and drift."
    - "notes.py imports model for lesson_slug and collapse only; importing runtime would put a scorer within reach of learner data and importing surfaces would invert the tier rule evidence.py:12-16 states."
---

<objective>
Build the phase's shared synthetic corpus and the learner-note schema: the
NOTE-01 record, its closed vocabularies, its multi-selector provenance, its
relocation resolution, and its guard backstop.

Decisions already made, cited, and never re-derived here:

- **16C-DECISIONS.md `## D-16C-2`**: note document format (Markdown plus JSON
  sidecar, `_notes/` default root, compare-and-swap writes, one reader).
- **16C-DECISIONS.md `## D-16C-3`**: module and file names used here.
- **16C-DECISIONS.md `## D-16C-6` and `## D15`**: strategy-action-state
  naming; the Activity capitalization rule appears in every docstring that
  touches either vocabulary.
- **16C-DECISIONS.md `## D-16C-8`**: every closed vocabulary, verbatim.
- **16C-DECISIONS.md `## D6`, `## D13`, `## D14`**: relocation chips with
  probable-never-auto-applied, three equivalent capture paths producing one
  target record, authored pre-highlighting as orientation with zero events
  and zero ownership (clause C107).
- **16C-UI-SPEC.md Copywriting Contract**: every capture-panel string
  transcribed below, verbatim.
- **REQUIREMENTS.md NOTE-01**, including its degraded contract: "a stale
  anchor keeps the note attached to its objective and flags the broken
  selector."

Purpose: every later 16C plan consumes this corpus and this schema; nothing
downstream invents a vocabulary or a fixture subject.
Output: one fixture builder, one schema module, one published JSON schema,
one green test, one guard marker.
</objective>

<context>
@.planning/phases/16C-strategies-notes-prototype-convergence/16C-DECISIONS.md
@.planning/phases/16C-strategies-notes-prototype-convergence/16C-UI-SPEC.md
@.planning/phases/16C-strategies-notes-prototype-convergence/16C-RESEARCH.md
@.planning/phases/16C-strategies-notes-prototype-convergence/16C-PATTERNS.md
@.planning/REQUIREMENTS.md
@model.py
@runtime.py
@evidence.py
@schema_validate.py
@surfaces/cli.py
@tests/subject_loop_roundtrip.py
@fixtures/subject_loop_emt.md
</context>

## Artifacts this phase produces (plan 16C-02 share)

New symbols introduced by this plan, and by nothing earlier:

- `fixtures/note_strategy_corpus.py`: `SEED`, `SUBJECTS`,
  `build_subject_bank`, `build_all`, `typed_relations`, `build_note_set`,
  `revise_lesson`.
- `notes.py`: `NOTE_SCHEMA_VERSION`, `NOTES_DIRNAME`, `EPISTEMIC_ROLES`,
  `STRATEGY_ACTION_STATES`, `RELOCATION_STATES`, `NOTE_STATUS`,
  `TARGET_KINDS`, `AUTHORSHIP_TYPES`, `ANCHOR_STATE_LABELS`,
  `PROBABLE_CONTROLS`, `CAPTURE_COPY`, `hash_quoted_context`, `new_note_id`,
  `note_record`, `target_record`, `resolve_anchor`, `authored_prehighlight`,
  `write_note_document`, `read_note_document`.
- `schemas/note.schema.json`.
- `tests/note_schema_roundtrip.py` and its `check_*` functions.
- One additive marker branch in `surfaces/cli.py`'s corpus-marker check.

The phase-wide symbol union is repeated in `16C-01-PLAN.md`.

<tasks>

<task type="auto">
  <name>Task 1: the four-subject synthetic corpus builder</name>
  <files>fixtures/note_strategy_corpus.py</files>
  <read_first>
- `16C-RESEARCH.md`, "Recommended Project Structure" and Pattern 6, plus the
  ROADMAP freeze-gate paragraph naming the four subjects.
- `fixtures/subject_loop_emt.md` in full, as the shipped synthetic-bank shape
  (preamble, `## LESSON`, `## TERMS`, items) this builder generates.
- `model.py` `parse_lesson` (line 469) and `parse_terms` (line 625)
  docstrings, for the exact shapes the generated banks must satisfy.
- `16C-DECISIONS.md` `## D-16C-7`, the trio input contract: typed relations
  are explicit fixture data, never a new inline grammar.
  </read_first>
  <action>
1. Create `fixtures/note_strategy_corpus.py`, a stdlib-only module with a
   docstring stating: every string in this file is fictional, invented for
   fixtures, and no line derives from any real course, book, or learner;
   banks are written only to caller-supplied directories, never into the
   repository tree. Include the D-16C-6 naming sentence: "strategy-action
   states are learner task states (lowercase activity); the Activity view
   (capitalized) is the 16B IA jobs area and is not this module's subject."

2. Define `SEED = 1603` and
   `SUBJECTS = ("emt_respiratory", "math_linear_system", "cs_loop_invariant", "history_conflicting_accounts")`.
   Content is literal string constants; `SEED` seeds any `random.Random` use
   so building twice is byte-identical.

3. Define `build_subject_bank(subject, dest_dir)`: writes
   `<dest_dir>/<subject>_bank.md` and returns its path. Each bank carries, in
   order: a title line naming it fictional (for example
   `# Fictional respiratory assessment drill (synthetic fixture)`), a
   `## LESSON` section with at least four `### ` headings each carrying two
   to four sentences of invented prose and at least one `[[term]]` reference,
   a `## TERMS` table with at least four rows, and at least two parseable
   questions (one `mc`, one `short`) with invented stems. The four subjects
   are, per the ROADMAP freeze gate: a fictional EMT respiratory assessment,
   a fictional mathematics linear system, a fictional CS loop invariant with
   an off-by-one, and a fictional history topic where two invented diarists
   give conflicting primary accounts of the same event. Content rules stated
   inline: no em dash characters, no real names, no real textbook wording.
   These banks are note and strategy fixtures, not authored courseware; they
   must parse (`model.load` returns at least 2 items, `parse_lesson` at least
   4 headings, `parse_terms` at least 4 terms) but are not required to pass
   `itembank lint`, and the module docstring says so.

4. Define `typed_relations(subject)`: returns a list of explicit typed edges
   `(source_slug, relation_type, target_slug)` over that subject's heading
   and term slugs, at least four edges per subject, using only the relation
   types `("part_of", "causes", "contrasts_with", "requires")`. This is the
   trio's declared relation data per D-16C-7; no inline grammar.

5. Define `build_note_set(subject, headings)`: returns at least five
   synthetic learner-note dicts for that subject, each naming an
   `epistemic_role` from the seven-role vocabulary, invented
   `learner_wording`, an anchor heading slug from `headings`, and one
   objective id string of the form `<subject>.obj.<n>`. At least one note per
   subject uses each of `quote`, `learner_claim`, and `learner_question`.

6. Define `revise_lesson(dest_dir, subject)`: rewrites the already-built bank
   file replacing exactly one lesson heading's title and body with different
   invented text (so both its slug and its content hash change) and returns
   the replaced heading's original slug. This is the NOTE-01
   anchor-invalidation fixture.

7. Define `build_all(dest_dir)`: builds all four banks and returns a manifest
   dict `{subject: path}`.

8. Prove determinism and cleanliness. Run:

```
python -c "import tempfile, filecmp, os; import sys; sys.path.insert(0, '.'); from fixtures import note_strategy_corpus as c; a = tempfile.mkdtemp(); b = tempfile.mkdtemp(); ma = c.build_all(a); mb = c.build_all(b); same = all(open(ma[s], 'rb').read() == open(mb[s], 'rb').read() for s in c.SUBJECTS); print('deterministic', same, len(ma))"
python itembank.py guard .
```

   Expected: `deterministic True 4`, then a final line `0 offending files`.
  </action>
  <verify>
  <automated>python -c "import tempfile, sys; sys.path.insert(0, '.'); import model; from fixtures import note_strategy_corpus as c; d = tempfile.mkdtemp(); m = c.build_all(d); [print(s, len(model.load(m[s])), len(model.parse_lesson(m[s])['headings']), len(model.parse_terms(m[s])['terms']), len(c.typed_relations(s))) for s in c.SUBJECTS]; print('corpus ok')" && python itembank.py guard .</automated>
Expected: four lines each showing at least 2 items, at least 4 headings, at
least 4 terms, at least 4 relations, then `corpus ok`, then `0 offending
files`. The degraded state this task proves is repository cleanliness: the
builder writes only to the caller's temp directory and the guard stays green
with the builder committed.
  </verify>
  <acceptance_criteria>
- `build_all` returns four paths; every bank parses with at least 2 items, 4
  headings, 4 terms; every subject has at least 4 typed relations.
- Building twice into two directories produces byte-identical files.
- `revise_lesson` changes exactly one heading's slug and content hash,
  verified in Task 2's relocation checks.
- `python itembank.py guard .` reports `0 offending files`.
- No file this task writes contains an em dash character, verified with the
  `chr(0x2014)` form from plan 16C-01.
  </acceptance_criteria>
  <reversibility rating="reversible">A fixture builder; deleting it removes
  test data only.</reversibility>
  <done>Four fictional subjects exist as deterministic, guard-green fixture
  builders every later 16C plan consumes.</done>
</task>

<task type="auto">
  <name>Task 2: notes.py, the NOTE-01 record, vocabularies, provenance, and relocation</name>
  <files>notes.py, schemas/note.schema.json, tests/note_schema_roundtrip.py</files>
  <read_first>
- `16C-DECISIONS.md` `## D-16C-1`, `## D-16C-2`, `## D-16C-8`, `## D6`,
  `## D13`, `## D14`, in full.
- `16C-UI-SPEC.md`, the Note Capture Panel Contract and the Copywriting
  Contract rows for capture, anchor states, and the privacy line.
- `runtime.py` `write_session` (line 1430), the atomic write shape to copy.
- `model.py` `lesson_slug` (line 447) and `collapse` (line 444).
- `schema_validate.py` `SUPPORTED` (line 27) and `validate` (line 120).
- `evidence.py` lines 12 to 16 area docstring, the runtime-tier placement
  rule notes.py copies.
- `tests/subject_loop_roundtrip.py` lines 1 to 45, the direct-execution test
  shell with a local `fail(msg)`.
  </read_first>
  <action>
1. Create `notes.py` at the repository root, a runtime-tier peer that imports
   `hashlib`, `json`, `os`, `uuid`, and `model` (for `lesson_slug` and
   `collapse` only). It must not import `runtime`, and nothing from
   `surfaces/`. Module docstring: notes are learner-owned artifacts, never
   annotations baked into accepted lessons; the runtime settles nothing here;
   plus the D-16C-6 Activity naming sentence.

2. Define the closed vocabularies exactly as D-16C-8 locks them:

```
NOTE_SCHEMA_VERSION = 1
NOTES_DIRNAME = "_notes"
EPISTEMIC_ROLES = ("quote", "learner_claim", "learner_question",
                   "learner_example", "calculation", "diagram",
                   "accepted_reference_link")
STRATEGY_ACTION_STATES = ("not_started", "draft", "completed",
                          "skipped_optional", "equivalent_completed",
                          "needs_review")
RELOCATION_STATES = ("resolved", "relocated_exact", "relocated_probable",
                     "orphaned")
NOTE_STATUS = ("draft", "learner_accepted", "disputed", "superseded",
               "deleted")
TARGET_KINDS = ("source", "lesson_step", "media", "item_public", "concept")
AUTHORSHIP_TYPES = ("learner", "authored")
```

3. Define the locked copy constants, transcribed verbatim from the UI-SPEC
   Copywriting Contract (no em dashes, no rewording):

```
ANCHOR_STATE_LABELS = {
    "resolved": "Anchored",
    "relocated_exact": "Anchor moved with the lesson",
    "relocated_probable": "Anchor probably moved: review needed",
    "orphaned": "Anchor lost. Still linked to {objective name}.",
}
PROBABLE_CONTROLS = ("Confirm new location", "Keep unanchored")
CAPTURE_COPY = {
    "affordance": "Add a note",
    "anchor_prompt": "What is this note about?",
    "anchor_choices": ("This selection", "This block", "This whole section",
                       "This objective (no anchor)"),
    "keyboard_picker": "Use arrow keys to choose a block, then Enter to select. Shift plus arrows extends the selection.",
    "role_prompt": "This note is:",
    "role_choices": ("A quotation", "My claim", "My question", "My example",
                     "A calculation", "A diagram",
                     "A link to an accepted reference"),
    "privacy_line": "Private to you. Nothing is shared unless you request review.",
    "save": "Save to my notes",
    "submit": "Submit activity",
    "submit_clarifier": "Submitting shares this response with the course. Your saved notes stay private.",
    "saved_status": "Saved to your notes.",
    "draft_restored": "Your draft note was restored.",
    "empty_state": "No notes yet for this course. Add one from any lesson in Learn.",
}
```

   The seven `role_choices` map positionally to `EPISTEMIC_ROLES`; state that
   in a comment.

4. Define `hash_quoted_context(text)`: returns
   `"sha256:" + hashlib.sha256(model.collapse(text).encode("utf-8")).hexdigest()[:16]`,
   the one hashing helper both this module and the trio use for
   quoted-context identity. Docstring: change detection, never security
   (ID-02).

5. Define `new_note_id()` returning `uuid.uuid4().hex[:16]`, the
   `model.new_item_id` shape.

6. Define `target_record(target_kind, stable_id, content_fingerprint,
   locator, quoted_context_hash)`: validates `target_kind` against
   `TARGET_KINDS` (raise `ValueError("unknown target kind: %r" % kind)` on
   anything else) and returns a dict with exactly those five keys. No field
   records which capture path produced it; a comment cites D13: pointer,
   keyboard, and structured-choice capture produce this identical record.

7. Define `note_record(course_id, objective_ids, epistemic_role,
   learner_wording, targets, strategy_id="", authorship="learner",
   owner="local", privacy_scope="private", status="draft")`: validates
   `epistemic_role`, `authorship`, and `status` against their vocabularies
   (ValueError naming the unknown member) and returns a dict with exactly the
   keys `note_id`, `note_document_id`, `revision_id`, `owner`,
   `privacy_scope`, `course_id`, `objective_ids`, `strategy_id`,
   `epistemic_role`, `learner_wording`, `targets`, `derivations`, `status`,
   `authorship`, `created_at`, `updated_at`. `derivations` starts empty;
   `note_document_id` and `revision_id` are `new_note_id()` values;
   timestamps are ISO-8601 UTC strings.

8. Define `resolve_anchor(target, headings)`: `headings` is
   `model.parse_lesson(path)["headings"]`. Behavior, exactly:
   - If a heading's `slug` equals `target["stable_id"]` and
     `hash_quoted_context(that heading["body"])` equals
     `target["quoted_context_hash"]`, return
     `{"state": "resolved", "candidates": [that slug]}`.
   - Else if exactly one heading's body hash equals the target's
     quoted-context hash, return
     `{"state": "relocated_exact", "candidates": [that slug]}`.
   - Else if a heading's slug matches but its body hash differs, or two or
     more headings' body hashes match, return
     `{"state": "relocated_probable", "candidates": [every matching slug, slug match first]}`.
   - Else return `{"state": "orphaned", "candidates": []}`.
   The function reads its arguments and mutates nothing; a comment cites D6
   and Do-Not-Re-Open row 5: `relocated_probable` requires review and is
   never auto-applied; only `relocated_exact` may be re-anchored by a caller,
   through the atomic writer, and even that is a caller decision.

9. Define `authored_prehighlight(region_label, target)`: returns
   `{"authorship": "authored", "owner": "", "region_label": region_label,
   "target": target}`. Docstring cites C107 and D14: authored emphasis is
   sparse orientation with one concise screen-reader label per region; it
   produces zero evidence events and zero note ownership, and this module
   gives it no path into a note document's learner notes.

10. Define `write_note_document(dir_path, course_id, markdown, sidecar)` and
    `read_note_document(dir_path, course_id)`:
    - Paths: `<dir_path>/notes.md` and `<dir_path>/notes.md.json`.
    - `sidecar` is `{"schema_version": NOTE_SCHEMA_VERSION,
      "note_document_id": ..., "course_id": ..., "notes": [note records]}`.
    - Write each file to `<path>.tmp` then `os.replace`, the
      `runtime.write_session` shape, sidecar first, markdown second.
    - `read_note_document` is the one reader: returns
      `{"markdown": ..., "sidecar": ...}` or `None` when absent; a partial
      `.tmp` beside a valid pair is ignored, so an interrupted write leaves
      the last accepted state readable.

11. Create `schemas/note.schema.json` describing one sidecar document, using
    only keywords from `schema_validate.SUPPORTED` plus annotations:
    `type: object`, `required` `["schema_version", "note_document_id",
    "course_id", "notes"]`, `additionalProperties: false`, `notes` an array
    of note objects whose `epistemic_role`, `status`, and `authorship` use
    `enum` with the exact vocabulary members, targets validated with the five
    target keys. Confirm it self-checks:

```
python schema_validate.py --all schemas
```

    Expected: exit 0.

12. Create `tests/note_schema_roundtrip.py` in the shipped direct-execution
    shape (shebang, `ROOT` sys.path insert, local `fail(msg)` printing
    `FAIL: ` and exiting 1). Checks, each its own function:
    - `check_vocabularies`: the seven tuples equal the D-16C-8 values
      exactly; `note_record` and `target_record` raise `ValueError` naming an
      unknown role, status, authorship, and target kind.
    - `check_capture_copy`: every `CAPTURE_COPY` value and
      `ANCHOR_STATE_LABELS` value equals the UI-SPEC string verbatim
      (assert the exact strings from step 3).
    - `check_target_identity`: three target records built to simulate the
      three capture paths over the same block are `==` identical.
    - `check_roundtrip`: build a corpus bank in a temp dir
      (`note_strategy_corpus.build_subject_bank`), anchor five notes from
      `build_note_set` to its headings via `target_record` with
      `hash_quoted_context` over each heading body, write and read the note
      document, assert the read sidecar equals the written one and
      `schema_validate.validate` passes it against `schemas/note.schema.json`.
    - `check_relocation_states`: drive all four states through
      `resolve_anchor`: untouched heading resolves; a heading renamed in the
      file with identical body reads `relocated_exact`; `revise_lesson`
      produces `orphaned` or `relocated_probable` for the replaced heading's
      note (assert the state is one of those two and NOT `resolved`, and that
      the note record itself still carries its `objective_ids` unchanged,
      which is NOTE-01's degraded contract); a duplicated body across two
      headings reads `relocated_probable` with two candidates.
    - `check_atomic_write`: write a document, then plant a corrupt
      `notes.md.json.tmp` beside it; `read_note_document` still returns the
      last accepted sidecar.
    - `check_authored_zero`: create a temp evidence log path, record its
      byte size (0 or absent), call `authored_prehighlight` for two regions,
      assert the record's `owner` is the empty string, its `authorship` is
      `authored`, and the temp log is still absent or byte-identical: zero
      events.
    - `main()` prints `NOTE SCHEMA: 7 passed, 0 failed` and exits 0.

13. Run:

```
python tests/note_schema_roundtrip.py
python schema_validate.py --all schemas
```

    Expected: final line `NOTE SCHEMA: 7 passed, 0 failed`, exit 0; exit 0.

    No em dash characters in any file this task writes.
  </action>
  <verify>
  <automated>python tests/note_schema_roundtrip.py && python schema_validate.py --all schemas</automated>
Expected: final line `NOTE SCHEMA: 7 passed, 0 failed`, exit 0 from both. The
degraded state this task proves is the broken anchor: an anchor invalidated
by a lesson revision keeps its note attached to its objective with the broken
selector flagged as a non-resolved relocation state, never silently
relocated and never dropped.
  </verify>
  <acceptance_criteria>
- `python tests/note_schema_roundtrip.py` exits 0 with final line
  `NOTE SCHEMA: 7 passed, 0 failed`.
- Every vocabulary tuple matches D-16C-8 exactly; unknown members raise
  `ValueError` naming the member.
- Every copy string matches the UI-SPEC Copywriting Contract verbatim.
- `resolve_anchor` exercises all four states in the test, mutates nothing,
  and returns `relocated_probable` for an ambiguous multi-hit.
- `notes.py` contains no import of `runtime` and none from `surfaces`,
  asserted in the test via `ast` over the module source (module-level and
  function-level imports both).
- `schemas/note.schema.json` passes `python schema_validate.py --all schemas`
  and rejects a sidecar carrying an unknown `status`.
- No file this task writes contains an em dash character, verified with the
  `chr(0x2014)` form.
  </acceptance_criteria>
  <reversibility rating="costly">The vocabularies and the sidecar shape are
  what plans 16C-06, 16C-07, and 16C-09 build against and what real note
  documents will carry; renaming a vocabulary member after notes exist is a
  migrate operation, not an edit.</reversibility>
  <done>The NOTE-01 record exists with closed vocabularies, one hashing
  helper, four relocation states, an atomic writer, one reader, and a
  published schema.</done>
</task>

<task type="auto">
  <name>Task 3: the guard learns the note-document marker</name>
  <files>surfaces/cli.py, tests/note_schema_roundtrip.py</files>
  <read_first>
- `surfaces/cli.py` `cmd_guard` (line 299) and the `_corpus_marker` helper it
  calls, in full.
- `16C-RESEARCH.md` Pattern 6 and Pitfall 8: a stray real note pasted into
  the repo must fail CI the same way a stray bank does, through one additive
  marker check, never a second guard.
- `tests/guard_roundtrip.py`, for how guard behavior is currently tested.
  </read_first>
  <action>
1. Extend the corpus-marker check in `surfaces/cli.py` additively: a markdown
   file whose text contains a line matching the regex
   `^\s*"?note_document_id"?\s*:` is a corpus marker, reported as
   `carries the corpus marker note_document_id`. Add it inside the existing
   marker helper as one new branch beside the existing section markers. Do
   not add a new walker, a new command, or a new skip list entry.

2. Add `check_guard_marker` to `tests/note_schema_roundtrip.py`: in a temp
   directory, write `stray_note.md` containing a fictional line
   `note_document_id: abc123` plus one sentence of invented prose, then run
   `python itembank.py guard <tempdir>` via subprocess. Assert exit code 1
   and that stdout contains `1 offending files` and `note_document_id`.
   Then run `python itembank.py guard .` at the repository root via
   subprocess and assert exit 0 with `0 offending files`: the marker catches
   strays without flagging the repository.

3. Update `main()` to run eight checks and print
   `NOTE SCHEMA: 8 passed, 0 failed`. Run:

```
python tests/note_schema_roundtrip.py
python tests/guard_roundtrip.py
python itembank.py guard .
```

   Expected: final line `NOTE SCHEMA: 8 passed, 0 failed`, exit 0; exit 0;
   `0 offending files`.

   No em dash characters in any file this task writes.
  </action>
  <verify>
  <automated>python tests/note_schema_roundtrip.py && python tests/guard_roundtrip.py && python itembank.py guard .</automated>
Expected: `NOTE SCHEMA: 8 passed, 0 failed` then exit 0 then `0 offending
files`. The degraded state this task proves is the refusal: a stray note
document outside fixtures/ fails guard by name while the repository stays
green.
  </verify>
  <acceptance_criteria>
- The marker lands inside the existing corpus-marker helper as one branch; no
  second walker or command exists (`git diff surfaces/cli.py` shows one
  function changed).
- The temp-dir guard run exits 1 naming `note_document_id`; the repo guard
  run reports `0 offending files`.
- `python tests/guard_roundtrip.py` still exits 0.
- No file this task writes contains an em dash character, verified with the
  `chr(0x2014)` form.
  </acceptance_criteria>
  <reversibility rating="reversible">One additive marker branch; removing it
  restores the prior guard exactly.</reversibility>
  <done>A real note document cannot be committed to this repository without
  CI failing by name.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| fixture content to repository | Generated bank text is committed as Python constants; anything real crossing in would live in git history forever. |
| note sidecar to renderers | The sidecar is untrusted learner input to any later surface; closed vocabularies are validated on read and learner wording is data, never markup. |
| anchor resolution to provenance | A guessed relocation silently applied converts a guess into provenance. |
| guard to stray learner data | The marker check is the only mechanical stop between a pasted real note and CI. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-16C-02-01 | Information Disclosure | real learner or course content entering the repo through fixtures | high | mitigate | Every corpus string is invented and labeled synthetic in the module docstring; banks are written only to caller directories; `python itembank.py guard .` is an acceptance check on every task; Task 3's marker catches stray note documents by name. |
| T-16C-02-02 | Tampering | a probable relocation auto-applied, converting a guess into provenance | high | mitigate | `resolve_anchor` mutates nothing and returns `relocated_probable` with candidates for every ambiguous case; the test asserts the revised-lesson note keeps its objective_ids with a non-resolved state. |
| T-16C-02-03 | Spoofing | authored pre-highlighting recorded as learner activity | medium | mitigate | `authored_prehighlight` carries empty owner and authored authorship, has no path into learner notes, and `check_authored_zero` asserts a byte-identical evidence log. |
| T-16C-02-04 | Tampering | a second parser growing around the note document | medium | mitigate | The sidecar is stdlib json; the Markdown half is stored and returned verbatim by one reader; no markdown grammar code exists in notes.py, asserted by the ast import check. |
| T-16C-02-05 | Elevation of Privilege | notes.py reaching the scorer or a surface | medium | mitigate | The test asserts via ast that notes.py imports neither runtime nor anything from surfaces. |
| T-16C-02-06 | Tampering | supply chain: a third-party dependency introduced by this plan | high | mitigate | None is added; stdlib only. Per PLANNING-DIRECTIVES section 4a, any future dependency is vendored at a pinned version with a recorded checksum and a named license review. |
</threat_model>

<out_of_scope>
Refused by this plan, by name:

- No promotion, review, or deletion functions; plan 16C-06 owns NOTE-02 and
  NOTE-03, including every promotion copy string.
- No evidence event, no `evidence.py` change, and no `import evidence` in
  notes.py yet; the two lifecycle event types and the builder that appends
  them are plan 16C-06's.
- No trio projection or validator; plan 16C-07 owns `note_outputs.py`.
- No note rendering, route, CLI command, or HTML; 16C ships contracts and
  fixtures, pixels are 17A's.
- No approved_roots enforcement or settings change; the `_notes/` default is
  a documented path constant, and root governance stays with the 16B
  settings surface.
- No component-ID anchors; heading slugs are the 16C scheme per D-16C-7, and
  the D-14A-2 upgrade is a recorded seam, not code here.
- No `itembank lint` requirements on corpus banks; they are fixtures, not
  authored courseware, and the author-bank rules stay with the authoring
  skill.
</out_of_scope>

<flagged_assumptions>
- **The corpus banks skip lint by design.** If a reviewer wants lint-clean
  corpus banks, that is a fixture-quality upgrade with its own plan; the
  parse-level assertions here are what the downstream fixtures actually
  consume.
- **`relocated_exact` versus `orphaned` for a fully replaced heading depends
  on whether any other heading body collides.** The test therefore asserts
  the replaced heading's state is in `("orphaned", "relocated_probable")`
  rather than pinning one, and records which occurred.
- **The sidecar carries the whole note list per document (one file per
  course per surface, D-16C-2).** Per-note files were considered and not
  chosen; revisiting that is a new decision record, and the one reader keeps
  the change local.
</flagged_assumptions>

<summary_obligations>
`16C-02-SUMMARY.md` records: the four corpus paths and their item, heading,
term, and relation counts; the final line of every verify command with actual
stdout; which relocation state the revised-lesson fixture produced; the exact
guard output for the stray-note temp run and the repo run; confirmation that
every copy string matched the UI-SPEC verbatim; and any deviation from this
plan with its reason.
</summary_obligations>

<output>
Create
`.planning/phases/16C-strategies-notes-prototype-convergence/16C-02-SUMMARY.md`
when done.
</output>
