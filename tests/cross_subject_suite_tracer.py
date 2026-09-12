#!/usr/bin/env python3
"""Phase 16C (16C-09) cross-subject freeze-gate tracer.

The whole 16C contract in one measured pass over four synthetic subjects.
Each scenario corresponds to one fixture the ROADMAP's Phase 16C freeze gate
names, and the report this run feeds records each as passed, weaker proof, or
not run.

This file measures. Every number it prints was produced by the run that
printed it, on the machine and Python version it names, and nothing here
carries a budget, a target, or an estimate: a figure among measurements that
was not measured is a fabricated measurement.

It also holds the ordering check the ROADMAP requires: Phase 16C's freeze is
a 14B-or-later freeze, and 14B's own freeze is conditional on the Phase 13.9
walking skeleton having been walked. So this file reads 13.9's SUMMARY
evidence directly and halts by name if it is absent, rather than trusting any
downstream freeze heading.
"""
import io
import os
import platform
import subprocess
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tests"))

import evidence
import model
import note_outputs
import notes
import progress_claims as pc
import strategies
import upgrade_audit
from fixtures import note_strategy_corpus as corpus
from surfaces import ia

CLOSURE_13_9 = os.path.join(ROOT, ".planning", "phases",
                            "13.9-walking-skeleton", "13.9-03-SUMMARY.md")
LEGACY = os.path.join(ROOT, "fixtures", "legacy_pre135_bank.md")

HALT_13_9 = ("HALT 16C-09 freeze gate: Phase 13.9 has not been walked "
             "(13.9-03-SUMMARY.md missing); the 16C freeze is a 14B-or-later "
             "freeze and may not close before the walking skeleton is "
             "walked.")

FAILURES = []
MEASURED = {}


def fail(msg):
    print("FAIL: %s" % msg)
    FAILURES.append(msg)


def _anchor_notes(subject, bank):
    headings = model.parse_lesson(bank)["headings"]
    by_slug = dict((h["slug"], h) for h in headings)
    made = []
    for raw in corpus.build_note_set(subject, headings):
        heading = by_slug[raw["anchor_slug"]]
        digest = notes.hash_quoted_context(heading["body"])
        target = notes.target_record("lesson_step", heading["slug"], digest,
                                     "heading:%s" % heading["slug"], digest)
        made.append(notes.note_record(
            "course-%s" % subject, [raw["objective_id"]],
            raw["epistemic_role"], raw["learner_wording"], [target],
            owner="weibao"))
    return headings, made


def scenario_strategy_fallback(manifest, tmp):
    """STRATEGY-01, over every subject: one unavailable strategy falls back
    alone, and the picker says so."""
    ids = strategies.STRATEGY_IDS
    available = tuple(s for s in ids if s != "worked_reasoning")
    for subject in corpus.SUBJECTS:
        for strategy_id in ids:
            got = strategies.resolve_strategy(strategy_id, available, ids)
            want = ("continuous_reading" if strategy_id == "worked_reasoning"
                    else strategy_id)
            if got != want:
                fail("%s: %s resolved to %r, expected %r"
                     % (subject, strategy_id, got, want))
        rows = dict((r["strategy_id"], r)
                    for r in strategies.picker_rows(available, ids))
        row = rows["worked_reasoning"]
        if row["row_class"] != "fallback":
            fail("%s: the unavailable row read %r" % (subject,
                                                      row["row_class"]))
        if row["copy"] != ("Worked reasoning isn't available right now. "
                           "Continuing with continuous reading."):
            fail("%s: the unavailable sentence is %r" % (subject,
                                                         row["copy"]))
        if not rows["continuous_reading"]["preselected"]:
            fail("%s: the degraded picker did not preselect the fallback"
                 % subject)


def scenario_conflict_matrix(manifest, tmp):
    """STRATEGY-02: every conflict sentence is 16B's, the sitting locks, and
    16B's own extended fixture runs beside this one."""
    for subject in corpus.SUBJECTS:
        setting = "Learning strategy (%s)" % subject
        state = {setting: {"learner_preference": "retrieval_first",
                           "instructor_policy": "guided_note_spine"}}
        result = strategies.composed_resolve(state)
        if result["effective"][setting] != "guided_note_spine":
            fail("%s: the policy did not win: %r" % (subject,
                                                     result["effective"]))
        expected = ia.mode_layer_conflict_copy(setting, "instructor_policy")
        if not result["conflicts"] or result["conflicts"][0]["copy"] != \
                expected:
            fail("%s: the conflict sentence is not 16B's: %r"
                 % (subject, result["conflicts"]))
        locked = strategies.composed_resolve(state, sitting_active=True)
        if len(locked["locks"]) != 1 or locked["conflicts"]:
            fail("%s: the sitting lock is %r" % (subject, locked))
        elif locked["locks"][0]["copy"] != \
                "Strategy changes are paused during a test sitting.":
            fail("%s: the lock sentence is %r"
                 % (subject, locked["locks"][0]["copy"]))

    run = subprocess.run([sys.executable,
                          os.path.join(ROOT, "tests",
                                       "mode_layer_roundtrip.py")],
                         capture_output=True, text=True)
    if run.returncode != 0:
        fail("the extended 16B conflict fixture failed: %r"
             % run.stdout[-300:])


