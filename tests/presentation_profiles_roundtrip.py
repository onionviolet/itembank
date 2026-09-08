#!/usr/bin/env python3
"""Phase 20 deterministic contract for the two presentation recipes.

This fixture uses public presentation data only. It deliberately does not
start a real sitting or read a real learner's evidence.
"""
import os
import json
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from model import load
import runtime
from surfaces import daemon, ia, presentation, quiz, quiz_page, settings, study, theme


def fail(message):
    raise AssertionError(message)


def ok(message):
    print("ok: " + message)


def fixture(response_type="mc", purpose="practice"):
    return presentation.semantic_view(
        application="itembank", course="Synthetic Algebra", location="Practice",
        purpose=purpose, response_type=response_type, disclosure="now",
        position="Item 2 of 5", source="Synthetic source", content=(
            '<form method="post" action="/answer/synthetic">'
            '<input name="option" value="A"><button type="submit">Submit answer</button></form>'),
        next_action={"label": "Submit answer", "href": "/answer/synthetic"},
        status={"label": "Recovery", "kind": "warn", "text": "Resume safely."})


def check_profile_parity():
    view = fixture()
    guide = presentation.render_profile(view, "field-guide")
    deck = presentation.render_profile(view, "trajectory-deck")
    for text in ("Application: itembank", "Synthetic Algebra", "Practice",
                 "Purpose", "Response format", "Disclosure", "Position",
                 "Single choice", "Feedback available now", "Item 2 of 5",
                 "Synthetic source", "Resume safely."):
        if text not in guide or text not in deck:
            fail("profile lost semantic text %r" % text)
    for token in ('action="/answer/synthetic"', 'name="option"',
                  'href="/answer/synthetic"'):
        if guide.count(token) != deck.count(token):
            fail("profile changed behavior token %r" % token)
    if 'data-presentation-profile="field-guide"' not in guide or \
       'data-presentation-profile="trajectory-deck"' not in deck:
        fail("profile identity is not exposed")
    if 'ib-profile-guide-main' not in guide or 'ib-profile-deck-task' not in deck:
        fail("profiles did not provide distinct composition landmarks")
    if guide.index('ib-source') > guide.index('actions') or \
       deck.index('ib-profile-deck-task') > deck.index('ib-source'):
        fail("profile composition lost its distinct source and task priority")
    ok("both recipes preserve public content, hrefs, form action, and response name")


def check_activity_separation():
    for purpose, label in presentation.ACTIVITY_PURPOSE_LABELS.items():
        text = presentation.render_profile(fixture(purpose=purpose))
        if label not in text:
            fail("purpose %s lacks %s" % (purpose, label))
    for response_type, label in presentation.RESPONSE_FORMAT_LABELS.items():
        text = presentation.render_profile(fixture(response_type=response_type))
        if label not in text:
            fail("response type %s lacks %s" % (response_type, label))
    if "Activity" in presentation.activity_frame(fixture()):
        fail("learner activity frame must not borrow capitalized durable-job Activity")
    ok("all purpose values remain separate from all shipped response formats")


