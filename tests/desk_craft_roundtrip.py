#!/usr/bin/env python3
"""Desk projection keeps real course state and actions visible."""
import html
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from surfaces import daemon


def check_ordered_shelf():
    first = {
        "course_id": 'a"<id>', "name": 'Logic <& "proofs"',
        "attention": "needs_input", "token": 'cue"<red>',
        "chip": "Needs input", "resume_cue": "Session status unavailable",
        "cta_href": '/course/a?view=1&x="',
        "cta_label": 'Open Logic <& "proofs"',
        "actions": ({"href": "/course/a/sources?x=1&y=2",
                     "label": "View source <files>"},),
        "degraded": False,
    }
    second = {
        "course_id": "sample", "name": "Sample course",
        "attention": "ready", "token": "ready", "chip": "Ready",
        "resume_cue": "No sessions yet", "cta_href": "/course/sample",
        "cta_label": "Start Sample course", "actions": (), "degraded": False,
    }
    shelf = {"cards": [first, second], "reorderable": True,
             "workspace_fingerprint": 'sha256:abc"<x>',
             "empty_heading": "No courses yet", "empty_body": "Add a course"}
    sample = {"course_id": "sample", "note": "Sample only",
              "confirm_copy": "Remove this sample?",
              "remove_label": "Remove sample"}
    walkthrough = {"status": "unseen", "offer_copy": "Take the tour",
                   "start_copy": "Start walkthrough",
                   "skip_copy": "Skip for now",
                   "replay_copy": "Replay walkthrough"}
    page = daemon._course_shelf_body(shelf, walkthrough=walkthrough,
                                     sample=sample)
    plain = html.unescape(page)
    assert '<section class="desk-focus"' in page
    assert 'First in your course order' in page
    assert '<h2 id="desk-focus-title">Logic &lt;&amp; &quot;proofs&quot;</h2>' in page
    assert 'href="/course/a?view=1&amp;x=&quot;"' in page
    assert 'Open Logic &lt;&amp; &quot;proofs&quot;' in page
    assert 'aria-label="Open Logic &lt;&amp; &quot;proofs&quot;">Open</a>' in page
    assert 'data-course-id="a&quot;&lt;id&gt;"' in page
    assert 'data-ia-token="cue&quot;&lt;red&gt;"' in page
    assert 'data-workspace-fingerprint="sha256:abc&quot;&lt;x&gt;"' in page
    assert '<div class="course-shelf" role="list"' in page
    assert page.count('class="course-card"') == 2
    assert '<span class="course-mark" aria-hidden="true">01</span>' in page
    assert '<span class="course-mark" aria-hidden="true">02</span>' in page
    assert '<summary>Course options</summary>' in page
    assert 'View source &lt;files&gt;' in page
    assert 'data-drag-handle' in page
    assert page.index('data-drag-handle') < page.index('<details class="course-details">')
    assert 'data-move="up"' in page and 'data-move="down"' in page
    assert 'value="remove_sample_course"' in page
    assert 'value="advance_walkthrough"' in page
    assert 'value="skip_walkthrough"' in page
    assert 'value="replay_walkthrough"' in page
    assert 'value="add_sample_course"' not in page
    assert 'Your place is saved' not in plain
    assert 'latest' not in plain.lower()
    assert 'desk-plant' not in page
    assert '<p class="actions"><form' not in page


def check_empty_shelf():
    page = daemon._course_shelf_body({
        "cards": [], "reorderable": False,
        "empty_heading": "No courses yet", "empty_body": "Try a sample"})
    assert '<h2>Your desk</h2>' in page
    assert '0 courses' in page
    assert 'value="add_sample_course"' in page
    assert 'class="desk-focus"' not in page
    assert 'No course is ready yet' not in page
    assert 'Your place is saved' not in page
    assert 'data-shelf-status' in page


def check_recovery_action_labels():
    for label in ("Open last valid overview", "Open last known Sample course"):
        assert daemon._course_action_label({"name": "Sample course",
                                            "cta_label": label}) == label


def main():
    check_ordered_shelf()
    check_empty_shelf()
    check_recovery_action_labels()
    print("desk craft: canonical focus, shelf controls, escaping, and empty state ok")


if __name__ == "__main__":
    main()