def scenario_note_anchor(manifest, tmp):
    """NOTE-01, over every subject: a revision breaks the anchor and the note
    keeps its objective."""
    for subject in corpus.SUBJECTS:
        subject_dir = os.path.join(tmp, "anchor-%s" % subject)
        bank = corpus.build_subject_bank(subject, subject_dir)
        headings, made = _anchor_notes(subject, bank)
        replaced = corpus.revise_lesson(subject_dir, subject)
        after = model.parse_lesson(bank)["headings"]
        touched = [n for n in made
                   if n["targets"][0]["stable_id"] == replaced]
        if not touched:
            fail("%s: no note was anchored to the revised heading" % subject)
            continue
        for note in touched:
            before_objectives = list(note["objective_ids"])
            state = notes.resolve_anchor(note["targets"][0], after)
            if state["state"] == "resolved":
                fail("%s: a revised heading still read resolved" % subject)
            if state["state"] not in notes.RELOCATION_STATES:
                fail("%s: %r is not a relocation state" % (subject, state))
            if note["objective_ids"] != before_objectives:
                fail("%s: the broken anchor cost the note its objective"
                     % subject)


def scenario_promotion_pair(manifest, tmp):
    """NOTE-02, over every subject: one promotes, the other stays inert."""
    for subject in corpus.SUBJECTS:
        subject_dir = os.path.join(tmp, "promo-%s" % subject)
        bank = corpus.build_subject_bank(subject, subject_dir)
        _, made = _anchor_notes(subject, bank)
        promoted, untouched = made[0], made[1]
        result = notes.review_promotion(
            notes.request_review(promoted),
            [{"text": "a claim", "source_id": "src-1"}], {"src-1"}, [],
            "accept", "Weibao")
        if result["outcome"] != "applied":
            fail("%s: the sourced note produced %r" % (subject,
                                                       result["outcome"]))
            continue
        if notes.promotion_state(untouched) != "private":
            fail("%s: the unreviewed note reads %r"
                 % (subject, notes.promotion_state(untouched)))
        blob = repr(result["derived"])
        if untouched["note_id"] in blob \
                or untouched["learner_wording"] in blob:
            fail("%s: the unreviewed note leaked into the derived record"
                 % subject)
        log = os.path.join(subject_dir, "evidence.jsonl")
        notes.strategy_lifecycle_event(log, "activity_completed",
                                       "s-%s" % subject,
                                       "guided_note_spine", "completed",
                                       promoted["note_id"])
        text = io.open(log, encoding="utf-8").read()
        if untouched["note_id"] in text \
                or untouched["learner_wording"] in text:
            fail("%s: the unreviewed note reached the evidence log" % subject)


def scenario_pending_artifact(manifest, tmp):
    """NOTE-03: pending, a refused model marker, then a human settlement."""
    log = os.path.join(tmp, "artifact-evidence.jsonl")
    artifact = notes.artifact_record(
        "proof", "course-math", ["math_linear_system.obj.1"],
        ["States the case", "Carries the sign", "Checks the point"])
    response_id = "b" * 32
    evidence.append_event(log, {
        "schema_version": evidence.EVENT_SCHEMA_VERSION,
        "event_id": response_id,
        "event_type": "response",
        "ts": evidence.utc_now(),
        "session_id": "s-trace",
        "item_id": artifact["artifact_id"],
        "score": None,
        "dedupe_key": "trace-artifact-response",
    })
    view = notes.artifact_evidence_view(artifact, response_id, log)
    if view["state"] != "pending" or view["badge"] != "Pending review":
        fail("the artifact did not read pending: %r" % view)
    try:
        evidence.mark_event("s-trace", artifact["artifact_id"], "ref",
                            response_id, True, marker="model")
    except ValueError:
        pass
    else:
        fail("the marker gate accepted a model mark")
    evidence.append_event(log, evidence.mark_event(
        "s-trace", artifact["artifact_id"], "ref", response_id, True,
        rubric=[{"point": p, "pass": True} for p in artifact["rubric"]],
        marker="human"))
    view = notes.artifact_evidence_view(artifact, response_id, log)
    if view["state"] != "settled":
        fail("a human mark did not settle the artifact: %r" % view["state"])
    if "%" in "\n".join(view["lines"]):
        fail("the settled artifact rendered a percent")


