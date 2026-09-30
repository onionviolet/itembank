#!/usr/bin/env python3
"""Home highlights a known sitting without manufacturing recency or progress."""
import copy
import os
import sys
import tempfile
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from surfaces import daemon


def check_served_home(hold=False):
    import course
    import runtime
    import sample_course
    from surfaces import ia, session
    from daemon_roundtrip import start_daemon, get

    with tempfile.TemporaryDirectory(prefix="desk_experience_") as temp:
        root = Path(temp)
        directory = root / "study"
        sample_course.write_sample_course(str(directory))
        for name in ("Synthetic logic and proof workshop", "Synthetic field ecology: long course titles remain readable",
                     "Synthetic code tracing"):
            dest = root / name.split()[1]
            dest.mkdir()
            course.create_course(str(dest), name, "agent", "test")
        course_id = course.read_course(str(directory))["object_id"]
        state = ia.course_shelf_state(temp)
        ids = [row["course_id"] for row in state["cards"] if row["course_id"] != course_id] + [course_id]
        result = ia.reorder_shelf(temp, ids, state.get("workspace_fingerprint"))
        assert result["ok"], result
        bank = directory / "study_skills_sample.md"
        attempts = root / "_attempts"
        attempts.mkdir(exist_ok=True)
        session.do_start(str(bank), {"objective": "", "count": 3, "seed": 0,
                                   "selection_mode": "practice"}, "practice",
                         str(attempts / "session_synthetic.json"), False,
                         preset_session_id="synthetic")
        proc, url, _ = start_daemon(temp)
        try:
            before = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()}
            status, body = get(url)
            assert status == 200
            hero = body.split('<section class="desk-focus"', 1)[1].split('</section>', 1)[0]
            assert "Continue a saved session" in hero
            total = len(runtime.read_session(str(attempts / "session_synthetic.json"))["items"])
            assert "Practice · Question 1 of %d" % total in hero
            assert "session=synthetic" in hero and "course=" + course_id in hero
            status, courses = get(url + "courses")
            assert status == 200 and "data-drag-handle" in courses
            after = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()}
            assert before == after, "viewing Home or Courses wrote learner state"
            if hold:
                print("Synthetic desk: " + url, flush=True)
                input("Press Enter after browser review to close the disposable server.\n")
        finally:
            proc.terminate()
            proc.wait(timeout=5)


def card(name, state="absent", position=2, total=6, mode="practice"):
    return {"course_id": name, "name": name, "attention": "up_to_date",
            "token": "ready", "chip": "Up to date", "resume_cue": "Session in progress",
            "cta_href": "/quiz/fixture?session=" + name if state == "active" else "/course/" + name,
            "cta_label": ("Resume " if state == "active" else "Start ") + name,
            "actions": (), "degraded": False,
            "resume": {"state": state, "sessions": (
                {"status": "active", "position": position, "total": total, "mode": mode},)}}


def check_focus_and_authority():
    cards = [card("first"), card("saved", "active"), card("other", "active")]
    before = copy.deepcopy(cards)
    shelf = {"cards": cards, "reorderable": True, "workspace_fingerprint": "base"}
    page = daemon._course_shelf_body(shelf)
    hero = page.split('<section class="desk-focus"', 1)[1].split('</section>', 1)[0]
    assert '<h2 id="desk-focus-title">saved</h2>' in hero
    assert 'Continue a saved session' in hero
    assert 'Practice · Question 3 of 6' in hero
    assert 'href="/quiz/fixture?session=saved"' in hero
    assert cards == before, "presentation changed canonical input"
    assert page.index('data-course-id="first"') < page.index('data-course-id="saved"')
    assert daemon._desk_focus_card([cards[2], cards[1]]) is cards[2]
    assert daemon._desk_focus_card([cards[0]]) is cards[0]
    assert daemon._desk_focus_card([]) is None
    ambiguous = card("multiple", "ambiguous")
    assert daemon._desk_focus_card([ambiguous, cards[1]]) is cards[1]
    assert 'Question' not in daemon._desk_hero(ambiguous)
    invalid_route = card("unroutable", "active")
    invalid_route["cta_href"] = "/course/unroutable"
    assert daemon._desk_focus_card([invalid_route, cards[1]]) is cards[1]


def check_unknown_positions():
    for position, total, mode in ((True, 6, "practice"), (-1, 6, "practice"),
                                  (6, 6, "practice"), (2, 0, "practice"),
                                  (2, 6, "unknown"), (2, "6", "exam")):
        assert daemon._desk_session_context(card("bad", "active", position, total, mode)) == ""
    assert daemon._desk_session_context(card("exam", "active", 0, 4, "exam")) == "Test · Question 1 of 4"


if __name__ == "__main__":
    check_focus_and_authority()
    check_unknown_positions()
    check_served_home("--browser-hold" in sys.argv)
    print("desk experience: canonical sitting, course-order tie-break and unknown positions ok")
