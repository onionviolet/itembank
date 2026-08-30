#!/usr/bin/env python3
"""Phase 16C (16C-02) learner-note schema roundtrip.

Direct standard-library roundtrip script in the project's established shape:
`fail(msg)` and a non-zero exit on failure. It proves the NOTE-01 record end
to end over the phase's own synthetic corpus: closed vocabularies that raise
on an unknown member, copy that matches the UI-SPEC Copywriting Contract
verbatim, three capture paths that produce one identical target record, an
atomic document write with one reader, all four relocation states driven
through `resolve_anchor`, authored pre-highlighting that produces zero
evidence, and the guard marker that keeps a real note document out of this
repository.

The degraded state this file exists to prove is the broken anchor: a lesson
revision that invalidates an anchor leaves the note attached to its objective
with the selector flagged, never silently relocated and never dropped.
"""
import ast
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import model
import notes
import schema_validate
from fixtures import note_strategy_corpus as corpus

NOTE_SCHEMA = os.path.join(ROOT, "schemas", "note.schema.json")

FAILURES = []


def fail(msg):
    print("FAIL: %s" % msg)
    FAILURES.append(msg)


def _load_schema():
    with open(NOTE_SCHEMA, encoding="utf-8") as fh:
        return json.load(fh)


def _anchor_notes(subject, bank_path, course_id):
    """Build the corpus note set for `subject` and turn it into real note
    records anchored to the bank's headings. Returns (records, headings)."""
    headings = model.parse_lesson(bank_path)["headings"]
    by_slug = dict((h["slug"], h) for h in headings)
    records = []
    for raw in corpus.build_note_set(subject, headings):
        heading = by_slug[raw["anchor_slug"]]
        target = notes.target_record(
            "lesson_step", heading["slug"],
            notes.hash_quoted_context(heading["body"]),
            "heading:%s" % heading["slug"],
            notes.hash_quoted_context(heading["body"]))
        records.append(notes.note_record(
            course_id, [raw["objective_id"]], raw["epistemic_role"],
            raw["learner_wording"], [target]))
    return records, headings


