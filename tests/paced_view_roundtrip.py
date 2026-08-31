#!/usr/bin/env python3
"""Plan 16D-03: the served paced view, end to end.

One renderer, one scorer, one store: the paced view is `lesson_page`'s
third mode over the same rendered headings, its checkpoints are the shipped
6.2 gate bands scored through `runtime.score_response`, its attempts land
in the one evidence store with context "lesson_run" and mode "paced", and
its tier disclosure is `runtime.checkpoint_feedback`'s payload rendered
verbatim. The TOC is a jump, never a gate; the pager gates forward only on
an unattempted declared gate and shows a stated sentence, never a disabled
control.

Standard library only, runnable as `python tests/paced_view_roundtrip.py`.
Writes only under a temp dir.
"""
import json
import os
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

import evidence                                         # noqa: E402
import schema_validate                                  # noqa: E402
from surfaces import lesson as lesson_surface           # noqa: E402

FIXTURE = os.path.join(ROOT, "fixtures", "paced_lesson_bank.md")
STEM = "paced_lesson_bank"
CHECK_ID = "4b6fb5cba3ae425f"
RESPONSE_SCHEMA = json.load(open(
    os.path.join(ROOT, "schemas", "response.schema.json"), encoding="utf-8"))


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def ok(msg):
    print("ok: " + msg)


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


def main():
    work = tempfile.mkdtemp(prefix="paced_view_")
    proc = None
    try:
        shutil.copyfile(FIXTURE, os.path.join(work, STEM + ".md"))
        proc = subprocess.Popen(
            [sys.executable, "-u", os.path.join(ROOT, "itembank.py"),
             "daemon", work, "--no-open", "--port", "0"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        lines = []
        threading.Thread(target=lambda: [lines.append(l)
                                         for l in proc.stdout],
                         daemon=True).start()
        base = None
        for _ in range(80):
            time.sleep(0.1)
            m = re.search(r"http://127\.0\.0\.1:\d+/", "".join(lines))
            if m:
                base = m.group(0).rstrip("/")
                break
        if not base:
            fail("daemon never printed a URL:\n" + "".join(lines))
        route = base + "/lesson/" + STEM

        # 1. The plain lesson carries no paced chrome.
        _, plain = get(route)
        if "paced-" in plain:
            fail("the plain lesson route grew paced chrome")

        # 2. Paced entry: step 1 of 3, three TOC links, the silent-step
        #    Ledger line (the lesson has a checkpoint, step 1 does not).
        _, p1 = get(route + "?view=paced")
        if "Step 1 of 3" not in p1:
            fail("paced entry did not show step 1 of 3")
        if p1.count("?view=paced&amp;step=") < 3:
            fail("the Steps list must link every step")
        if lesson_surface.PACED_NO_EVIDENCE not in p1:
            fail("a checkpoint-free step must state that it records nothing")

        # 3. The TOC is a jump, never a gate: straight to the last step
        #    past the unattempted required gate.
        _, p3 = get(route + "?view=paced&step=application")
        if "Step 3 of 3" not in p3:
            fail("a forward TOC jump past an unattempted gate must work")

        # 4. The gate step: band present, pager gated with the exact
        #    sentence and no disabled control.
        _, p2 = get(route + "?view=paced&step=mechanism")
        if 'name="check"' not in p2:
            fail("the checkpoint band is missing from its step")
        if lesson_surface.PACED_GATED_CONTINUE not in p2:
            fail("an unattempted gate must show the stated sentence")
        if ">Continue</a>" in p2:
            fail("a gated step must not also offer Continue")
        if re.search(r"<[^>]+\sdisabled[\s>]", p2):
            fail("never a disabled control (UI-SPEC section 8 rule 9)")

        # 5. A wrong checkpoint: tier 1 marks the learner's own picks only,
        #    tier 2 carries touched rationale, and the reveal is offered
        #    but not shown.
        _, held = post_form(route + "/check",
                            {"check": CHECK_ID, "action": "check",
                             "view": "paced", "step": "mechanism",
                             "option": ["A", "C"]})
        if lesson_surface.PACED_TOUCHED_HEADING not in held:
            fail("tier 2 heading missing after a wrong checkpoint")
        marks = re.findall(r'<li>([A-E])\) <span class="paced-mark">'
                           r"(right|not right)</span></li>", held)
        if sorted(marks) != [("A", "right"), ("C", "not right")]:
            fail("tier 1 must mark exactly the touched options: %r" % marks)
        if "paced-reveal" in held:
            fail("tier 1 must not carry the full reveal")
        if lesson_surface.PACED_SHOW_ANSWER not in held:
            fail("the explicit-reveal control must be offered after a "
                 "wrong attempt")

        # 6. A second wrong attempt releases the full reveal.
        _, revealed = post_form(route + "/check",
                                {"check": CHECK_ID, "action": "check",
                                 "view": "paced", "step": "mechanism",
                                 "option": ["D", "E"]})
        if "paced-reveal" not in revealed or "Answer:" not in revealed:
            fail("a second wrong attempt must release the full reveal")

        # 7. The gate is attempted now, so Continue is an ordinary link.
        _, after = get(route + "?view=paced&step=mechanism")
        if ">Continue</a>" not in after:
            fail("an attempted gate must open the pager")

        # 8. Resume: a fresh paced GET lands on the recorded step.
        _, resumed = get(route + "?view=paced")
        if "Resuming at step 2." not in resumed:
            fail("a fresh paced GET must resume at the recorded step")

        # 9. An unknown step id falls back to step 1 with the stated line,
        #    never a guessed neighbour.
        _, gone = get(route + "?view=paced&step=never-was")
        if lesson_surface.PACED_UNKNOWN_STEP not in gone \
                or "Step 1 of 3" not in gone:
            fail("an unknown step must fall back to step 1 with the line")

        # 10. The evidence: lesson_run context, paced mode, schema-valid.
        log = os.path.join(work, "_evidence", "evidence.jsonl")
        responses = [json.loads(l) for l in open(log, encoding="utf-8")
                     if json.loads(l).get("event_type")
                     == evidence.RESPONSE_EVENT_TYPE]
        paced_events = [r for r in responses
                        if r.get("context") == "lesson_run"]
        if len(paced_events) != 2:
            fail("expected 2 lesson_run response events, got %d"
                 % len(paced_events))
        for r in paced_events:
            if r.get("mode") != "paced":
                fail("a paced checkpoint event must carry mode paced")
            errors = schema_validate.validate(r, RESPONSE_SCHEMA)
            if errors:
                fail("a paced response event does not validate: %r" % errors)

        # 11. The static build carries no paced chrome and no step state.
        out = os.path.join(work, "out.html")
        r = subprocess.run(
            [sys.executable, os.path.join(ROOT, "itembank.py"), "build",
             os.path.join(work, STEM + ".md"), out, "--force"],
            capture_output=True, text=True, encoding="utf-8")
        if r.returncode != 0:
            fail("static build failed: %s" % (r.stderr or r.stdout)[-400:])
        built = open(out, encoding="utf-8").read()
        if "paced-steps" in built or "paced-pager" in built:
            fail("the static build must carry no paced chrome")

        ok("paced view: projection, jump-only TOC, stated gate, tier "
           "ladder over HTTP, resume, fallback, labelled evidence, and a "
           "chrome-free static build")
        print("PASS paced_view_roundtrip.py")
        return 0
    finally:
        if proc is not None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
