#!/usr/bin/env python3
"""Phase 16C (16C-06) note promotion, artifact, and lifecycle roundtrip.

Direct standard-library roundtrip script in the project's established shape:
`fail(msg)` and a non-zero exit on failure. It proves NOTE-02, NOTE-03, and
the one additive evidence extension:

- two new event types carrying strategy lifecycle facts and no content,
- additivity proven against the exact baselines `16C-PRECONDITION.md`
  recorded before any 16C change existed,
- promotion gated on accepted sources and stopped by a source conflict,
- acceptance producing a derived cited copy and never mutating the original,
- an unreviewed note staying private and inert forever,
- an artifact pending until a HUMAN mark settles it, with a model proposal
  changing nothing,
- deletion that removes the note and says honestly what it cannot remove.

The degraded states this file exists to prove are the unreviewed default and
pending-forever: a note nobody reviews and an artifact nobody marks both stay
exactly where they are, and neither drifts toward authority on its own.
"""
import copy as copy_mod
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import evidence
import notes
from fixtures import note_strategy_corpus as corpus
import model

PRECONDITION = os.path.join(
    ROOT, ".planning", "phases",
    "16C-strategies-notes-prototype-convergence", "16C-PRECONDITION.md")

FAILURES = []


def fail(msg):
    print("FAIL: %s" % msg)
    FAILURES.append(msg)


def _a_note(course_id="course-x"):
    target = notes.target_record(
        "lesson_step", "counting-the-breaths", "fp", "heading:x",
        notes.hash_quoted_context("an invented block of prose"))
    return notes.note_record(course_id, ["emt.obj.1"], "learner_claim",
                             "An invented claim about counting.", [target])