def check_response_type_presentation_matrix():
    """All canonical types keep one schema and gain presentation guidance."""
    expected = {
        "mc": ("Single choice", "Choose one option."),
        "multi": ("Multiple choice", "Choose the requested number of options."),
        "table": ("Table response", "Choose one category for every row."),
        "build": ("Build response", "Select every step in the order it should happen."),
        "dnd": ("Ordering or matching", "Dragging is not required."),
        "short": ("Short response", "stays pending until a marker reviews it"),
        "visual": ("Visual interaction", "adjacent keyboard controls"),
        "check": ("Code check", "runtime records the verdict"),
    }
    schema = json.load(open(os.path.join(ROOT, "schemas", "item.schema.json"),
                            encoding="utf-8"))
    if set(expected) != set(schema["properties"]["type"]["enum"]):
        fail("fixture matrix drifted from runtime item types")
    if quiz_page.RESPONSE_FORMAT_LABELS != {
            key: presentation.RESPONSE_FORMAT_LABELS[key] for key in expected}:
        fail("server-baseline labels drifted from shared presentation labels")
    if quiz_page.RESPONSE_FORMAT_INSTRUCTIONS != {
            key: presentation.RESPONSE_FORMAT_INSTRUCTIONS[key] for key in expected}:
        fail("server-baseline instructions drifted from shared presentation instructions")
    public = {}
    for name in ("sample_bank.md", "check_bank.md", "visual_bank.md"):
        for question in load(os.path.join(ROOT, "fixtures", name)):
            public.setdefault(question["type"], runtime.public_item(question))
    if set(public) != set(expected):
        fail("public fixture matrix does not cover all canonical response types")
    schema_types = {
        "mc": "string", "multi": "array", "table": "object",
        "build": "array", "dnd": "object", "short": "string",
        "visual": "object", "check": "string",
    }
    for response_type, item in public.items():
        if item["response_schema"].get("type") != schema_types[response_type]:
            fail("%s response schema changed shape" % response_type)
    if public["check"]["response_schema"].get("format") != "source" or \
       public["check"].get("interaction_contract", {}).get("type") != "check":
        fail("code check stopped being an activity contract over a source response")
    source = open(os.path.join(ROOT, "surfaces", "quiz_page.py"), encoding="utf-8").read()
    for response_type, (label, instruction) in expected.items():
        if presentation.RESPONSE_FORMAT_LABELS.get(response_type) != label:
            fail("response type %s lost learner-facing label" % response_type)
        if instruction not in presentation.RESPONSE_FORMAT_INSTRUCTIONS.get(response_type, ""):
            fail("response type %s lost its instruction" % response_type)
        if label not in source or instruction not in source:
            fail("quiz clients do not carry %s presentation copy" % response_type)
        for profile in presentation.PROFILE_RECIPES:
            page = presentation.render_profile(fixture(response_type=response_type), profile)
            if label not in page:
                fail("%s profile lost %s label" % (profile, response_type))
    for token in ('body.className = `response-body response-${q.type}`',
                  '.response-table,.response-dnd,.response-visual,.response-check',
                  'overflow-x:auto', 'overscroll-behavior-inline:contain',
                  'role="status"', 'aria-live="polite"',
                  'data-server-baseline'):
        if token not in source:
            fail("response presentation contract omitted %r" % token)
    if "Recorded, and waiting on a mark." not in source or \
       "Not correct. Your answer was recorded." not in source:
        fail("pending and incorrect states are not visibly distinct")
    if source.count("function asCheck(q, body, act, card)") != 2:
        fail("code check must remain one capability in each existing client")
    visual = {"type": "visual", "id": "q8", "stem": "Place the point.",
              "response_schema": {"type": "string"}}
    baseline = quiz_page.baseline_for(
        {"item": visual, "session_id": "synthetic"}, {}, "/answer",
        {"submit": "token", "hint": "hint", "stumped": "stumped"})
    for token in ("Visual interaction", "adjacent keyboard controls",
                  "Enable JavaScript", "No response has been recorded"):
        if token not in baseline:
            fail("visual no-script fallback omitted %r" % token)
    if "Submit answer" in baseline or 'name="answer"' in baseline:
        fail("visual no-script fallback rendered a dead response control")
    ok("eight response types keep labels, instructions, profiles, pending/error states, and local overflow")


