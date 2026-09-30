#!/usr/bin/env python3
"""The isolated tutor only consumes runtime releases and preserves context."""
import importlib.util
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))
import course
import graph
import model
from surfaces import session
from a3_course_workflows_roundtrip import seed, tree_hash
from formal_assessment_connected_roundtrip import temporary_bank

spec = importlib.util.spec_from_file_location("a3_tutor", ROOT / "prototypes/audit-course-tutor/tutor.py")
tutor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tutor)


def run(mode):
    with tempfile.TemporaryDirectory(prefix="a3-tutor-") as base:
        first, second, source = seed(base)
        bank = temporary_bank(base)
        question = model.load(bank)[0]
        read = course.read_course(base)
        doc = read["doc"]
        graph.add_objective(doc, "Synthetic tutor target", objective_id=question["objective"])
        course.write_course(base, doc, read["fingerprint"], "human", "test")
        course.bind_source(base, question["objective"], source["object_id"], "Source", "covered", "high", "human", "test")
        attempt = os.path.join(base, "_attempts", "session_tutor.json")
        started = session.do_start(bank, {"count": 2, "seed": 0, "selection_mode": "exam", "type_counts": {"mc": 1, "short": 1}}, mode, attempt, False)
        assert started["item"]["type"] == "mc"
        if mode == "practice":
            response = session.do_submit(attempt, "A", None)
            assert response["accepted"]
            session.do_teach(attempt, "hint")
        before = tree_hash(base)
        payload = tutor.context(base, attempt, "formal_synthetic")
        page = tutor.render(payload)
        assert payload["session_id"] == started["session_id"]
        assert "session=" + started["session_id"] in page and "mode=" + mode in page
        assert "CORRECT:" not in page and "WHY BEST:" not in page and "DISTRACTOR ANALYSIS:" not in page
        if mode == "exam":
            assert not payload["teaching"]["available"] and not payload["citations"]
        else:
            assert payload["teaching"]["available"]
            assert payload["teaching"]["shown"] and payload["citations"]
            assert "A source stays useful as direct reading" in page
        assert tree_hash(base) == before


if __name__ == "__main__":
    run("exam")
    run("practice")
    print("A3 cited tutor prototype: read-only runtime release, formal refusal and exact sitting return passed")
