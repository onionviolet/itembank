#!/usr/bin/env python3
"""Phase 16C (16C-07) note-output trio roundtrip and prototype tracers.

Direct standard-library roundtrip script in the project's established shape:
`fail(msg)` and a non-zero exit on failure.

It proves the STYLE-DISCIPLINE bar the trio has to clear before any further
output mode may register: three modes are three projections of ONE parse
(counted, not asserted), each degrades to coherent plain Markdown, each
validator fails in its own words on its own deliberately broken fixture, and
the three prototype tracers A, B, and C hold.

The degraded state this file exists to prove is interruption safety: a
corrupt temp file planted after the second write leaves both accepted notes
readable and still anchored, which is prototype A's no-note-loss gate.
"""
import ast
import copy as copy_mod
import io
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import model
import note_outputs
import notes
from fixtures import note_strategy_corpus as corpus

FAILURES = []


def fail(msg):
    print("FAIL: %s" % msg)
    FAILURES.append(msg)


def _instance(bank, notes_list, relations):
    return note_outputs.content_instance(
        model.parse_lesson(bank), model.parse_terms(bank), relations,
        notes_list)


def _anchor(heading, role, wording, owner="local"):
    digest = notes.hash_quoted_context(heading["body"])
    target = notes.target_record("lesson_step", heading["slug"], digest,
                                 "heading:%s" % heading["slug"], digest)
    return notes.note_record("course-emt", ["emt.obj.1"], role, wording,
                             [target], owner=owner)


def _fixture(tmp, subject="emt_respiratory"):
    bank = corpus.build_subject_bank(subject, tmp)
    lesson = model.parse_lesson(bank)
    headings = lesson["headings"]
    made = []
    for raw in corpus.build_note_set(subject, headings):
        heading = [h for h in headings if h["slug"] == raw["anchor_slug"]][0]
        made.append(_anchor(heading, raw["epistemic_role"],
                            raw["learner_wording"]))
    return bank, headings, made


def check_parse_once():
    """All three outputs come from one parse. Counted through the real
    parsers, because the claim is about calls, not intentions."""
    tmp = tempfile.mkdtemp()
    real_lesson, real_terms = model.parse_lesson, model.parse_terms
    counts = {"lesson": 0, "terms": 0}
    try:
        bank, headings, made = _fixture(tmp)

        def counting_lesson(path):
            counts["lesson"] += 1
            return real_lesson(path)

        def counting_terms(path):
            counts["terms"] += 1
            return real_terms(path)

        model.parse_lesson = counting_lesson
        model.parse_terms = counting_terms
        try:
            instance = note_outputs.content_instance(
                model.parse_lesson(bank), model.parse_terms(bank),
                corpus.typed_relations("emt_respiratory"), made)
            for _ in range(2):
                for mode in note_outputs.OUTPUT_MODES:
                    note_outputs.render_mode(mode, instance, headings)
        finally:
            model.parse_lesson, model.parse_terms = real_lesson, real_terms

        if counts != {"lesson": 1, "terms": 1}:
            fail("six renders cost %r parses, expected one each" % (counts,))
    finally:
        model.parse_lesson, model.parse_terms = real_lesson, real_terms
        shutil.rmtree(tmp, ignore_errors=True)