def check_migration_fallback_and_preview():
    with tempfile.TemporaryDirectory() as root:
        cfg = settings.load_settings(root)
        profile, notice = settings.resolve_presentation_profile(cfg)
        if profile != "field-guide" or notice is not None:
            fail("missing setting did not migrate to field-guide")
        cfg["presentation_profile"] = "removed-profile"
        settings.write_settings(root, cfg)
        loaded = settings.load_settings(root)
        profile, notice = settings.resolve_presentation_profile(loaded)
        if profile != "field-guide" or not notice or "removed-profile" not in notice:
            fail("unknown saved value did not retain visible fallback")
        before = open(settings.settings_path(root), "rb").read()
        page = theme.theme_page(loaded)
        after = open(settings.settings_path(root), "rb").read()
        if before != after or "data-profile-choice" not in page:
            fail("preview changed saved settings or was not rendered")
        theme.persist_presentation_profile(root, "trajectory-deck")
        saved = settings.load_settings(root)
        if saved["presentation_profile"] != "trajectory-deck":
            fail("supported profile did not save")
        if saved.get("theme") != cfg.get("theme") or saved.get("accent") != cfg.get("accent"):
            fail("profile save reset an appearance axis")
    ok("missing migration, invalid fallback, preview-without-save, and axis independence")


def check_state_labels():
    expected = {
        "empty": "Choose another bank", "loading": "Loading course",
        "unavailable": "Offline help remains available", "conflict": "Inspect changes",
        "interrupted": "Resume the same session", "pending": "Continue course",
        "invalid": "Save a supported profile", "recovery": "Retry from last accepted state",
    }
    for state, action in expected.items():
        markup = presentation.status_notice(state + " state", "warn", state)
        if state not in markup:
            fail("state label %s is not visible" % state)
        if not action:
            fail("state %s lacks a documented recovery action" % state)
    ok("distinct degraded-state labels have explicit recovery vocabulary")


def check_course_transition_and_degraded_state_contract():
    """Synthetic state rows are explicit and cannot mutate a sitting."""
    expected = {
        "empty": ("Nothing has been added", "/course/synthetic"),
        "loading": ("Loading Learn", "/course/synthetic"),
        "unavailable": ("unavailable right now", "/help/ia.offline"),
        "conflict": ("Nothing was overwritten", "/course/synthetic"),
        "interrupted": ("Resume the same session", "/course/synthetic"),
        "pending": ("pending review", "/course/synthetic"),
        "invalid": ("safe fallback", "/settings"),
        "recovery": ("last accepted course state", "/course/synthetic"),
    }
    for state, (notice, href) in expected.items():
        row = ia.course_area_notice("synthetic", "learn", state)
        if notice not in row["notice"] or row["action_href"] != href:
            fail("course state %s lost its distinct notice or safe action: %r"
                 % (state, row))
    with tempfile.TemporaryDirectory() as root:
        row = ia.course_area_notice("synthetic", "learn", "invalid")
        state = {"course_name": "Synthetic Algebra", "course_id": "synthetic",
                 "area": "learn", "area_label": "Learn", "notice": row["notice"],
                 "display_state": row["state"],
                 "next_action": {"label": row["action_label"],
                                 "href": row["action_href"]},
                 "nav": []}
        page = daemon._course_frame(type("Handler", (), {"root": root, "banks": {}})(),
                                    state, {"href": "/", "label": "Back"})
        for token in ('data-course-state="invalid"', 'href="/settings"',
                      "Save a supported profile"):
            if token not in page:
                fail("course state renderer omitted %r" % token)
    ok("course transitions name distinct degraded states and supported safe actions")