def scenario_progress_tuple(manifest, tmp):
    """GRAPH-03 over real appended lifecycle events."""
    log = os.path.join(tmp, "progress-evidence.jsonl")
    appended = 0
    for index, subject in enumerate(corpus.SUBJECTS):
        notes.strategy_lifecycle_event(
            log, "activity_completed" if index % 2 == 0
            else "activity_skipped", "s-%s" % subject,
            "guided_note_spine",
            "completed" if index % 2 == 0 else "skipped_optional",
            "note-%d" % index)
        appended += 1
    MEASURED["lifecycle_events_appended"] = appended

    snapshot = tuple(evidence.capture_events(log))
    if len(snapshot) != appended:
        fail("the captured snapshot holds %d of %d appended events"
             % (len(snapshot), appended))
    course_records = {
        "emt.obj.1": {"membership": "required", "designed": 4, "cited": 3,
                      "complete": True, "retention_state": "stable"},
        "emt.obj.2": {"membership": "required_choice", "designed": 0,
                      "cited": 1, "complete": False,
                      "retention_state": "weak"},
        "emt.obj.3": {"membership": "enrichment", "designed": 5, "cited": 2,
                      "complete": False, "retention_state": "unknown"},
        "emt.obj.4": {"membership": "required", "designed": 2, "cited": 2,
                      "complete": False, "version_split": True,
                      "retention_state": "unknown"},
    }
    snapshot = snapshot + (
        {"event_type": "response", "event_id": "r1", "score": True},
        {"event_type": "response", "event_id": "r2", "score": None},
        {"event_type": "mark", "response_event_id": "r1"})
    claims = pc.claims_from_events(snapshot, course_records)
    fills = [pc.fill_state("emt.obj.1", 3, "stable"),
             pc.fill_state("emt.obj.2", 3, "due")]
    text = pc.render_claims_text(claims, fills)
    MEASURED["progress_block"] = text

    if "%" in text:
        fail("the progress block rendered a percent")
    lowered = text.lower()
    for word in ("overall", "readiness", "retrievability"):
        if word in lowered:
            fail("the progress block carries %r" % word)
    for label in pc.DIMENSION_LABELS.values():
        if text.count(label) != 1:
            fail("%r appears %d times in the progress block"
                 % (label, text.count(label)))
    for needle in ("Indeterminate:", "pending review",
                   "Earlier evidence stays with the earlier version."):
        if needle not in text:
            fail("the progress block is missing %r" % needle)
    if "activities completed rather than skipped" not in text:
        fail("the lifecycle events did not reach the participation row")


def scenario_trio(manifest, tmp):
    """The trio's own proofs and the three prototype gates, run here rather
    than trusted from their suite."""
    import note_trio_roundtrip as trio
    before = len(trio.FAILURES)
    for name in ("check_parse_once", "check_plain_coherence",
                 "check_validators_fail_meaningfully",
                 "check_good_instance_passes",
                 "scenario_a_guided_note_spine",
                 "scenario_b_worked_reasoning",
                 "scenario_c_provenance_relocation"):
        getattr(trio, name)()
    new = trio.FAILURES[before:]
    for message in new:
        fail("trio %s" % message)
    MEASURED["trio_functions_run"] = 7


