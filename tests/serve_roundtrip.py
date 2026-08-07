#!/usr/bin/env python3
"""Assert that `itembank serve` scores in the process and writes answers to disk.

Two regressions guarded here, both of which fail silently in the worst way.

First, persistence: the static `build` page cannot save anything, so a sitting
used to vanish with the tab. If the write half breaks, the person believes their
work was recorded when it was not.

Second, answer leakage: the served page must never carry the key. If that breaks
nothing looks wrong, because the quiz still works. It just becomes a page that
hands over the answers to anyone who opens the source, which disqualifies every
surface an agent or a second person touches.

Since plan 01-10, the attempt file itself is `evidence.render_attempt_md()`'s
output, a view over `_evidence/evidence.jsonl` rather than a second store, and
its "MARK:" / "[auto: ...]" text reflects that render's own vocabulary.

Standard library only, no test framework, runnable as `python tests/serve_roundtrip.py`.
"""
import json, os, re, subprocess, sys, tempfile, threading, time
import urllib.error, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import itembank                                            # noqa: E402

BANK = os.path.join(ROOT, "fixtures", "sample_bank.md")


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def correct_answer(q):
    """The response `score_response` should mark true, in the shape the page posts."""
    if q["type"] == "mc":
        return q["correct"][0]
    if q["type"] == "multi":
        return list(q["correct"])
    if q["type"] in ("table", "dnd"):
        return dict((str(i), r["cat"]) for i, r in enumerate(q["rows"]))
    if q["type"] == "build":
        return list(q["steps"])
    return "A constructed response, written out in full sentences."


def wrong_answer(q):
    """A response that must not be marked true."""
    if q["type"] == "mc":
        return next(k for k in sorted(q["opts"]) if k != q["correct"][0])
    if q["type"] == "multi":
        others = [k for k in sorted(q["opts"]) if k not in q["correct"]]
        return others[:len(q["correct"])] or [q["correct"][0]]
    if q["type"] in ("table", "dnd"):
        return dict((str(i), next(c for c in q["cats"] if c != r["cat"]))
                    for i, r in enumerate(q["rows"]))
    if q["type"] == "build":
        return list(reversed(q["steps"]))
    return None


def post(answer_url, payload):
    req = urllib.request.Request(answer_url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=5) as res:
        return json.loads(res.read().decode("utf-8"))


def served_post_path(quiz_url, page):
    """The answer-POST target the served page's own script carries, resolved
    against the page's URL. `itembank serve` is a daemon launch scoped to
    one bank (plan 02-02) -- its answer path is bank-scoped
    (`/quiz/<stem>/answer`), not the bare `/answer` a single-bank process
    used to hardcode, so this reads it off the page rather than assuming
    the convention.
    """
    m = re.search(r'fetch\("([^"]+)"', page)
    if not m:
        fail("could not find the answer-POST target in the served page")
    return urllib.parse.urljoin(quiz_url, m.group(1))


def served_items(page):
    """The item payload the page was actually given."""
    m = re.search(r"(?m)^const Q = (\[.*\]);$", page)
    if not m:
        fail("could not find the item payload in the served page")
    return json.loads(m.group(1))


def check_no_key(page, qs):
    items = served_items(page)
    if len(items) != len(qs):
        fail("served %d items, bank has %d" % (len(items), len(qs)))
    for item in items:
        for leak in ("key", "explain", "correct", "opts", "cats", "da", "why",
                     "model", "rubric", "steps_correct"):
            if leak in item:
                fail("served item %s carries %r, which is answer-key data"
                     % (item.get("id"), leak))
    # The page carries the offline branch's *code* in both modes, which is fine:
    # it reads `key` off an item, and under `serve` no item has one. What must
    # not exist is a second set of scoring rules that could disagree with the
    # process.
    for banned in ("function grade(", "q.correct.includes", "same(picked"):
        if banned in page:
            fail("served page references %r; the process is the only scorer" % banned)
    # Nothing from the answer half of the bank may appear anywhere in the source,
    # not only inside the payload.
    for q in qs:
        if q["type"] == "short" and q.get("model") and q["model"] in page:
            fail("served page contains the model answer for %s" % q["id"])
        if q.get("why") and q["why"] in page:
            fail("served page contains the WHY BEST text for %s" % q["id"])