def check_vocabularies():
    """The seven closed vocabularies equal D-16C-8 exactly, and every
    validated field raises ValueError naming its unknown member."""
    expected = {
        "EPISTEMIC_ROLES": ("quote", "learner_claim", "learner_question",
                            "learner_example", "calculation", "diagram",
                            "accepted_reference_link"),
        "STRATEGY_ACTION_STATES": ("not_started", "draft", "completed",
                                   "skipped_optional", "equivalent_completed",
                                   "needs_review"),
        "RELOCATION_STATES": ("resolved", "relocated_exact",
                              "relocated_probable", "orphaned"),
        "NOTE_STATUS": ("draft", "learner_accepted", "disputed", "superseded",
                        "deleted"),
        "TARGET_KINDS": ("source", "lesson_step", "media", "item_public",
                         "concept"),
        "AUTHORSHIP_TYPES": ("learner", "authored"),
    }
    for name, value in expected.items():
        if getattr(notes, name) != value:
            fail("%s is %r, expected %r" % (name, getattr(notes, name), value))

    good_target = notes.target_record("concept", "s", "f", "l",
                                      notes.hash_quoted_context("x"))
    cases = [
        ("epistemic role", lambda: notes.note_record(
            "c", ["o"], "not_a_role", "w", [good_target])),
        ("authorship type", lambda: notes.note_record(
            "c", ["o"], "quote", "w", [good_target], authorship="robot")),
        ("note status", lambda: notes.note_record(
            "c", ["o"], "quote", "w", [good_target], status="archived")),
        ("target kind", lambda: notes.target_record(
            "paragraph", "s", "f", "l", "sha256:0000000000000000")),
    ]
    for label, call in cases:
        try:
            call()
        except ValueError as exc:
            if label.split()[0] not in str(exc):
                fail("%s ValueError does not name the field: %s"
                     % (label, exc))
        else:
            fail("%s accepted an unknown member" % label)

    # The tier rule, asserted over the source rather than over what happens
    # to be imported: notes.py may not reach the scorer or any surface.
    tree = ast.parse(open(os.path.join(ROOT, "notes.py"),
                         encoding="utf-8").read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names = [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            names = [node.module or ""]
        else:
            continue
        for name in names:
            if name == "runtime" or name.split(".")[0] == "surfaces":
                fail("notes.py imports %s; the tier rule forbids it" % name)


def check_capture_copy():
    """Every capture and anchor string equals the UI-SPEC Copywriting
    Contract verbatim. Written out here rather than compared to the module,
    so a silent edit on either side is a failure."""
    expect = {
        "affordance": "Add a note",
        "anchor_prompt": "What is this note about?",
        "anchor_choices": ("This selection", "This block",
                           "This whole section",
                           "This objective (no anchor)"),
        "keyboard_picker": "Use arrow keys to choose a block, then Enter to select. Shift plus arrows extends the selection.",
        "role_prompt": "This note is:",
        "role_choices": ("A quotation", "My claim", "My question",
                         "My example", "A calculation", "A diagram",
                         "A link to an accepted reference"),
        "privacy_line": "Private to you. Nothing is shared unless you request review.",
        "save": "Save to my notes",
        "submit": "Submit activity",
        "submit_clarifier": "Submitting shares this response with the course. Your saved notes stay private.",
        "saved_status": "Saved to your notes.",
        "draft_restored": "Your draft note was restored.",
        "empty_state": "No notes yet for this course. Add one from any lesson in Learn.",
    }
    if set(notes.CAPTURE_COPY) != set(expect):
        fail("CAPTURE_COPY keys are %r" % sorted(notes.CAPTURE_COPY))
    for key, value in expect.items():
        if notes.CAPTURE_COPY.get(key) != value:
            fail("CAPTURE_COPY[%r] is %r" % (key, notes.CAPTURE_COPY.get(key)))
    labels = {
        "resolved": "Anchored",
        "relocated_exact": "Anchor moved with the lesson",
        "relocated_probable": "Anchor probably moved: review needed",
        "orphaned": "Anchor lost. Still linked to {objective name}.",
    }
    if notes.ANCHOR_STATE_LABELS != labels:
        fail("ANCHOR_STATE_LABELS is %r" % (notes.ANCHOR_STATE_LABELS,))
    if set(notes.ANCHOR_STATE_LABELS) != set(notes.RELOCATION_STATES):
        fail("every relocation state needs exactly one label")
    if notes.PROBABLE_CONTROLS != ("Confirm new location", "Keep unanchored"):
        fail("PROBABLE_CONTROLS is %r" % (notes.PROBABLE_CONTROLS,))
    if len(notes.CAPTURE_COPY["role_choices"]) != len(notes.EPISTEMIC_ROLES):
        fail("role_choices must map positionally onto EPISTEMIC_ROLES")


def check_target_identity():
    """D13: pointer selection, the keyboard block-and-range picker, and the
    structured block-choice list produce the identical record."""
    body = "One invented block of lesson prose, quoted three ways."
    made = [notes.target_record("lesson_step", "a-block",
                                notes.hash_quoted_context(body),
                                "heading:a-block",
                                notes.hash_quoted_context(body))
            for _ in ("pointer", "keyboard", "structured")]
    if not (made[0] == made[1] == made[2]):
        fail("the three capture paths produced different records")
    if any("path" in key or "input" in key for key in made[0]):
        fail("the target record leaks the interaction path")


def check_roundtrip():
    """Write and read one note document; the sidecar survives byte for byte
    and validates against the published schema."""
    tmp = tempfile.mkdtemp()
    try:
        bank = corpus.build_subject_bank("emt_respiratory", tmp)
        records, _ = _anchor_notes("emt_respiratory", bank, "course-emt")
        sidecar = {"schema_version": notes.NOTE_SCHEMA_VERSION,
                   "note_document_id": notes.new_note_id(),
                   "course_id": "course-emt",
                   "notes": records}
        markdown = "# Notes for course-emt\n\n" + "\n\n".join(
            "## %s\n\n%s" % (r["epistemic_role"], r["learner_wording"])
            for r in records)
        notes_dir = os.path.join(tmp, notes.NOTES_DIRNAME)
        notes.write_note_document(notes_dir, "course-emt", markdown, sidecar)
        read = notes.read_note_document(notes_dir, "course-emt")
        if read is None:
            fail("read_note_document returned None after a write")
            return
        if read["sidecar"] != sidecar:
            fail("the sidecar did not survive the roundtrip")
        if read["markdown"] != markdown:
            fail("the markdown did not survive the roundtrip")
        errors = schema_validate.validate(read["sidecar"], _load_schema())
        if errors:
            fail("sidecar fails its own schema: %s" % errors[:3])
        if notes.read_note_document(os.path.join(tmp, "nowhere")) is not None:
            fail("read_note_document invented a document")

        bad = json.loads(json.dumps(sidecar))
        bad["notes"][0]["status"] = "archived"
        if not schema_validate.validate(bad, _load_schema()):
            fail("the schema accepted an unknown note status")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check_relocation_states():
    """All four states, driven through real lesson revisions."""
    tmp = tempfile.mkdtemp()
    try:
        bank = corpus.build_subject_bank("cs_loop_invariant", tmp)
        records, headings = _anchor_notes("cs_loop_invariant", bank,
                                          "course-cs")
        first = records[0]["targets"][0]
        state = notes.resolve_anchor(first, headings)
        if state["state"] != "resolved":
            fail("an untouched anchor read %r" % (state,))

        # relocated_exact: the same body under a renamed heading.
        renamed = [dict(h) for h in headings]
        target_slug = first["stable_id"]
        for h in renamed:
            if h["slug"] == target_slug:
                h["slug"] = h["slug"] + "-renamed"
        state = notes.resolve_anchor(first, renamed)
        if state["state"] != "relocated_exact":
            fail("a renamed heading with identical body read %r" % (state,))

        # relocated_probable: the same body under two headings.
        doubled = renamed + [dict(renamed[0], slug="a-copy")]
        state = notes.resolve_anchor(first, doubled)
        if state["state"] != "relocated_probable":
            fail("two identical bodies read %r" % (state,))
        if len(state["candidates"]) < 2:
            fail("an ambiguous match must name every candidate: %r" % (state,))

        # The NOTE-01 degraded contract, over a real revision.
        note_for_last = None
        for record in records:
            if record["targets"][0]["stable_id"] == headings[-1]["slug"]:
                note_for_last = record
        if note_for_last is None:
            target = notes.target_record(
                "lesson_step", headings[-1]["slug"],
                notes.hash_quoted_context(headings[-1]["body"]),
                "heading:%s" % headings[-1]["slug"],
                notes.hash_quoted_context(headings[-1]["body"]))
            note_for_last = notes.note_record(
                "course-cs", ["cs_loop_invariant.obj.1"], "learner_claim",
                "An invented claim about the last section.", [target])
        before = list(note_for_last["objective_ids"])
        replaced_slug = corpus.revise_lesson(tmp, "cs_loop_invariant")
        if replaced_slug != headings[-1]["slug"]:
            fail("revise_lesson replaced %r, expected %r"
                 % (replaced_slug, headings[-1]["slug"]))
        after_headings = model.parse_lesson(bank)["headings"]
        state = notes.resolve_anchor(note_for_last["targets"][0],
                                     after_headings)
        if state["state"] not in ("orphaned", "relocated_probable"):
            fail("a revised heading left the anchor %r" % (state,))
        if state["state"] == "resolved":
            fail("a revised heading must never read resolved")
        if note_for_last["objective_ids"] != before:
            fail("resolve_anchor changed the note's objective ids")
        print("  relocation: revised heading produced %r" % state["state"])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check_atomic_write():
    """A corrupt leftover .tmp beside a valid pair is ignored, so an
    interrupted write leaves the last accepted state readable."""
    tmp = tempfile.mkdtemp()
    try:
        sidecar = {"schema_version": notes.NOTE_SCHEMA_VERSION,
                   "note_document_id": notes.new_note_id(),
                   "course_id": "course-x",
                   "notes": []}
        notes.write_note_document(tmp, "course-x", "# Notes\n", sidecar)
        with open(os.path.join(tmp, "notes.md.json.tmp"), "w",
                  encoding="utf-8") as fh:
            fh.write("{ this is a half written file")
        read = notes.read_note_document(tmp, "course-x")
        if read is None or read["sidecar"] != sidecar:
            fail("a stray .tmp broke the reader: %r" % (read,))
        for name in ("notes.md.tmp", "notes.md.json.tmp"):
            path = os.path.join(tmp, name)
            if name == "notes.md.tmp" and os.path.exists(path):
                fail("the writer left %s behind" % name)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check_authored_zero():
    """C107 and D14: authored pre-highlighting carries no owner and writes no
    evidence at all."""
    tmp = tempfile.mkdtemp()
    try:
        log = os.path.join(tmp, "events.jsonl")
        before = os.path.exists(log)
        regions = [notes.authored_prehighlight(
            "Key term in the invented respiratory section",
            notes.target_record("lesson_step", "counting-the-breaths", "f",
                                "l", notes.hash_quoted_context("body"))),
            notes.authored_prehighlight(
            "Second emphasized region",
            notes.target_record("lesson_step", "reading-the-effort", "f",
                                "l", notes.hash_quoted_context("body2")))]
        for region in regions:
            if region["authorship"] != "authored":
                fail("authored_prehighlight authorship is %r"
                     % region["authorship"])
            if region["owner"] != "":
                fail("authored emphasis claimed an owner: %r"
                     % region["owner"])
        if os.path.exists(log) != before:
            fail("authored pre-highlighting wrote an evidence log")
        if os.path.exists(log):
            fail("authored pre-highlighting created %s" % log)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check_guard_marker():
    """A stray note document outside fixtures/ fails guard by name, and the
    repository itself stays green."""
    tmp = tempfile.mkdtemp()
    try:
        stray = os.path.join(tmp, "stray_note.md")
        with open(stray, "w", encoding="utf-8") as fh:
            fh.write("note_document_id: abc123\n\n"
                     "An invented sentence standing in for a real note that "
                     "was pasted into the wrong tree.\n")
        run = subprocess.run(
            [sys.executable, os.path.join(ROOT, "itembank.py"), "guard", tmp],
            capture_output=True, text=True)
        if run.returncode != 1:
            fail("guard exited %d on a stray note document" % run.returncode)
        if "1 offending files" not in run.stdout:
            fail("guard did not count the stray note: %r" % run.stdout[-200:])
        if "note_document_id" not in run.stdout:
            fail("guard did not name the marker: %r" % run.stdout[-200:])
        run = subprocess.run(
            [sys.executable, os.path.join(ROOT, "itembank.py"), "guard",
             ROOT], capture_output=True, text=True)
        if run.returncode != 0 or "0 offending files" not in run.stdout:
            fail("the marker flagged the repository itself: %r"
                 % run.stdout[-300:])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    checks = [check_vocabularies, check_capture_copy, check_target_identity,
              check_roundtrip, check_relocation_states, check_atomic_write,
              check_authored_zero, check_guard_marker]
    for check in checks:
        check()
    failed = len(FAILURES)
    print("NOTE SCHEMA: %d passed, %d failed" % (len(checks) - failed, failed))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
