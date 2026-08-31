#!/usr/bin/env python3
"""Phase 16D (16D-04) paced-lesson freeze-gate tracer.

One scripted end-to-end run over fixtures/paced_lesson_bank.md, composing
the three finer-grained roundtrips this plan names
(tests/paced_steps_roundtrip.py, tests/lesson_run_roundtrip.py,
tests/paced_view_roundtrip.py) into a single scenario table in the
16C cross-subject tracer's house style, rather than re-asserting their
fine-grained checks here.

This file measures. Every number it prints came from the run that printed
it, on the machine and Python version it names.

Standard library only, runnable as `python3 tests/paced_lesson_tracer.py`.
Writes only under tempfile.mkdtemp() directories.
"""
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import blueprint                                        # noqa: E402
import model                                             # noqa: E402
import runtime                                           # noqa: E402
from surfaces import lesson as lesson_surface            # noqa: E402

FIXTURE = os.path.join(ROOT, "fixtures", "paced_lesson_bank.md")
PLAIN = os.path.join(ROOT, "fixtures", "lesson_bank.md")
STEM = "paced_lesson_bank"
CHECK_ID = "4b6fb5cba3ae425f"
MC_ID = "d6ac6b415a7d49a5"

FAILURES = []
MEASURED = {}


def fail(msg):
    print("FAIL: %s" % msg)
    FAILURES.append(msg)


def ok(msg):
    print("  ok: %s" % msg)


def report(msg):
    print("  report: %s" % msg)


def maybe_ok(before, msg):
    """Print the scenario's summary line only when nothing failed since
    `before`, so a scenario's own text never claims success it did not
    have (the table's passed/FAILED verdict in main() is unaffected)."""
    if len(FAILURES) == before:
        ok(msg)


def get(url):
    with urllib.request.urlopen(url, timeout=5) as res:
        return res.status, res.read().decode("utf-8")


def post_form(url, fields):
    body = urllib.parse.urlencode(fields, doseq=True).encode("utf-8")
    req = urllib.request.Request(
        url, data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=5) as res:
        return res.status, res.read().decode("utf-8")