def main():
    qs = itembank.parse_bank(open(BANK, encoding="utf-8").read())
    stem = os.path.splitext(os.path.basename(BANK))[0]
    out = os.path.join(tempfile.mkdtemp(), "attempt.md")
    proc = subprocess.Popen(
        [sys.executable, "-u", os.path.join(ROOT, "itembank.py"), "serve", BANK,
         "--no-open", "--port", "0", "--out", out],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    lines = []
    threading.Thread(target=lambda: [lines.append(l) for l in proc.stdout],
                     daemon=True).start()

    # `itembank serve` is now a daemon launch scoped to one bank (plan
    # 02-02): the printed URL already names `/quiz/<stem>`, but this regex
    # only needs the base -- the quiz page itself lives at `/quiz/<stem>`,
    # scraped explicitly below rather than assumed to be the server root.
    base = None
    for _ in range(60):                       # up to ~6s for the bind and banner
        time.sleep(0.1)
        m = re.search(r"http://127\.0\.0\.1:\d+/", "".join(lines))
        if m:
            base = m.group(0)
            break
    if not base:
        fail("server never printed a URL. Output was:\n" + "".join(lines))
    quiz_url = base + "quiz/%s" % stem

    try:
        page = urllib.request.urlopen(quiz_url, timeout=5).read().decode("utf-8")
        if "const SERVE = true" not in page:
            fail("served page is not in recording mode")
        if "function asShort" not in page:
            fail("served page has no short-answer renderer")
        check_no_key(page, qs)

        answer_url = served_post_path(quiz_url, page)

        # A wrong answer must come back wrong. Re-answering the same item is a
        # new attempt, not an overwrite: the evidence log is append-only, so
        # both this wrong first attempt and the correct one it is followed
        # with below are live, recorded events, and the render shows both --
        # nothing evaporates.
        first = qs[0]
        bad = post(answer_url, {"id": first["id"], "response": wrong_answer(first)})
        if bad["score"] is not False:
            fail("a wrong answer scored %r, expected False" % bad["score"])
        if not bad["explain"].get("why"):
            fail("the verdict carried no explanation, so the page has nothing to render")

        for q in qs:
            got = post(answer_url, {"id": q["id"], "response": correct_answer(q)})
            want = None if q["type"] == "short" else True
            if got["score"] is not want:
                fail("item %s (%s) scored %r, expected %r"
                     % (q["id"], q["type"], got["score"], want))

        try:
            post(answer_url, {"id": "no-such-item", "response": "A"})
            fail("the server accepted an answer for an item that does not exist")
        except urllib.error.HTTPError as exc:
            if exc.code != 404:
                fail("unknown item returned HTTP %d, expected 404" % exc.code)
    finally:
        proc.terminate()

    text = open(out, encoding="utf-8").read()
    for needle in ("A constructed response, written out in full sentences.",
                   "MARK: pending",
                   "[auto: correct]",
                   "[auto: WRONG]"):
        if needle not in text:
            fail("attempt file is missing %r" % needle)
    short = next(q for q in qs if q["type"] == "short")
    if short["model"] not in text:
        fail("attempt file dropped the model answer the marker needs")
    if short["rubric"][0] not in text:
        fail("attempt file dropped the rubric the marker checks against")
    if "- [ ]" in text:
        # Attempt files land in an Obsidian vault, where `- [ ]` is a task and
        # gets swept into unrelated Dataview queries.
        fail("attempt file uses task checkboxes; use (unmarked) instead")

    print("ok: serve scored %d items in-process and wrote %d bytes to %s"
          % (len(qs), len(text), out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