def scenario_upgrade(manifest, tmp):
    """UPGRADE-01 and UPGRADE-02 over the legacy fixture, bytes untouched."""
    import hashlib
    digest = hashlib.sha256(open(LEGACY, "rb").read()).hexdigest()
    rows = upgrade_audit.baseline_audit(LEGACY)
    if len(rows) != 11:
        fail("the baseline audit returned %d rows" % len(rows))
    if [r["item"] for r in rows] != list(upgrade_audit.BASELINE_AUDIT_ITEMS):
        fail("the audit rows are out of order")
    diff = upgrade_audit.bounded_diff(LEGACY, [
        {"before": "states", "after": "conditions",
         "reason": "names the distinction the item tests"},
        {"before": "spoken", "after": "verbal", "reason": "cosmetic"}])
    if len(diff["proposed"]) != 1 or len(diff["skipped"]) != 1:
        fail("the bounded diff produced %r" % diff)
    if diff["skipped"][0]["copy"] != "Skipped: no learning value added.":
        fail("the skip sentence is %r" % diff["skipped"][0]["copy"])
    halted = upgrade_audit.run_upgrade(LEGACY, [
        {"before": "CORRECT: B\n\nWHY BEST: The spoken",
         "after": "CORRECT: A\n\nWHY BEST: The spoken",
         "reason": "a stated reason"}])
    if not halted.get("halted"):
        fail("a flipped key did not halt")
    elif "keyed content" not in halted["copy"]:
        fail("the halt does not name what moved: %r" % halted["copy"])
    if "diff" in halted:
        fail("a halted upgrade offered a diff")
    if hashlib.sha256(open(LEGACY, "rb").read()).hexdigest() != digest:
        fail("the upgrade run modified the legacy fixture")


def scenario_registry_consistency(manifest, tmp):
    """The deliberate duplications are still equal, and the event tuple is
    the size the freeze will claim."""
    if notes._REGISTERED_STRATEGY_IDS != strategies.STRATEGY_IDS:
        fail("notes.py's local strategy tuple %r has drifted from "
             "strategies.STRATEGY_IDS %r"
             % (notes._REGISTERED_STRATEGY_IDS, strategies.STRATEGY_IDS))
    if len(evidence.KNOWN_EVENT_TYPES) != 17:
        fail("KNOWN_EVENT_TYPES holds %d members, expected 17"
             % len(evidence.KNOWN_EVENT_TYPES))
    if evidence.EVENT_SCHEMA_VERSION != 2:
        fail("EVENT_SCHEMA_VERSION is %r" % evidence.EVENT_SCHEMA_VERSION)
    if set(notes.STRATEGY_LIFECYCLE_EVENT_TYPES) - \
            set(evidence.KNOWN_EVENT_TYPES):
        fail("a lifecycle event type is not registered in the evidence store")
    if strategies.LIFECYCLE_EVENT_TYPES != \
            notes.STRATEGY_LIFECYCLE_EVENT_TYPES:
        fail("the strategy registry and the note store name different "
             "lifecycle types")
    if set(note_outputs.NOTE_OUTPUT_CHECKS.values()) != {"error"}:
        fail("a trio check declares no severity")


SCENARIOS = (
    ("scenario_strategy_fallback", scenario_strategy_fallback),
    ("scenario_conflict_matrix", scenario_conflict_matrix),
    ("scenario_note_anchor", scenario_note_anchor),
    ("scenario_promotion_pair", scenario_promotion_pair),
    ("scenario_pending_artifact", scenario_pending_artifact),
    ("scenario_progress_tuple", scenario_progress_tuple),
    ("scenario_trio", scenario_trio),
    ("scenario_upgrade", scenario_upgrade),
    ("scenario_registry_consistency", scenario_registry_consistency),
)


def main():
    if not os.path.exists(CLOSURE_13_9):
        print(HALT_13_9)
        sys.exit(1)

    tmp = tempfile.mkdtemp(prefix="itembank-16C-tracer-")
    started = time.monotonic()
    try:
        manifest = corpus.build_all(tmp)
        MEASURED["subjects"] = {}
        for subject, path in manifest.items():
            lesson = model.parse_lesson(path)
            terms = model.parse_terms(path)
            MEASURED["subjects"][subject] = {
                "items": len(model.load(path)),
                "headings": len(lesson["headings"]),
                "terms": len(terms["terms"]),
                "relations": len(corpus.typed_relations(subject)),
            }
        for name, scenario in SCENARIOS:
            before = len(FAILURES)
            scenario_started = time.monotonic()
            scenario(manifest, tmp)
            elapsed = time.monotonic() - scenario_started
            state = "passed" if len(FAILURES) == before else "FAILED"
            MEASURED.setdefault("scenarios", {})[name] = round(elapsed, 3)
            print("  %-32s %s  %.3fs" % (name, state, elapsed))
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)

    total = time.monotonic() - started
    MEASURED["elapsed"] = round(total, 3)
    MEASURED["platform"] = "%s %s" % (platform.system(), platform.release())
    MEASURED["python"] = platform.python_version()
    failed = len(FAILURES)
    print("CROSS-SUBJECT SUITE: %d passed, %d failed"
          % (len(SCENARIOS) - failed, failed))
    print("elapsed: %.3fs" % total)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
