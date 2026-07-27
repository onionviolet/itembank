#!/usr/bin/env python3
"""Assert that `itembank serve` actually writes answers to disk.

This is the regression test for the reason `serve` exists at all. The static
`build` page cannot persist anything, so a sitting used to vanish with the tab.
If this test ever fails, answers are being lost silently, which is the worst
possible failure mode here: the person believes their work was recorded.

Standard library only, no test framework, runnable as `python tests/serve_roundtrip.py`.
"""
import json, os, re, subprocess, sys, tempfile, threading, time, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BANK = os.path.join(ROOT, "fixtures", "sample_bank.md")


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def main():
    out = os.path.join(tempfile.mkdtemp(), "attempt.md")
    proc = subprocess.Popen(
        [sys.executable, "-u", os.path.join(ROOT, "itembank.py"), "serve", BANK,
         "--no-open", "--port", "0", "--out", out],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    lines = []
    threading.Thread(target=lambda: [lines.append(l) for l in proc.stdout],
                     daemon=True).start()

    url = None
    for _ in range(60):                       # up to ~6s for the bind and banner
        time.sleep(0.1)
        m = re.search(r"http://127\.0\.0\.1:\d+/", "".join(lines))
        if m:
            url = m.group(0)
            break
    if not url:
        fail("server never printed a URL. Output was:\n" + "".join(lines))

    try:
        page = urllib.request.urlopen(url, timeout=5).read().decode("utf-8")
        if "const RECORD = true" not in page:
            fail("served page is not in recording mode")
        if "function asShort" not in page:
            fail("served page has no short-answer renderer")

        answers = [
            {"n": 1, "type": "mc", "stem": "A selected-response item",
             "objective": "Ops", "answer": "B", "correct": True,
             "model": "", "rubric": []},
            {"n": 6, "type": "short", "stem": "A constructed-response item",
             "objective": "Regulatory framework",
             "answer": "The words the candidate actually typed.",
             "correct": None, "model": "The model answer.",
             "rubric": ["First checkable claim", "Second checkable claim"]},
        ]
        for k in (1, 2):                      # partial write, then the finish write
            req = urllib.request.Request(
                url + "save",
                data=json.dumps({"answers": answers[:k], "done": k == 2}).encode(),
                headers={"Content-Type": "application/json"})
            if urllib.request.urlopen(req, timeout=5).status != 204:
                fail("save POST %d was not accepted" % k)
            if not os.path.exists(out):
                fail("no attempt file after save POST %d" % k)
    finally:
        proc.terminate()

    text = open(out, encoding="utf-8").read()
    for needle in ("The words the candidate actually typed.",
                   "First checkable claim",
                   "MARK: (unmarked)",
                   "[auto: correct]",
                   "finished"):
        if needle not in text:
            fail("attempt file is missing %r" % needle)
    if "The model answer." not in text:
        fail("attempt file dropped the model answer the marker needs")
    if "- [ ]" in text:
        # Attempt files land in an Obsidian vault, where `- [ ]` is a task and
        # gets swept into unrelated Dataview queries.
        fail("attempt file uses task checkboxes; use (unmarked) instead")

    print("ok: serve wrote %d bytes to %s" % (len(text), out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