def check_lifecycle_event():
    """Two additive event types, a closed key set, and no content."""
    tmp = tempfile.mkdtemp()
    try:
        log = os.path.join(tmp, "evidence.jsonl")
        first = notes.strategy_lifecycle_event(
            log, "activity_completed", "s1", "guided_note_spine",
            "completed", "note-1")
        if first.get("status") != "recorded":
            fail("the first append reported %r" % (first,))
        replay = notes.strategy_lifecycle_event(
            log, "activity_completed", "s1", "guided_note_spine",
            "completed", "note-1")
        if replay.get("status") != "already_recorded":
            fail("an identical replay reported %r" % (replay,))
        notes.strategy_lifecycle_event(
            log, "activity_skipped", "s1", "worked_reasoning",
            "skipped_optional")

        live = list(evidence.live_events(log))
        if len(live) != 2:
            fail("expected two live events, got %d" % len(live))
        wanted = {"schema_version", "event_id", "event_type", "ts",
                  "session_id", "strategy_id", "action_state", "note_ref",
                  "dedupe_key"}
        for event in live:
            if set(event) != wanted:
                fail("the lifecycle event carries %r" % sorted(event))
            for key in event:
                if any(part in key for part in ("wording", "text",
                                                "content", "body")):
                    fail("the lifecycle event carries a content-bearing "
                         "field: %r" % key)
            for value in event.values():
                if isinstance(value, str) and len(value) > 200:
                    fail("a lifecycle field is long enough to be content")

        for label, call in [
                ("event type", lambda: notes.strategy_lifecycle_event(
                    log, "activity_started", "s", "guided_note_spine",
                    "completed")),
                ("strategy", lambda: notes.strategy_lifecycle_event(
                    log, "activity_completed", "s", "close_reading",
                    "completed")),
                ("action state", lambda: notes.strategy_lifecycle_event(
                    log, "activity_completed", "s", "guided_note_spine",
                    "finished"))]:
            try:
                call()
            except ValueError:
                pass
            else:
                fail("an unknown %s was accepted" % label)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check_event_schema_registration():
    """The two new types are registered in the published event schema too.

    D-23's convention is that an event type joins `KNOWN_EVENT_TYPES` and the
    schema enum in the same commit as its builder. Plan 16C-06 names only the
    tuple, and a lifecycle event was checked against
    `schemas/response.schema.json` here before the enum was extended: it
    failed, because `other_event`'s enum is closed. Registering the tuple
    alone would have shipped an event type the project's own published
    contract rejects.
    """
    with open(os.path.join(ROOT, "schemas", "response.schema.json"),
              encoding="utf-8") as fh:
        schema = json.load(fh)
    enum = schema["$defs"]["other_event"]["properties"]["event_type"]["enum"]
    for event_type in notes.STRATEGY_LIFECYCLE_EVENT_TYPES:
        if event_type not in enum:
            fail("%r is in KNOWN_EVENT_TYPES but not in the published "
                 "event schema enum (D-23)" % event_type)
    tmp = tempfile.mkdtemp()
    try:
        log = os.path.join(tmp, "evidence.jsonl")
        notes.strategy_lifecycle_event(log, "activity_completed", "s1",
                                       "guided_note_spine", "completed",
                                       "note-1")
        notes.strategy_lifecycle_event(log, "activity_skipped", "s1",
                                       "worked_reasoning",
                                       "skipped_optional")
        import schema_validate
        for line in io.open(log, encoding="utf-8"):
            event = json.loads(line)
            errors = schema_validate.validate(event, schema)
            if errors:
                fail("a %s event fails the published schema: %s"
                     % (event["event_type"], errors[0][:160]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _recorded_baseline():
    """The five baseline lines 16C-01 recorded, read from the precondition
    file rather than recomputed. Re-recording the baseline would make the
    additivity proof circular."""
    text = io.open(PRECONDITION, encoding="utf-8").read()
    block = text.split("## Additivity baseline", 1)[1].split("```")[1]
    lines = [l.strip() for l in block.strip().split("\n") if l.strip()]
    hashes = {}
    counts = view_hash = None
    for line in lines:
        if line.startswith("["):
            counts = line
        elif re.fullmatch(r"[0-9a-f]{64}", line):
            view_hash = line
        else:
            path, digest = line.rsplit(" ", 1)
            hashes[path] = digest
    return hashes, counts, view_hash


# Schema keys added AFTER 16C recorded its additivity baseline. Stripping
# these reconstructs the document the baseline describes, so 16C's proof stays
# checkable instead of being retired the first time a later phase extends one
# of the baselined files. A key is added here only when the phase that added
# it is additive by construction; a key that CHANGED an existing property
# would not come back to the baseline digest and would still fail, which is
# the case the check exists for.
POST_BASELINE_SCHEMA_KEYS = {
    # plan 15A-04: the agent autonomy policy.
    "schemas/settings.schema.json": ("agent_policy",),
}


def check_additivity():
    """The pre-16C world is byte-identical, and the degrade path still
    degrades."""
    hashes, counts, view_hash = _recorded_baseline()
    if len(hashes) != 3 or counts is None or view_hash is None:
        fail("could not parse the recorded baseline: %r"
             % (hashes, counts, view_hash))
        return
    for path, expected in hashes.items():
        raw = open(os.path.join(ROOT, path), "rb").read()
        actual = hashlib.sha256(raw).hexdigest()
        if actual == expected:
            continue
        # A later phase may legitimately EXTEND a baselined schema. 16C's
        # claim is that 16C did not change the pre-16C world, and that claim
        # is still checkable after an additive change: strip the keys added
        # after the baseline was taken and the digest must come back.
        #
        # The baseline itself is never re-recorded. Re-recording it would make
        # the additivity proof circular, which is exactly what
        # `_recorded_baseline`'s docstring warns about, so the recovery is to
        # reconstruct the baselined document rather than to update the number.
        if path in POST_BASELINE_SCHEMA_KEYS:
            document = json.loads(raw.decode("utf-8"))
            for key in POST_BASELINE_SCHEMA_KEYS[path]:
                document.get("properties", {}).pop(key, None)
                if key in document.get("required", []):
                    document["required"].remove(key)
            stripped = json.dumps(document, indent=2,
                                  ensure_ascii=False) + "\n"
            actual = hashlib.sha256(stripped.encode("utf-8")).hexdigest()
            if actual == expected:
                continue
        fail("%s changed: %s, baseline %s" % (path, actual, expected))
    caps = [list(evidence.capture_events(os.path.join(ROOT, p)))
            for p in ("fixtures/selection_evidence.jsonl",
                      "fixtures/lesson_retention_events.jsonl")]
    if str([len(c) for c in caps]) != counts:
        fail("the captured view counts are %r, baseline %r"
             % ([len(c) for c in caps], counts))
    actual = hashlib.sha256(json.dumps(caps, sort_keys=True)
                            .encode("utf-8")).hexdigest()
    if actual != view_hash:
        fail("the captured view hash is %s, baseline %s"
             % (actual, view_hash))
    if evidence.EVENT_SCHEMA_VERSION != 2:
        fail("the schema version moved to %r; D-16C-1 says it stays 2"
             % (evidence.EVENT_SCHEMA_VERSION,))
    if len(evidence.KNOWN_EVENT_TYPES) != 16:
        fail("KNOWN_EVENT_TYPES holds %d members"
             % len(evidence.KNOWN_EVENT_TYPES))
    if evidence.KNOWN_EVENT_TYPES[-2:] != ("activity_completed",
                                           "activity_skipped"):
        fail("the two new types are not last: %r"
             % (evidence.KNOWN_EVENT_TYPES[-2:],))

    # The D-09 degrade path: a reader meeting an unknown type skips and
    # warns rather than failing, which is what makes a later build's event
    # type survivable.
    tmp = tempfile.mkdtemp()
    try:
        log = os.path.join(tmp, "evidence.jsonl")
        with open(log, "w", encoding="utf-8") as fh:
            fh.write(json.dumps({"schema_version": 2,
                                 "event_id": "f" * 32,
                                 "event_type": "not_a_type",
                                 "ts": "2026-08-29T00:00:00.000Z"}) + "\n")
        run = subprocess.run(
            [sys.executable, "-c",
             "import sys; sys.path.insert(0, %r); import evidence; "
             "print(len(list(evidence.events(%r))))" % (ROOT, log)],
            capture_output=True, text=True)
        combined = run.stdout + run.stderr
        if "0" not in run.stdout:
            fail("an unknown event type was not skipped: %r" % run.stdout)
        if "unknown event_type" not in combined:
            fail("the skip did not warn: %r" % combined[-200:])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check_promotion_gates():
    """Unsupported claims block; a source conflict stops."""
    note = notes.request_review(_a_note())
    claims = [{"text": "a", "source_id": "src-1"},
              {"text": "b", "source_id": ""},
              {"text": "c", "source_id": "src-missing"}]
    result = notes.review_promotion(note, claims, {"src-1"}, [], "accept",
                                    "Weibao")
    if result["outcome"] != "blocked":
        fail("unsupported claims produced %r" % result["outcome"])
    elif result["copy"] != ("Every keyed or factual claim needs an accepted "
                            "source. 2 claims have no accepted source yet."):
        fail("the source-check sentence is %r" % result["copy"])

    supported = [{"text": "a", "source_id": "src-1"}]
    result = notes.review_promotion(
        note, supported, {"src-1"},
        ["src-1 and src-2 disagree about the order of events"], "accept",
        "Weibao")
    if result["outcome"] != "conflict_stop":
        fail("a source conflict produced %r" % result["outcome"])
    elif result["copy"] != ("A source conflict was found. Promotion is "
                            "stopped until the conflict is resolved."):
        fail("the conflict sentence is %r" % result["copy"])

    if notes.promotion_state(result["note"]) != "review_requested":
        fail("a blocked note left review_requested: %r"
             % notes.promotion_state(result["note"]))
    if "derived" in result:
        fail("a stopped promotion produced a derived record")


def check_promotion_accept_decline():
    """Acceptance derives; decline refuses; neither mutates the original."""
    note = notes.request_review(_a_note())
    before = copy_mod.deepcopy(note)
    claims = [{"text": "a", "source_id": "src-1"}]

    result = notes.review_promotion(note, claims, {"src-1"}, [], "accept",
                                    "Weibao")
    if result["outcome"] != "applied":
        fail("a clean promotion produced %r" % result["outcome"])
        return
    derived = result["derived"]
    if derived["status"] != "learner_accepted":
        fail("the derived record's status is %r" % derived["status"])
    if derived["note_id"] == note["note_id"]:
        fail("acceptance reused the original note id")
    edges = derived["derivations"]
    if not edges or edges[0].get("from_note_revision") != note["revision_id"]:
        fail("the derivation edge does not name the original revision: %r"
             % (edges,))
    if note != before:
        fail("acceptance mutated the learner's note")
    if not result["badge"].startswith("Accepted into the course on "):
        fail("the accepted badge is %r" % result["badge"])

    declined = notes.review_promotion(note, claims, {"src-1"}, [], "decline",
                                      "Weibao", reason="needs a citation")
    if declined["outcome"] != "refused":
        fail("a decline produced %r" % declined["outcome"])
    if declined["badge"] != ("Not accepted: needs a citation. Your note is "
                             "unchanged."):
        fail("the declined badge is %r" % declined["badge"])
    if note != before:
        fail("a decline mutated the learner's note")
    try:
        notes.review_promotion(note, claims, {"src-1"}, [], "decline",
                               "Weibao")
    except ValueError:
        pass
    else:
        fail("a decline without a reason was accepted")
    try:
        notes.review_promotion(note, claims, {"src-1"}, [], "accept", "")
    except ValueError:
        pass
    else:
        fail("a promotion with no named reviewer was accepted")

    # A model may annotate and never decides: the annotation rides on the
    # derived record and no code path turns it into an outcome.
    annotated = notes.review_promotion(
        note, claims, {"src-1"}, [], "accept", "Weibao",
        annotations=["Generated synthesis: this restates section 2."])
    if annotated["outcome"] != "applied":
        fail("an annotated promotion produced %r" % annotated["outcome"])
    if not annotated["derived"].get("annotations"):
        fail("the labeled annotation was dropped")


def check_unreviewed_stays_private():
    """A note nobody reviews is inert: no derived copy, no evidence."""
    tmp = tempfile.mkdtemp()
    try:
        bank = corpus.build_subject_bank("emt_respiratory", tmp)
        headings = model.parse_lesson(bank)["headings"]
        made = []
        for raw in corpus.build_note_set("emt_respiratory", headings)[:2]:
            heading = [h for h in headings
                       if h["slug"] == raw["anchor_slug"]][0]
            target = notes.target_record(
                "lesson_step", heading["slug"],
                notes.hash_quoted_context(heading["body"]),
                "heading:%s" % heading["slug"],
                notes.hash_quoted_context(heading["body"]))
            made.append(notes.note_record(
                "course-emt", [raw["objective_id"]], raw["epistemic_role"],
                raw["learner_wording"], [target]))
        promoted, untouched = made[0], made[1]

        result = notes.review_promotion(
            notes.request_review(promoted),
            [{"text": "a", "source_id": "src-1"}], {"src-1"}, [], "accept",
            "Weibao")
        if result["outcome"] != "applied":
            fail("the fixture's promotion did not apply")
            return

        if notes.promotion_state(untouched) != "private":
            fail("an unreviewed note reads %r"
                 % notes.promotion_state(untouched))
        if notes.PROMOTION_COPY["private_badge"] != \
                "Private note. Not part of the course.":
            fail("the private badge is %r"
                 % notes.PROMOTION_COPY["private_badge"])

        derived_blob = json.dumps(result["derived"])
        if untouched["note_id"] in derived_blob \
                or untouched["learner_wording"] in derived_blob:
            fail("the unreviewed note leaked into the derived record")

        # And it reaches no evidence event, checked against a log that does
        # carry lifecycle facts for the promoted one.
        log = os.path.join(tmp, "evidence.jsonl")
        notes.strategy_lifecycle_event(log, "activity_completed", "s1",
                                       "guided_note_spine", "completed",
                                       promoted["note_id"])
        blob = io.open(log, encoding="utf-8").read()
        if untouched["note_id"] in blob:
            fail("the unreviewed note reached the evidence log")
        if untouched["learner_wording"] in blob:
            fail("learner wording reached the evidence log")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check_artifact_pending():
    """Pending until a human mark; a proposal settles nothing."""
    tmp = tempfile.mkdtemp()
    try:
        log = os.path.join(tmp, "evidence.jsonl")
        artifact = notes.artifact_record(
            "proof", "course-math", ["math_linear_system.obj.1"],
            ["States which of the three cases applies",
             "Carries the sign through the substitution",
             "Checks the point in both original equations"])
        if artifact["kind"] != "proof" or len(artifact["rubric"]) != 3:
            fail("the artifact record is %r" % (artifact,))
        try:
            notes.artifact_record("essay", "c", [], [])
        except ValueError:
            pass
        else:
            fail("an unknown artifact kind was accepted")

        response = {
            "schema_version": evidence.EVENT_SCHEMA_VERSION,
            "event_id": "a" * 32,
            "event_type": "response",
            "ts": evidence.utc_now(),
            "session_id": "s-art",
            "item_id": artifact["artifact_id"],
            "score": None,
            "dedupe_key": hashlib.sha256(b"artifact-response").hexdigest(),
        }
        evidence.append_event(log, response)

        view = notes.artifact_evidence_view(artifact, "a" * 32, log)
        if view["state"] != "pending":
            fail("a fresh artifact reads %r" % view["state"])
        if view["badge"] != "Pending review":
            fail("the pending badge is %r" % view["badge"])
        if view["lines"][0] != ("Recorded as pending by itembank. A reviewer "
                                "settles this. A model never settles it."):
            fail("the pending explainer is %r" % view["lines"][0])

        proposal = evidence.mark_proposal_event(
            "s-art", "bank.md", artifact["artifact_id"], "ref", "a" * 32,
            "interaction-1", [])
        evidence.append_event(log, proposal)
        view = notes.artifact_evidence_view(artifact, "a" * 32, log)
        if view["state"] != "pending":
            fail("a model proposal settled the artifact: %r" % view["state"])
        if ("A model has proposed a mark. It settles nothing until a "
                "reviewer accepts it.") not in view["lines"]:
            fail("the proposal line is missing: %r" % view["lines"])

        try:
            evidence.mark_event("s-art", artifact["artifact_id"], "ref",
                                "a" * 32, True, marker="model")
        except ValueError:
            pass
        else:
            fail("the shipped marker gate accepted a model mark")

        mark = evidence.mark_event(
            "s-art", artifact["artifact_id"], "ref", "a" * 32, True,
            rubric=[{"point": p, "pass": i != 1}
                    for i, p in enumerate(artifact["rubric"])],
            marker="human")
        evidence.append_event(log, mark)
        view = notes.artifact_evidence_view(artifact, "a" * 32, log)
        if view["state"] != "settled":
            fail("a human mark did not settle the artifact: %r"
                 % view["state"])
        if not view["lines"][0].startswith("Reviewed by human on "):
            fail("the settled line is %r" % view["lines"][0])
        rendered = "\n".join(view["lines"])
        if "%" in rendered:
            fail("the artifact view rendered a percent")
        if re.search(r"\b\d+\s*/\s*\d+\b", rendered):
            fail("the artifact view summed its criteria: %r" % rendered)
        met = [l for l in view["lines"] if l.endswith("met")]
        if len(met) != 3:
            fail("expected three per-criterion lines, got %r" % met)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check_delete_honesty():
    """Deletion removes the note and leaves the evidence log alone."""
    tmp = tempfile.mkdtemp()
    try:
        log = os.path.join(tmp, "evidence.jsonl")
        note = _a_note()
        notes.strategy_lifecycle_event(log, "activity_completed", "s1",
                                       "guided_note_spine", "completed",
                                       note["note_id"])
        before = open(log, "rb").read()

        sidecar = {"schema_version": notes.NOTE_SCHEMA_VERSION,
                   "note_document_id": notes.new_note_id(),
                   "course_id": "course-x",
                   "notes": [note, _a_note()]}
        notes_dir = os.path.join(tmp, notes.NOTES_DIRNAME)
        notes.write_note_document(notes_dir, "course-x", "# Notes\n", sidecar)
        result = notes.delete_note(sidecar, note["note_id"])
        if result["deleted"] != 1:
            fail("delete_note removed %d notes" % result["deleted"])
        if any(n["note_id"] == note["note_id"]
               for n in result["sidecar"]["notes"]):
            fail("the note survived its own deletion")
        if result["sidecar"]["tombstones"][0]["status"] != "deleted":
            fail("no tombstone was recorded")
        if result["copy"] != ("Delete this note? This removes the note and "
                              "its private index. Evidence the runtime is "
                              "required to keep is not affected."):
            fail("the deletion copy is %r" % result["copy"])

        notes.write_note_document(notes_dir, "course-x", "# Notes\n",
                                  result["sidecar"])
        read = notes.read_note_document(notes_dir, "course-x")
        if any(n["note_id"] == note["note_id"]
               for n in read["sidecar"]["notes"]):
            fail("the deleted note came back on re-read")
        if open(log, "rb").read() != before:
            fail("deletion changed the append-only evidence log")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    checks = [check_lifecycle_event, check_event_schema_registration,
              check_additivity, check_promotion_gates,
              check_promotion_accept_decline, check_unreviewed_stays_private,
              check_artifact_pending, check_delete_honesty]
    for check in checks:
        check()
    failed = len(FAILURES)
    print("NOTE PROMOTION: %d passed, %d failed"
          % (len(checks) - failed, failed))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
