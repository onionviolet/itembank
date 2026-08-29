#!/usr/bin/env python3
"""The bundled sample course, held as literal strings in this module.

Every objective, lesson, and item here is invented. It is generic study-skills
advice written for this fixture; no real course, exam, clinical, or learner
material appears in it and none of it is derived from any source.

The course is materialized at runtime into a gitignored directory and is never
committed as markdown, which is why `itembank guard` stays green with it on
disk. No model, agent, or network is involved in producing it: the bytes are
fixed and the write is a file copy. That is what makes first launch reachable
on an install with nothing configured and no connection.

Shipping the bytes in a `.py` module rather than a committed `.md` also keeps
guard's markdown walk untouched, and a module import resolves in a checkout and
inside a `.pyz` alike without needing `resources.py`'s bundled-asset path.
"""
import os

import graph

SAMPLE_COURSE_ID = "sample-study-skills"

# The literal `(Sample)` suffix lives inside the name string itself, not in a
# renderer, so no surface can drop it and no card can present this course as
# real material.
SAMPLE_COURSE_NAME = "Study Skills Basics (Sample)"

SAMPLE_COURSE_DIRNAME = "_sample_course"

# Exactly the keys `ia.course_shelf_state` reads, so the sample course renders
# through the same card path as any other course rather than a special case.
SAMPLE_COURSE_RECORD = {
    "course_id": SAMPLE_COURSE_ID,
    "name": SAMPLE_COURSE_NAME,
    "attention": "up_to_date",
    "due_count": 0,
    "pending_review_count": 0,
    "resume_cue": "Not started",
    "last_activity": None,
}

_SAMPLE_BANK = """# Study skills basics (sample)

Bundled sample material for exploring itembank. Every claim here is generic
study-skills advice written for this sample; it is not real course material and
it is not drawn from any source.

## LESSON

### Spacing Practice Over Time

Reading something once leaves a strong feeling of knowing and a weak ability to
recall. The feeling comes from how easily the words went in, which is not the
same thing as how easily they will come back out later.

Spacing means returning to the same material after a gap rather than in one
sitting. The gap is the part that does the work: recall that takes effort
strengthens the memory more than recall that is instant, and a gap is what
makes recall take effort.

A schedule that grows its gaps beats one that repeats at a fixed interval. Two
reviews a week apart teach more than four reviews in one evening, and the
evening version costs twice as much time.

> [!EXAMPLE]
> You read a chapter on Monday. Reviewing it Tuesday, then Friday, then the
> following Wednesday will hold better than three reviews on Monday night.

> [!KEY] The gap is the mechanism, not the delay
> Returning after a gap is what strengthens recall. Repeating without a gap
> mostly rehearses the feeling of knowing.

Q1. Which study pattern is most likely to improve recall a week later?   (difficulty: application)
[LESSON-REF: Spacing Practice Over Time]
[OBJECTIVE: study:spacing]

A) Reading the chapter four times in one evening
B) Reviewing the chapter on three days spread across a week
C) Highlighting every paragraph of the chapter once
D) Rereading only the paragraphs that felt difficult

CORRECT: B

WHY BEST: Reviews separated by gaps force effortful recall each time, and that
effort is what strengthens the memory a week later.

KEY DISCRIMINATOR: The pattern must place gaps between the reviews, not merely
repeat the material or vary how it is marked up.

SECOND-BEST: A. Four passes is genuine repetition, and this would be correct if
the question asked which pattern covers the most material tonight.

DISTRACTOR ANALYSIS:
- A) Four passes in one evening has no gap between them; this would be correct if the question asked about coverage in a single sitting.
- B) Correct: three reviews across a week put a gap before each recall.
- C) Highlighting marks the text without requiring recall; this would be correct if the question asked how to find material again later.
- D) Rereading difficult paragraphs is still rereading; this would be correct if the question asked how to spend a fixed hour most efficiently.

TRAP: Counting how many times the material was seen instead of how many times
it had to be recalled after a gap.

CONFIDENCE: high

Q2. A learner says a chapter feels easy after one reading. What does that feeling most reliably indicate?   (difficulty: comprehension)
[LESSON-REF: Spacing Practice Over Time]
[OBJECTIVE: study:spacing]

A) That the material will still be recallable next week
B) That the reading went smoothly just now
C) That the chapter was shorter than average
D) That no further review is needed

CORRECT: B

WHY BEST: Ease of reading reports how fluently the words were processed in the
moment, which is a fact about the reading and not about later recall.

KEY DISCRIMINATOR: The answer must describe the present reading experience
rather than any prediction about the future.

SECOND-BEST: A. Learners commonly draw this conclusion, and it would be correct
if fluency and durable recall moved together, which they do not.

DISTRACTOR ANALYSIS:
- A) Later recall is exactly what fluency fails to predict; this would be correct if the question asked what learners usually assume.
- B) Correct: the feeling reports how smoothly the reading itself went.
- C) Length is not what the feeling measures; this would be correct if the question asked what makes a chapter quick to finish.
- D) Stopping review is a decision, not something a feeling indicates; this would be correct if the question asked what learners often do next.

TRAP: Treating the smoothness of reading as evidence about memory a week from
now.

CONFIDENCE: high
"""

_SAMPLE_README = """# Sample course

This is a bundled sample course that ships with itembank so a fresh install has
something to open. It is not real course material and nothing in it is drawn
from any source. You can remove it from the course card menu at any time.
"""

SAMPLE_COURSE_FILES = {
    "study_skills_sample.md": _SAMPLE_BANK,
    "README.md": _SAMPLE_README,
}


def sidecar_text():
    """A valid course-graph sidecar naming this sample course.

    Built through `graph.new_course` and `graph.serialize_course`, the same
    two calls any real course sidecar is built from, so `course.read_course`
    reads it and the sample renders as a healthy card rather than a degraded
    one.
    """
    return graph.serialize_course(
        graph.new_course(SAMPLE_COURSE_NAME, SAMPLE_COURSE_ID))


def write_sample_course(dest_dir, course_module=None):
    """Materialize the sample course into `dest_dir`, byte for byte.

    Overwrites any existing file, so a re-materialization is idempotent and
    produces identical bytes. Returns the sorted absolute paths written.
    """
    if course_module is None:
        try:
            import course as course_module
        except ImportError:
            course_module = None

    if not os.path.isdir(dest_dir):
        os.makedirs(dest_dir)

    written = []
    for name, text in SAMPLE_COURSE_FILES.items():
        path = os.path.join(dest_dir, name)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        written.append(os.path.abspath(path))

    sidecar_name = getattr(course_module, "COURSE_SIDECAR_FILENAME",
                           "course-graph.md")
    path = os.path.join(dest_dir, sidecar_name)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(sidecar_text())
    written.append(os.path.abspath(path))

    return sorted(written)
