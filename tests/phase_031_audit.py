#!/usr/bin/env python3
"""Phase 03.1 requirement-coverage audit (plan 03.1-07 Task 2).

Reads only the .planning files for phase 03.1 (safe to run while another
agent writes font files under fonts/):

  (a) parse each 03.1-0N-PLAN.md frontmatter `requirements:` list and
      confirm every one of LESSON-07..LESSON-17 appears in at least one
      plan;
  (b) for each of the eleven IDs, confirm the plan(s) that own it name a
      verification -- a tests/*.py fixture file or an executable command in
      the plan's <verify> block / acceptance criteria;
  (c) grep every PLAN.md for the deterministic-edge-probe skip sentence
      (visible-skip rule). The sentence is present in 03.1-07-PLAN.md; if
      no plan in the phase records it, the audit fails. Per-plan absence is
      printed as a visible gap line so nothing is laundered.

Standard library only. Runnable as `python tests/phase_031_audit.py`.
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PHASE = os.path.join(
    ROOT, ".planning", "phases", "03.1-lesson-rich-blocks-glossary-style")

LESSON_IDS = ["LESSON-%02d" % n for n in range(7, 18)]  # LESSON-07..17
SKIP_SENTENCE = "deterministic edge probe skipped"


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def plan_paths():
    return sorted(glob.glob(os.path.join(PHASE, "03.1-0?-PLAN.md")))


def frontmatter(text):
    m = re.search(r"^---\n(.*?)\n---", text, re.S)
    return m.group(1) if m else ""


def plan_requirements(text):
    """The `requirements:` frontmatter list, as LESSON-IDs (regex-pragmatic)."""
    fm = frontmatter(text)
    return re.findall(r"^\s*-\s*(LESSON-\d{2})\s*$", fm, re.M)


def named_verifications(text):
    """A verification is named when the plan's <verify> block or acceptance
    criteria mention a tests/*.py fixture file or an executable command."""
    blocks = []
    m = re.search(r"<verify>.*?</verify>", text, re.S)
    if m:
        blocks.append(m.group(0))
    m = re.search(r"<acceptance_criteria>.*?</acceptance_criteria>", text, re.S)
    if m:
        blocks.append(m.group(0))
    blob = "\n".join(blocks)
    if re.search(r"tests/[a-zA-Z0-9_]+\.py", blob):
        return True
    if re.search(r"\b(python|schema_validate|build\.py|grep|itembank)\b", blob):
        return True
    return False


def main():
    files = plan_paths()
    if not files:
        fail("no 03.1-0N-PLAN.md files found under %s" % PHASE)
    if len(files) < 7:
        fail("expected 7 phase plan files, found %d" % len(files))

    plans = []
    for path in files:
        text = open(path, encoding="utf-8").read()
        plans.append({
            "name": os.path.basename(path),
            "text": text,
            "requirements": set(plan_requirements(text)),
            "verified": named_verifications(text),
        })

    # (a) every ID must appear in at least one plan's requirements.
    covered = set()
    for p in plans:
        covered |= p["requirements"]
    missing = [lid for lid in LESSON_IDS if lid not in covered]
    if missing:
        fail("requirement IDs with no plan: %s" % ", ".join(missing))

    # (b) each ID's owning plan(s) must name a verification.
    for lid in LESSON_IDS:
        owners = [p for p in plans if lid in p["requirements"]]
        if not owners:
            fail("%s has no owning plan" % lid)
        if not any(o["verified"] for o in owners):
            fail("%s appears in %s but none of those plans names a "
                 "verification (no tests/*.py fixture and no command in its "
                 "<verify>/acceptance criteria)"
                 % (lid, ", ".join(o["name"] for o in owners)))

    # (c) visible-skip rule: grep every PLAN.md for the skip sentence.
    missing_skip = [p["name"] for p in plans
                    if SKIP_SENTENCE not in p["text"].lower()]
    if len(missing_skip) == len(plans):
        fail("no PLAN.md records the deterministic edge probe skip "
             "(visible-skip rule)")
    if missing_skip:
        print("gap: visible-skip sentence absent from %s (present only in "
              "03.1-07-PLAN.md)"
              % ", ".join(missing_skip))

    # (d) all eleven IDs covered, every owner verified.
    print("phase 03.1 requirement audit: 11/11 covered, ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
