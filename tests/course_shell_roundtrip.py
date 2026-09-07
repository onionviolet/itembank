#!/usr/bin/env python3
"""R5: one visible shelf-to-course-to-home application journey."""
import html
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import sample_course
from surfaces import daemon, ia


def fail(message):
    raise AssertionError(message)


def check_read_models_and_markup():
    root = tempfile.mkdtemp(prefix="course_shell_")
    try:
        ia.write_ia_state(root, "sample_course", {"removed": True})
        shelf = ia.course_shelf_state(root)
        body = daemon._course_shelf_body(shelf)
        for needle in ('aria-label="Application"', 'aria-current="page"',
                       'value="add_sample_course"', "No courses yet",
                       "data-shelf-status"):
            if needle not in body:
                fail("empty shelf omitted %r" % needle)
        result = ia.apply_shelf_action(root, "add_sample_course")
        if not result["ok"] or not result["written"]:
            fail("sample-course action did not create the course")
        state = ia.course_area_state(root, sample_course.SAMPLE_COURSE_ID,
                                     "learn")
        page = daemon._course_frame(
            type("Handler", (), {"root": root, "banks": {}})(), state,
            {"href": "/", "label": "Back to courses"},
            ia.course_dir_for(root, sample_course.SAMPLE_COURSE_ID))
        plain = html.unescape(page)
        for needle in ("Current area: Learn", "Course area: Learn",
                       'href="/"', "Back to courses"):
            if needle not in plain:
                fail("course frame omitted %r" % needle)
        if page.count('aria-current="page"') != 2:
            fail("desktop and mobile course navigation lost current state")
        for needle in (".course-nav-mobile{display:none}",
                       ".course-nav-desktop{display:none}",
                       ".course-nav-mobile{display:block"):
            if needle not in page:
                fail("responsive disclosure CSS omitted %r" % needle)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def main():
    check_read_models_and_markup()
    print("course shell: shelf, current area, mobile disclosure, empty action ok")


if __name__ == "__main__":
    main()
