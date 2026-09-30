#!/usr/bin/env python3
"""Synthetic served entry keeps exact sitting identity and full collection tools."""
import html
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import course
import runtime
import sample_course
from surfaces import daemon, ia, session
from daemon_roundtrip import start_daemon, get


def snapshot(root):
    return {str(path.relative_to(root)): path.read_bytes()
            for path in root.rglob('*') if path.is_file()}


def check_served(browser=False):
    with tempfile.TemporaryDirectory(prefix='overhaul_navigation_') as temp:
        root = Path(temp)
        directory = root / 'synthetic'
        sample_course.write_sample_course(str(directory))
        record = course.read_course(str(directory))
        course_id = record['object_id']
        name = 'Synthetic logic: 多语言 ' + 'long-course-name-' * 12
        other = root / 'other'
        other.mkdir()
        course.create_course(str(other), name, 'agent', 'test')
        bank = directory / 'study_skills_sample.md'
        attempts = root / '_attempts'
        attempts.mkdir(exist_ok=True)
        saved_path = attempts / 'session_navigation.json'
        session.do_start(str(bank), {'objective': '', 'count': 3, 'seed': 0,
                                    'selection_mode': 'practice'}, 'practice',
                         str(saved_path), False, preset_session_id='navigation')
        exact = ia.course_shelf_state(temp)['cards']
        exact = next(card for card in exact if card['course_id'] == course_id)['cta_href']
        proc, url, _ = start_daemon(temp)
        try:
            before = snapshot(root)
            status, home = get(url)
            assert status == 200 and 'overhaul-course-choices' in home
            assert 'Resume practice</a>' in home and 'title="Drag to reorder"' not in home
            assert html.escape(exact, quote=True) in home
            status, courses = get(url + 'courses')
            assert status == 200 and 'data-drag-handle' in courses
            assert 'data-move="up"' in courses and 'Course options' in courses
            assert 'value="remove_sample_course"' in courses
            assert html.escape(name, quote=True) in courses
            status, overview = get(url + 'course/' + course_id)
            assert status == 200 and html.escape(exact, quote=True) in overview
            assert 'overhaul-saved-sittings' in overview
            assert snapshot(root) == before, 'entry GET changed learner files'
            status, page = get(url.rstrip('/') + exact)
            assert status == 200 and 'session=navigation' in page
            assert runtime.read_session(str(saved_path))['cursor'] == 0
            assert get(url.rstrip('/') + exact)[0] == 200
            if browser:
                from playwright.sync_api import sync_playwright
                with sync_playwright() as pw:
                    chrome = pw.chromium.launch(channel=os.environ.get('ITEMBANK_VISUAL_QA_CHANNEL', 'chrome'))
                    tab = chrome.new_page()
                    try:
                        for width in (1280, 390):
                            tab.set_viewport_size({'width': width, 'height': 900})
                            for route in ('', 'courses', 'course/' + course_id):
                                tab.goto(url + route)
                                assert tab.evaluate('document.documentElement.scrollWidth <= innerWidth'), (width, route)
                                for link in tab.locator('.overhaul-course-choice a').all():
                                    assert link.is_visible()
                                if os.environ.get('ITEMBANK_NAV_SHOTS'):
                                    shots = Path(os.environ['ITEMBANK_NAV_SHOTS'])
                                    shots.mkdir(parents=True, exist_ok=True)
                                    label = 'overview' if route.startswith('course/') else route or 'home'
                                    tab.screenshot(path=str(shots / ('%s-%d.png' % (label, width))), full_page=True)
                            tab.goto(url)
                            tab.locator('.desk-focus-actions a').click()
                            assert 'session=navigation' in tab.url
                            tab.reload()
                            assert 'session=navigation' in tab.url
                            tab.go_back()
                            assert tab.locator('.desk-focus-actions a').get_attribute('href') == exact
                        print('browser: served Home/Courses/overview, long multilingual names, 1280/390px, exact resume/reload/back ok')
                    finally:
                        chrome.close()
        finally:
            proc.terminate()
            proc.wait(timeout=5)


def check_labels():
    from desk_experience_roundtrip import card
    assert daemon._course_action_label(card('test', 'active', mode='exam')) == 'Resume test'
    assert daemon._course_action_label(card('many', 'ambiguous')) == 'Choose a saved sitting'
    assert daemon._course_action_label(card('new')) == 'Start'


if __name__ == '__main__':
    check_labels()
    check_served('--browser' in sys.argv)
    print('overhaul navigation: exact entry, read-only views, labels, collection controls ok')