def _start_daemon(work):
    """Start `itembank daemon` over `work` and return (proc, base). Mirrors
    the harness shape tests/paced_view_roundtrip.py's main() uses."""
    proc = subprocess.Popen(
        [sys.executable, "-u", os.path.join(ROOT, "itembank.py"),
         "daemon", work, "--no-open", "--port", "0"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    lines = []
    threading.Thread(target=lambda: [lines.append(l) for l in proc.stdout],
                     daemon=True).start()
    base = None
    for _ in range(80):
        time.sleep(0.1)
        m = re.search(r"http://127\.0\.0\.1:\d+/", "".join(lines))
        if m:
            base = m.group(0).rstrip("/")
            break
    if not base:
        proc.terminate()
        raise RuntimeError("daemon never printed a URL:\n" + "".join(lines))
    return proc, base


# ---- 1. the pacing ladder at all three rungs --------------------------


def scenario_ladder(ctx, tmp):
    """D-16D-1/D-16D-2: an explicit marker wins, else the configured
    heading level, else the whole document, unsliced. Composes
    paced_steps_roundtrip's rungs into one pass rather than repeating its
    fine-grained assertions."""
    before = len(FAILURES)
    # Rung 1: the shipped fixture, four durable steps in document order.
    lesson1 = model.parse_lesson(FIXTURE)
    steps1 = model.lesson_steps(lesson1)
    ids1 = [s["id"] for s in steps1]
    if ids1 != ["intro", "orientation", "mechanism", "application"]:
        fail("rung 1 ids are %r" % ids1)
    if any(s["rung"] != 1 for s in steps1):
        fail("rung 1 steps must all carry rung 1")

    # Rung 2: strip the markers from an in-memory copy; [LESSON-PACE: h3]
    # takes over and ids become the heading slugs.
    text = open(FIXTURE, encoding="utf-8").read()
    stripped = re.sub(r"(?m)^\[STEP:.*\n?", "", text)
    path2 = os.path.join(tmp, "rung2.md")
    open(path2, "w", encoding="utf-8").write(stripped)
    lesson2 = model.parse_lesson(path2)
    steps2 = model.lesson_steps(lesson2)
    slugs = [h["slug"] for h in lesson2["headings"]]
    got2 = [s["id"] for s in steps2 if s["id"] != "intro"]
    if got2 != slugs:
        fail("rung 2 ids %r are not the heading slugs %r" % (got2, slugs))
    if any(s["rung"] != 2 for s in steps2):
        fail("rung 2 steps must all carry rung 2")

    # Rung 3: the plain, markerless, pace-less fixture is one whole-document
    # step, byte-identical to pre-16D behaviour.
    lesson3 = model.parse_lesson(PLAIN)
    steps3 = model.lesson_steps(lesson3)
    if len(steps3) != 1 or steps3[0]["id"] != "document" \
            or steps3[0]["rung"] != 3:
        fail("rung 3 must be one whole-document step: %r" % steps3)
    if steps3[0]["content"] != lesson3["body"]:
        fail("rung 3 content must be the effective lesson text, unsliced")

    maybe_ok(before, "ladder: rung 1 markers (4 steps), rung 2 heading "
             "slugs, rung 3 whole document")


# ---- 2. a full paced sitting over HTTP ---------------------------------


def scenario_full_sitting(ctx, tmp):
    """Read, wrong checkpoint (tier 1/2), second wrong (tier 3 reveal),
    resume, jump past the gate."""
    before = len(FAILURES)
    work = os.path.join(tmp, "http")
    os.makedirs(work, exist_ok=True)
    bank_path = os.path.join(work, STEM + ".md")
    shutil.copyfile(FIXTURE, bank_path)
    proc, base = _start_daemon(work)
    ctx["work"] = work
    ctx["proc"] = proc
    ctx["base"] = base
    ctx["bank_path"] = bank_path
    route = base + "/lesson/" + STEM
    ctx["route"] = route

    _, p1 = get(route + "?view=paced")
    if "Step 1 of 3" not in p1:
        fail("paced entry did not show step 1 of 3")

    _, jump = get(route + "?view=paced&step=mechanism")
    if 'name="check"' not in jump:
        fail("jumping to the gated step lost the checkpoint band")

    _, held = post_form(route + "/check",
                        {"check": CHECK_ID, "action": "check",
                         "view": "paced", "step": "mechanism",
                         "option": ["A", "C"]})
    if lesson_surface.PACED_TOUCHED_HEADING not in held:
        fail("tier 2 heading missing after a wrong checkpoint")
    if "paced-reveal" in held:
        fail("the first wrong attempt must not carry the full reveal")

    _, revealed = post_form(route + "/check",
                            {"check": CHECK_ID, "action": "check",
                             "view": "paced", "step": "mechanism",
                             "option": ["D", "E"]})
    if "paced-reveal" not in revealed or "Answer:" not in revealed:
        fail("a second wrong attempt must release the full reveal")

    _, resumed = get(route + "?view=paced")
    if "Resuming at step 2." not in resumed:
        fail("a fresh paced GET must resume at the recorded step")

    _, last = get(route + "?view=paced&step=application")
    if "Step 3 of 3" not in last:
        fail("a forward TOC jump must reach the last step")

    maybe_ok(before, "full sitting: step 1 of 3, tier 1/2 on the first "
             "wrong attempt, tier 3 reveal on the second, resume at "
             "step 2, TOC jump to step 3")


# ---- 3. resume stability across a lesson edit --------------------------


def scenario_resume_across_edit(ctx, tmp):
    """Continues scenario_full_sitting's daemon and recorded resume
    position deliberately: the recorded step id must survive an edit that
    inserts an earlier step, and the fallback line must fire only once the
    recorded id is truly gone."""
    before = len(FAILURES)
    route = ctx["route"]
    bank_path = ctx["bank_path"]
    text = open(bank_path, encoding="utf-8").read()

    # scenario_full_sitting's own last GET jumped to "application", which
    # became the new recorded resume position; re-visit "mechanism" so this
    # scenario is testing what it says it is testing (deliberate reuse of
    # the shared daemon, not a coincidence of leftover state).
    _, _ = get(route + "?view=paced&step=mechanism")

    insert = ("[STEP: preface]\n\n"
              "A preface makes the frame explicit before any signal work "
              "begins.\n\n"
              "### Preface Heading\n\n")
    edited = text.replace("## LESSON\n\n", "## LESSON\n\n" + insert, 1)
    if edited == text:
        fail("the insertion anchor '## LESSON' was not found in the bank")
    open(bank_path, "w", encoding="utf-8").write(edited)

    _, after_insert = get(route + "?view=paced")
    if "Why Dimming Happens" not in after_insert:
        fail("the recorded step id 'mechanism' did not survive an edit "
             "that inserted an earlier step")

    # Now remove the [STEP: mechanism] marker line only; its heading stays,
    # so the heading folds into the previous step and the id is truly gone.
    edited2 = edited.replace("[STEP: mechanism]\n\n", "", 1)
    if edited2 == edited:
        fail("the '[STEP: mechanism]' marker line was not found to remove")
    open(bank_path, "w", encoding="utf-8").write(edited2)

    _, gone = get(route + "?view=paced")
    if lesson_surface.PACED_UNKNOWN_STEP not in gone:
        fail("a truly gone recorded step must show the fallback line")
    if "Step 1 of" not in gone:
        fail("the fallback must land on step 1, got: %r" % gone[:200])

    maybe_ok(before, "resume: an inserted earlier step leaves 'mechanism' "
             "resolvable; removing its marker fires the fallback line at "
             "step 1")


# ---- 4. the denominator exclusion, blueprint's AGENT-03 path -----------


def scenario_denominator(ctx, tmp):
    before = len(FAILURES)
    rows = []
    for n, context in enumerate(("quiz", "quiz", "lesson_gate",
                                 "lesson_run", "lesson_run")):
        rows.append({"ts": "2026-06-01T00:00:0%dZ" % n,
                     "objective": "glimmer:mechanism", "score": True,
                     "context": context})
    window = {"start": "2026-01-01T00:00:00Z", "end": "2027-01-01T00:00:00Z",
              "boundary": "half-open"}
    proposal = blueprint.evidence_proposal(
        "glimmer:mechanism", rows, window, ["response"], [],
        ["a small sample can look like a trend"])
    if proposal["denominator"] != 3:
        fail("5 rows, 2 lesson_run, expected denominator 3, got %d"
             % proposal["denominator"])
    maybe_ok(before, "denominator: 5 rows, 2 lesson_run rows excluded, "
             "denominator 3")


# ---- 5. exam contrast: never disclosed, never paced chrome -------------


def scenario_exam_contrast(ctx, tmp):
    before = len(FAILURES)
    qs = model.load(FIXTURE)
    q1 = qs[0]
    for mode in ("exam", "diagnostic"):
        refused = runtime.checkpoint_feedback(q1, "A", 1, False,
                                              session_mode=mode)
        if refused.get("error") != "checkpoint.assessment_mode":
            fail("%s must be refused by name, got %r" % (mode, refused))

    route = ctx["route"]
    _, plain = get(route)
    if "paced-" in plain:
        fail("the plain lesson route grew paced chrome")

    maybe_ok(before, "exam contrast: exam and diagnostic checkpoints "
             "refused by name; the plain lesson route carries no paced "
             "chrome")


# ---- 6. rung-3 byte-identity for a markerless lesson --------------------


def scenario_rung3_byte_identity(ctx, tmp):
    before = len(FAILURES)
    lesson = model.parse_lesson(PLAIN)
    if lesson["pace"] != "none":
        fail("a markerless, pace-less lesson must read pace none")
    steps = model.lesson_steps(lesson)
    if len(steps) != 1:
        fail("a markerless lesson must resolve to exactly one step, got %d"
             % len(steps))

    route = ctx["route"]
    _, first = get(route)
    _, second = get(route)
    if first != second:
        fail("the served plain lesson page was not byte-identical across "
             "two GETs")

    maybe_ok(before, "rung 3: pace none, one step, the served plain page "
             "is byte-identical across two GETs")


# ---- 7. the reconsideration probes -------------------------------------


def scenario_reconsideration_probes(ctx, tmp):
    before = len(FAILURES)
    # (a) informational: does the shipped fixture use authored markers, the
    # authors-take-rung-2 probe. Not a failure either way; it is reported.
    lesson = model.parse_lesson(FIXTURE)
    uses_markers = "[STEP:" in (lesson.get("body") or "")
    report("the fixture uses authored [STEP:] markers: %s" % uses_markers)

    # (b) tier 1 non-triviality: one wrong single pick on a four-option mc
    # must not resolve the item by elimination. At least two options must
    # remain unresolved (unmarked and not revealed).
    qs = model.load(FIXTURE)
    q1 = qs[0]
    all_options = set(q1["opts"].keys())
    t1 = runtime.checkpoint_feedback(q1, "A", 1, False)
    marked = set(m["option"] for m in t1["selection_marks"])
    revealed_correct = set()
    if t1.get("reveal") is not None:
        revealed_correct = set(q1.get("correct") or ())
    unresolved = all_options - marked - revealed_correct
    if len(unresolved) < 2:
        fail("tier 1 left only %d option(s) unresolved: %r"
             % (len(unresolved), unresolved))
    else:
        ok("tier 1 non-triviality: %d of %d options remain unresolved "
           "after one wrong single pick" % (len(unresolved),
                                            len(all_options)))

    # (c) no lesson_run row reaches a denominator without policy: a rows
    # list of ONLY lesson_run rows must read denominator 0, no-evidence.
    window = {"start": "2026-01-01T00:00:00Z", "end": "2027-01-01T00:00:00Z",
              "boundary": "half-open"}
    only_lesson_run = [
        {"ts": "2026-06-01T00:00:00Z", "objective": "glimmer:mechanism",
         "score": True, "context": "lesson_run"},
        {"ts": "2026-06-01T00:00:01Z", "objective": "glimmer:mechanism",
         "score": True, "context": "lesson_run"},
    ]
    proposal = blueprint.evidence_proposal(
        "glimmer:mechanism", only_lesson_run, window, ["response"], [], [])
    if proposal["denominator"] != 0:
        fail("a rows list of only lesson_run rows must read denominator 0, "
             "got %d" % proposal["denominator"])
    if proposal["uncertainty"] != "no-evidence":
        fail("a denominator of 0 must read uncertainty no-evidence, got %r"
             % proposal["uncertainty"])

    maybe_ok(before, "reconsideration: marker-usage reported, tier 1 is "
             "not trivially solvable, no lesson_run row reaches a "
             "denominator unpoliced")


# ---- 8. the layout leg, when the pinned Playwright harness is present --


def scenario_layout_leg(ctx, tmp):
    try:
        import playwright  # noqa: F401
    except ImportError:
        ok("layout leg SKIPPED: Playwright is not installed; falls back "
           "to the scripted human QA pass")
        return
    r = subprocess.run(
        [sys.executable, os.path.join(ROOT, "tools", "visual_qa.py"),
         "--json", "-"],
        capture_output=True, text=True, encoding="utf-8", timeout=600)
    if r.returncode != 0:
        fail("tools/visual_qa.py did not report a clean matrix: %s"
             % (r.stdout + r.stderr)[-2000:])
    else:
        ok("layout leg: tools/visual_qa.py reported a clean matrix")


SCENARIOS = (
    ("scenario_ladder", scenario_ladder),
    ("scenario_full_sitting", scenario_full_sitting),
    ("scenario_resume_across_edit", scenario_resume_across_edit),
    ("scenario_denominator", scenario_denominator),
    ("scenario_exam_contrast", scenario_exam_contrast),
    ("scenario_rung3_byte_identity", scenario_rung3_byte_identity),
    ("scenario_reconsideration_probes", scenario_reconsideration_probes),
    ("scenario_layout_leg", scenario_layout_leg),
)


def main():
    tmp = tempfile.mkdtemp(prefix="itembank-16D-tracer-")
    ctx = {}
    started = time.monotonic()
    try:
        for name, scenario in SCENARIOS:
            before = len(FAILURES)
            scenario_started = time.monotonic()
            try:
                scenario(ctx, tmp)
            except Exception as exc:  # a scenario must never abort the run
                fail("%s raised %r" % (name, exc))
            elapsed = time.monotonic() - scenario_started
            state = "passed" if len(FAILURES) == before else "FAILED"
            MEASURED.setdefault("scenarios", {})[name] = round(elapsed, 3)
            print("  %-32s %s  %.3fs" % (name, state, elapsed))
    finally:
        proc = ctx.get("proc")
        if proc is not None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
        shutil.rmtree(tmp, ignore_errors=True)

    total = time.monotonic() - started
    MEASURED["elapsed"] = round(total, 3)
    MEASURED["platform"] = "%s %s" % (platform.system(), platform.release())
    MEASURED["python"] = platform.python_version()
    failed = len(FAILURES)
    print("TRACER: %d passed, %d failed" % (len(SCENARIOS) - failed, failed))
    print("elapsed: %.3fs" % total)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