def check_course_lesson_practice_context():
    """The representative navigation slice keeps one course and one bank."""
    with tempfile.TemporaryDirectory() as root:
        course_dir = os.path.join(root, "synthetic.course")
        os.makedirs(course_dir)
        bank = os.path.join(course_dir, "lesson_bank.md")
        shutil.copyfile(os.path.join(ROOT, "fixtures", "lesson_bank.md"), bank)
        original = ia.course_shelf_state
        try:
            ia.course_shelf_state = lambda _root: {
                "cards": [{"course_id": "synthetic"}]}
            original_dir = ia.course_dir_for
            ia.course_dir_for = lambda _root, cid: (
                course_dir if cid == "synthetic" else None)
            links = daemon._lesson_context_nav(
                type("Handler", (), {"root": root})(), bank)
        finally:
            ia.course_shelf_state = original
            ia.course_dir_for = original_dir
        if links != [
                {"href": "/course/synthetic/learn", "label": "Back to course"},
                {"href": "/", "label": "Courses"},
                {"href": "/quiz/lesson_bank", "label": "Continue to practice"}]:
            fail("course, lesson, and practice did not preserve one context: %r" % links)
    for token in ("sessionStorage", "scrollY", "activeId", "beforeunload",
                  "e.returnValue", 'closest("form")'):
        if token not in daemon.RESTORE_SCRIPT:
            fail("course navigation lost locator, focus, or unsaved warning %r" % token)
    ok("course-to-lesson-to-practice preserves course, locator, focus, history, and unsaved warning")


def check_live_surface_output():
    """Study and served Quiz are real renderers, not profile helper output."""
    source = os.path.join(ROOT, "fixtures", "sample_bank.md")
    qs = load(source)
    behavior = {}
    for profile in settings.PRESENTATION_PROFILES:
        _, page = quiz.page_for(source, qs, serve=True, bank_stem="sample",
                                mode="practice", home_href="/",
                                presentation_profile=profile)
        if 'data-presentation-profile="%s"' % profile not in page:
            fail("served quiz did not consume %s" % profile)
        for text in ("Purpose", "Practice", "Response format", "Disclosure",
                     "Feedback available now"):
            if text not in page:
                fail("served quiz lost activity hierarchy %r" % text)
        behavior[profile] = (page.count('action="/answer"'),
                             page.count('name="option"'),
                             page.count('id="offline"'))
    if behavior["field-guide"] != behavior["trajectory-deck"]:
        fail("profile changed served quiz form or runtime script behavior")
    with tempfile.TemporaryDirectory() as root:
        bank = os.path.join(root, "sample_bank.md")
        shutil.copyfile(source, bank)
        cfg = settings.load_settings(root)
        cfg["presentation_profile"] = "trajectory-deck"
        settings.write_settings(root, cfg)
        page = study.study_page(bank, load(bank))
        if 'data-presentation-profile="trajectory-deck"' not in page:
            fail("saved profile did not reach real Study output")
        for text in ("Application: itembank", "Study", "Purpose",
                     "Deliberate review", "Recall and reveal"):
            if text not in page:
                fail("Study lost shared hierarchy %r" % text)
        lesson_page = daemon.lesson.lesson_page(
            bank, load(bank), daemon.parse_lesson(bank))
        for text in ('data-presentation-profile="trajectory-deck"',
                     "Application: itembank", "Reading"):
            if text not in lesson_page:
                fail("lesson lost shared hierarchy %r" % text)
        class Handler:
            pass
        handler = Handler()
        handler.root = root
        state = {"course_name": "Synthetic Algebra", "course_id": "synthetic",
                 "area": "learn", "area_label": "Lesson", "notice": "No lesson yet.",
                 "nav": [{"href": "/course/synthetic", "current": False,
                          "label": "Overview"},
                         {"href": "/course/synthetic/learn", "current": True,
                          "label": "Learn"}]}
        course_page = daemon._course_frame(
            handler, state, {"href": "/course/synthetic", "label": "Back"})
        if 'data-presentation-profile="trajectory-deck"' not in course_page:
            fail("saved profile did not reach real course lesson frame")
    ok("saved profile reaches real course lesson, study, and served quiz output without behavior drift")


def main():
    check_profile_parity()
    check_activity_separation()
    check_response_type_presentation_matrix()
    check_migration_fallback_and_preview()
    check_state_labels()
    check_course_transition_and_degraded_state_contract()
    check_course_lesson_practice_context()
    check_live_surface_output()
    print("all presentation profile checks passed")


if __name__ == "__main__":
    main()