def check_no_content_fork():
    """One source of truth: change the instance, every projection changes."""
    tmp = tempfile.mkdtemp()
    try:
        bank, headings, made = _fixture(tmp)
        relations = corpus.typed_relations("emt_respiratory")
        instance = _instance(bank, made, relations)
        before = dict((m, note_outputs.PROJECTIONS[m](instance))
                      for m in note_outputs.OUTPUT_MODES)

        changed = copy_mod.deepcopy(instance)
        original_wording = changed["notes"][0]["learner_wording"]
        changed["notes"][0]["learner_wording"] = "An entirely different note."
        after = dict((m, note_outputs.PROJECTIONS[m](changed))
                     for m in note_outputs.OUTPUT_MODES)

        if original_wording not in before["notebook_page"]:
            fail("the notebook page did not carry the original wording")
        if "An entirely different note." not in after["notebook_page"]:
            fail("the notebook page did not follow the changed instance")
        if original_wording in after["notebook_page"]:
            fail("a projection cached the original wording")
        for mode in note_outputs.OUTPUT_MODES:
            if note_outputs.PROJECTIONS[mode](instance) != before[mode]:
                fail("%s is not a pure function of its instance" % mode)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check_plain_coherence():
    """Each projection stands alone as Markdown, with no markup at all."""
    tmp = tempfile.mkdtemp()
    try:
        bank, headings, made = _fixture(tmp)
        instance = _instance(bank, made,
                             corpus.typed_relations("emt_respiratory"))
        rendered = dict((m, note_outputs.PROJECTIONS[m](instance))
                        for m in note_outputs.OUTPUT_MODES)
        for mode, text in rendered.items():
            if not text.strip():
                fail("%s rendered nothing" % mode)
                continue
            if not text.split("\n")[0].startswith("# "):
                fail("%s does not open with a heading: %r"
                     % (mode, text.split("\n")[0]))
            if "<" in text and ">" in text:
                fail("%s carries markup; the plain form is Markdown" % mode)
        labels = notes.CAPTURE_COPY["role_choices"]
        if not any(l in rendered["notebook_page"] for l in labels):
            fail("the notebook page carries no role label")
        if "(owner: " not in rendered["notebook_page"]:
            fail("the notebook page does not show ownership per block")
        if "Provenance: " not in rendered["notebook_page"]:
            fail("the notebook page does not show provenance per block")
        if "## Summary" not in rendered["cornell_notes"]:
            fail("Cornell notes carry no summary region")
        if "## Cue: " not in rendered["cornell_notes"]:
            fail("Cornell notes carry no cues")
        if rendered["concept_map"].count("relates to ") < 4:
            fail("the concept map carries %d edges, expected at least 4"
                 % rendered["concept_map"].count("relates to "))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check_no_file_reads():
    """The module cannot reach around the one seam to a file."""
    tree = ast.parse(open(os.path.join(ROOT, "note_outputs.py"),
                         encoding="utf-8").read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                and node.func.id == "open":
            fail("note_outputs.py opens a file; every projection reads the "
                 "instance the caller parsed")
        if isinstance(node, ast.Import):
            names = [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            names = [node.module or ""]
        else:
            continue
        for name in names:
            head = name.split(".")[0]
            if head in ("runtime", "evidence") or head == "surfaces":
                fail("note_outputs.py imports %s" % name)


def check_validators_fail_meaningfully():
    """Each broken fixture fails its own check, in the validator's words."""
    tmp = tempfile.mkdtemp()
    try:
        fixtures = corpus.broken_trio_fixtures(tmp)
        bank = fixtures["bank"]
        lesson = model.parse_lesson(bank)
        terms = model.parse_terms(bank)
        wanted = {
            "cornell": ("cornell_notes", "note_output.cue_without_notes",
                        "The Cornell notes view can't be built from this "
                        "content: a cue has no matching notes. Showing plain "
                        "Markdown instead."),
            "concept_map": ("concept_map", "note_output.edge_untyped",
                            "The Concept map view can't be built from this "
                            "content: a relation has no type. Showing plain "
                            "Markdown instead."),
            "notebook": ("notebook_page", "note_output.anchor_moved",
                         "The Notebook page view can't be built from this "
                         "content: an anchor points to a block that moved. "
                         "Showing plain Markdown instead."),
        }
        for key, (mode, code, sentence) in wanted.items():
            case = fixtures[key]
            instance = note_outputs.content_instance(
                lesson, terms, case["relations"], case["notes"])
            failures = note_outputs.validate_mode(mode, instance,
                                                  case["headings"])
            codes = set(f["code"] for f in failures)
            if code not in codes:
                fail("the %s fixture produced %r, expected %r"
                     % (key, sorted(codes), code))
            result = note_outputs.render_mode(mode, instance,
                                              case["headings"])
            if result["ok"]:
                fail("the %s fixture rendered ok" % key)
                continue
            if result["copy"] != sentence:
                fail("the %s refusal is %r" % (key, result["copy"]))
            if not result["text"].strip():
                fail("the %s refusal lost the content" % key)
            if not result["text"].split("\n")[0].startswith("# "):
                fail("the %s refusal did not carry a plain document" % key)

        if set(note_outputs.NOTE_OUTPUT_CHECKS) != {
                "note_output.ownership_missing", "note_output.anchor_moved",
                "note_output.provenance_missing",
                "note_output.cue_without_notes",
                "note_output.edge_untyped"}:
            fail("NOTE_OUTPUT_CHECKS is %r"
                 % sorted(note_outputs.NOTE_OUTPUT_CHECKS))
        if set(note_outputs.NOTE_OUTPUT_CHECKS.values()) != {"error"}:
            fail("every check declares a severity in code")

        # Ownership and provenance, the notebook's other two checks.
        case = fixtures["good"]
        ownerless = copy_mod.deepcopy(case["notes"])
        ownerless[0]["owner"] = ""
        instance = note_outputs.content_instance(lesson, terms,
                                                 case["relations"], ownerless)
        codes = set(f["code"] for f in note_outputs.validate_mode(
            "notebook_page", instance, case["headings"]))
        if "note_output.ownership_missing" not in codes:
            fail("an ownerless block passed the notebook validator")

        locatorless = copy_mod.deepcopy(case["notes"])
        locatorless[0]["targets"][0]["locator"] = ""
        instance = note_outputs.content_instance(
            lesson, terms, case["relations"], locatorless)
        codes = set(f["code"] for f in note_outputs.validate_mode(
            "notebook_page", instance, case["headings"]))
        if "note_output.provenance_missing" not in codes:
            fail("a block with no locator passed the notebook validator")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check_good_instance_passes():
    """The unbroken instance validates clean in all three modes."""
    tmp = tempfile.mkdtemp()
    try:
        fixtures = corpus.broken_trio_fixtures(tmp)
        case = fixtures["good"]
        instance = note_outputs.content_instance(
            model.parse_lesson(fixtures["bank"]),
            model.parse_terms(fixtures["bank"]),
            case["relations"], case["notes"])
        for mode in note_outputs.OUTPUT_MODES:
            result = note_outputs.render_mode(mode, instance,
                                              case["headings"])
            if not result["ok"]:
                fail("the good instance failed %s: %r"
                     % (mode, result.get("failures")))
        try:
            note_outputs.validate_mode("mind_map", instance,
                                       case["headings"])
        except ValueError:
            pass
        else:
            fail("an unregistered output mode was validated")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def scenario_a_guided_note_spine():
    """Gate A: no note draft lost, every block returns to source, no key
    anywhere."""
    tmp = tempfile.mkdtemp()
    try:
        bank, headings, _ = _fixture(tmp)
        notes_dir = os.path.join(tmp, notes.NOTES_DIRNAME)
        written = []
        for index in range(3):
            written.append(_anchor(headings[index], "learner_claim",
                                   "Draft note %d about this section."
                                   % (index + 1)))
            sidecar = {"schema_version": notes.NOTE_SCHEMA_VERSION,
                       "note_document_id": "doc-a",
                       "course_id": "course-emt",
                       "notes": written[:2] if index == 2 else list(written)}
            if index == 2:
                # The interruption: the third write is planted as a corrupt
                # temp file rather than completed, so the accepted state is
                # the second write.
                with open(os.path.join(notes_dir, "notes.md.json.tmp"), "w",
                          encoding="utf-8") as fh:
                    fh.write('{"notes": [ this write never finished')
                break
            notes.write_note_document(notes_dir, "course-emt",
                                      "# Notes\n", sidecar)

        read = notes.read_note_document(notes_dir, "course-emt")
        if read is None:
            fail("gate A: the interrupted pass lost the document")
            return
        if len(read["sidecar"]["notes"]) != 2:
            fail("gate A: expected two accepted drafts, got %d"
                 % len(read["sidecar"]["notes"]))

        instance = _instance(bank, read["sidecar"]["notes"],
                             corpus.typed_relations("emt_respiratory"))
        for note in read["sidecar"]["notes"]:
            for target in note["targets"]:
                state = notes.resolve_anchor(target, headings)
                if state["state"] != "resolved":
                    fail("gate A: a block did not return to its source: %r"
                         % (state,))

        page = note_outputs.project_notebook_page(instance)
        if "Provenance: Anchored" not in page:
            fail("gate A: the notebook page does not show the anchor state")

        bank_text = io.open(bank, encoding="utf-8").read()
        keys = [l.split("CORRECT:", 1)[1].strip()
                for l in bank_text.split("\n") if l.startswith("CORRECT:")]
        for mode in note_outputs.OUTPUT_MODES:
            text = note_outputs.PROJECTIONS[mode](instance)
            if "CORRECT:" in text:
                fail("gate A: %s leaked the answer-key marker" % mode)
            for key in keys:
                if key and ("CORRECT: %s" % key) in text:
                    fail("gate A: %s leaked an answer key" % mode)
            for marker in ("WHY BEST:", "KEY DISCRIMINATOR:", "MODEL:",
                           "RUBRIC:"):
                if marker in text:
                    fail("gate A: %s leaked %s" % (mode, marker))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def scenario_b_worked_reasoning():
    """Gate B: a wrong explanation stays a labeled claim and cannot seed a
    key."""
    tmp = tempfile.mkdtemp()
    try:
        bank = corpus.build_subject_bank("cs_loop_invariant", tmp)
        headings = model.parse_lesson(bank)["headings"]
        wrong = _anchor(headings[1], "learner_claim",
                        "The invariant is false after the second pass, so "
                        "the loop is what is broken.")
        instance = _instance(bank, [wrong],
                             corpus.typed_relations("cs_loop_invariant"))

        page = note_outputs.project_notebook_page(instance)
        if "**My claim**" not in page:
            fail("gate B: the wrong explanation lost its role label")
        block = page[page.find("**My claim**"):]
        lowered = block.lower()
        for marker in ("correct", "verdict", "score"):
            if marker in lowered:
                fail("gate B: the block carries a %r marker" % marker)

        result = notes.review_promotion(
            notes.request_review(wrong),
            [{"text": wrong["learner_wording"], "source_id": ""}], set(), [],
            "accept", "Weibao")
        if result["outcome"] != "blocked":
            fail("gate B: an unsourced wrong claim produced %r"
                 % result["outcome"])
        elif result["copy"] != ("Every keyed or factual claim needs an "
                                "accepted source. 1 claims have no accepted "
                                "source yet."):
            fail("gate B: the block sentence is %r" % result["copy"])
        if "derived" in result:
            fail("gate B: a blocked claim produced a derived record")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def scenario_c_provenance_relocation():
    """Gate C: exact, probable without auto-apply, orphan, and ownership
    surviving export and reimport."""
    tmp = tempfile.mkdtemp()
    try:
        bank, headings, _ = _fixture(tmp)
        anchored = [_anchor(headings[i], "learner_claim",
                            "Claim about section %d." % i, owner="weibao")
                    for i in range(3)]

        # (a) renamed heading, same body.
        renamed = [dict(h) for h in headings]
        renamed[0] = dict(renamed[0], slug=renamed[0]["slug"] + "-renamed")
        state = notes.resolve_anchor(anchored[0]["targets"][0], renamed)
        if state["state"] != "relocated_exact" or len(state["candidates"]) != 1:
            fail("gate C: a renamed heading read %r" % (state,))

        # (b) same title, different body: probable, and nothing auto-applies.
        revised = [dict(h) for h in headings]
        revised[1] = dict(revised[1],
                          body="Entirely different invented prose.")
        state = notes.resolve_anchor(anchored[1]["targets"][0], revised)
        if state["state"] != "relocated_probable":
            fail("gate C: a revised body read %r" % (state,))
        notes_dir = os.path.join(tmp, notes.NOTES_DIRNAME)
        sidecar = {"schema_version": notes.NOTE_SCHEMA_VERSION,
                   "note_document_id": "doc-c",
                   "course_id": "course-emt",
                   "notes": anchored}
        notes.write_note_document(notes_dir, "course-emt", "# Notes\n",
                                  sidecar)
        stored = notes.read_note_document(notes_dir, "course-emt")
        notes.resolve_anchor(anchored[1]["targets"][0], revised)
        after = notes.read_note_document(notes_dir, "course-emt")
        if stored["sidecar"] != after["sidecar"]:
            fail("gate C: resolving a probable relocation rewrote the "
                 "stored document")

        # (c) deleted heading: orphaned, objective retained.
        remaining = [h for h in headings if h["slug"] !=
                     anchored[2]["targets"][0]["stable_id"]]
        state = notes.resolve_anchor(anchored[2]["targets"][0], remaining)
        if state["state"] != "orphaned":
            fail("gate C: a deleted heading read %r" % (state,))
        if not anchored[2]["objective_ids"]:
            fail("gate C: an orphaned note lost its objective")

        # Export and reimport, byte for byte.
        exported = os.path.join(tmp, "exported")
        os.makedirs(exported, exist_ok=True)
        for name in ("notes.md", "notes.md.json"):
            shutil.copyfile(os.path.join(notes_dir, name),
                            os.path.join(exported, name))
        reimported = notes.read_note_document(exported, "course-emt")
        if reimported is None:
            fail("gate C: the exported document did not reimport")
            return
        if reimported["sidecar"] != stored["sidecar"]:
            fail("gate C: export and reimport changed the document")
        for note in reimported["sidecar"]["notes"]:
            if note["owner"] != "weibao":
                fail("gate C: ownership was lost in export: %r"
                     % note["owner"])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    checks = [check_parse_once, check_no_content_fork, check_plain_coherence,
              check_no_file_reads, check_validators_fail_meaningfully,
              check_good_instance_passes, scenario_a_guided_note_spine,
              scenario_b_worked_reasoning, scenario_c_provenance_relocation]
    for check in checks:
        check()
    failed = len(FAILURES)
    print("NOTE TRIO: %d passed, %d failed" % (len(checks) - failed, failed))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
