#!/usr/bin/env python3
"""One roundtrip harness for the whole lesson architecture: parse, slug,
fingerprint, route, CLI twin, and both link directions.

The silent failures this guards are the ones the lesson feature could ship
with: a lesson that renders while its links point nowhere, a tag that quietly
eats the stem it follows, a lesson parser that truncates on a prose line
shaped like a question marker, and a fingerprint that starts drifting the
moment an item is tagged.

Standard library only, no test framework, runnable as
`python tests/lesson_roundtrip.py`.
"""
import inspect, json, os, re, shutil, subprocess, sys, tempfile, threading, time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import itembank                                            # noqa: E402
from surfaces import daemon, quiz                           # noqa: E402
from surfaces.quiz_page import TEMPLATE                     # noqa: E402

LES_BANK = os.path.join(ROOT, "fixtures", "lesson_bank.md")
SMP_BANK = os.path.join(ROOT, "fixtures", "sample_bank.md")


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def start_daemon(workdir):
    """Launch `itembank daemon <workdir> --no-open --port 0`, drain its stdout
    on a background thread, and return `(proc, url, lines)` once the printed
    banner's URL has been scraped -- the same subprocess-plus-background-
    thread shape `tests/daemon_roundtrip.py` uses.
    """
    args = [sys.executable, "-u", os.path.join(ROOT, "itembank.py"), "daemon",
            workdir, "--no-open", "--port", "0"]
    proc = subprocess.Popen(args, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True)
    lines = []

    def drain():
        for line in proc.stdout:
            lines.append(line)

    threading.Thread(target=drain, daemon=True).start()
    url = None
    for _ in range(200):
        for line in lines:
            m = re.search(r"http://127\.0\.0\.1:\d+/", line)
            if m:
                url = m.group(0).rstrip("/")
                break
        if url:
            break
        if proc.poll() is not None:
            break
        time.sleep(0.05)
    if not url:
        proc.kill()
        fail("daemon did not print a URL; output: " + "".join(lines))
    return proc, url, lines


def get(url):
    with urllib.request.urlopen(url, timeout=5) as res:
        return res.status, res.read().decode("utf-8")


# ---- in-process: slug, parse, fingerprint, served payload ------------------

def test_slug():
    a = itembank.lesson_slug("The Airway, Step By Step")
    b = itembank.lesson_slug("the airway step by step")
    if not (a == b and a):
        fail("lesson_slug is not case/whitespace-insensitive: %r vs %r" % (a, b))
    if itembank.lesson_slug("") != "":
        fail("lesson_slug('') should be ''")
    if itembank.lesson_slug(a) != a:
        fail("lesson_slug is not idempotent: %r -> %r" % (a, itembank.lesson_slug(a)))
    if a != "the-airway-step-by-step":
        fail("lesson_slug produced %r, expected 'the-airway-step-by-step'" % a)


def test_parse_lesson():
    if itembank.parse_lesson(SMP_BANK) is not None:
        fail("sample_bank has no ## LESSON section; parse_lesson should be None")
    L = itembank.parse_lesson(LES_BANK)
    if L is None:
        fail("lesson_bank did not parse a lesson")
    if [h["text"] for h in L["headings"]] != ["The Airway, Step By Step",
                                              "When to Call for Help"]:
        fail("headings not in document order: %r" % [h["text"] for h in L["headings"]])
    if not all(h["slug"] and h["body"] for h in L["headings"]):
        fail("every heading must carry a slug and a body")
    if L["error"] != "" or L["detail"] != "":
        fail("error/detail must be empty in plan 03-01")


def test_prose_line_shaped_like_question_marker():
    tmp = tempfile.mkdtemp()
    bank = os.path.join(tmp, "tricky_bank.md")
    text = """# Tricky bank

## LESSON

### First Heading

Some prose before the lookalike.

Q1. This is a prose line, not a question.

### Second Heading

Real content follows.

Q1. What opens an airway?   (difficulty: recall)
A) Nothing
B) Head-tilt/chin-lift
C) A pulse check
D) Oxygen only

CORRECT: B

WHY BEST: The head-tilt/chin-lift lifts the tongue off the pharynx.

KEY DISCRIMINATOR: A physical manoeuvre that opens the airway.

SECOND-BEST: A. Nothing opens nothing; this would be correct if the question asked what to avoid.

DISTRACTOR ANALYSIS:
- A) Not an airway manoeuvre; this would be correct if the question asked what not to do.
- B) Correct: the standard opening manoeuvre.
- C) A circulation check; this would be correct if the question asked about perfusion.
- D) Oxygen alone does not open an airway; this would be correct if the question asked about adjuncts.

TRAP: Confusing oxygen delivery with airway opening.

CONFIDENCE: high
"""
    open(bank, "w", encoding="utf-8").write(text)
    L = itembank.parse_lesson(bank)
    if L is None or [h["text"] for h in L["headings"]] != ["First Heading", "Second Heading"]:
        fail("parse_lesson truncated at a prose line shaped like Q1. (Pitfall 2)")
    qs = itembank.parse_bank(text)
    if len(qs) != 1 or qs[0]["type"] != "mc":
        fail("parse_bank should return exactly the real item, got %d" % len(qs))


def test_tag_does_not_corrupt_stem():
    qs = itembank.load(LES_BANK)
    tagged = [q for q in qs if q["lesson_ref"]]
    if len(tagged) != 2:
        fail("expected exactly 2 tagged items, got %d" % len(tagged))
    for q in tagged:
        if "LESSON-REF" in q["stem"]:
            fail("tag literal leaked into stem: %r" % q["stem"])
        if q["lesson_ref"] != "The Airway, Step By Step":
            fail("lesson_ref wrong: %r" % q["lesson_ref"])
        if q["lesson_slug"] != itembank.lesson_slug(q["lesson_ref"]):
            fail("lesson_slug not derived from lesson_ref")
    untagged = [q for q in qs if not q["lesson_ref"]]
    if len(untagged) != 1 or untagged[0]["lesson_slug"] != "":
        fail("untagged item must carry an empty lesson_slug")


def test_fingerprint_ignores_tag():
    qs = itembank.load(LES_BANK)
    tagged = [q for q in qs if q["lesson_ref"]][0]
    clean = dict(tagged)
    clean.pop("lesson_ref")
    clean.pop("lesson_slug")
    if itembank.content_fingerprint(tagged) != itembank.content_fingerprint(clean):
        fail("D-04 lock broken: tagging an item changed its fingerprint")


def test_lesson03_compatibility_floor():
    qs = itembank.parse_bank(open(SMP_BANK, encoding="utf-8").read())
    if len(qs) != 6 or [q["type"] for q in qs] != ["mc", "multi", "table", "build", "dnd", "short"]:
        fail("sample_bank no longer parses to the same six-item type sequence")
    first = qs[0]
    if first["stem"] != ("An operator notices the chlorine residual at the far end of the "
                         "distribution network has fallen below the regulatory floor, while "
                         "the reading at the plant outlet is normal. What is the most likely "
                         "explanation?"):
        fail("sample_bank first stem changed")
    if first["opts"] != {"A": "The plant is underdosing chlorine",
                         "B": "Chlorine demand in the network is consuming the residual before "
                              "it reaches the far end",
                         "C": "The far-end sampling tap is contaminated",
                         "D": "The regulatory floor was recently raised"}:
        fail("sample_bank first item options changed")
    if first["correct"] != ["B"]:
        fail("sample_bank first item correct answer changed")


def test_public_item_and_schema():
    qs = itembank.load(LES_BANK)
    for q in qs:
        p = itembank.public_item(q)
        if "lesson_slug" not in p:
            fail("public_item must always carry lesson_slug")
        if p["lesson_slug"] != q["lesson_slug"]:
            fail("public_item lesson_slug must match the question dict")
    schema = json.load(open(os.path.join(ROOT, "schemas", "item.schema.json"),
                            encoding="utf-8"))
    if "lesson_slug" not in schema["properties"]:
        fail("item.schema.json missing lesson_slug property")
    if schema["x-itembank-version"] != 1:
        fail("item.schema.json version must stay 1 (additive change)")


def test_structural_rules():
    if "lesson" in inspect.getsource(itembank.parse_bank):
        fail("parse_bank must not be modified")
    model_src = "\n".join(l for l in open(os.path.join(ROOT, "model.py"),
                                          encoding="utf-8") if not l.lstrip().startswith("#"))
    if "maxsplit" in model_src:
        fail("lesson preamble must use the unbounded split, never maxsplit")
    lesson_src = "\n".join(l for l in open(os.path.join(ROOT, "surfaces", "lesson.py"),
                                           encoding="utf-8") if not l.lstrip().startswith("#"))
    if "def lesson_slug" in lesson_src:
        fail("surfaces/lesson.py must import lesson_slug from model, never redefine it")
    if re.search(r"score_response|canonical_key|explain_payload", lesson_src):
        fail("the reader must hold no key and reach no verdict (D-10)")
    if re.search(r"^import (markdown|mistune|commonmark)", lesson_src, re.M):
        fail("the reader must be standard library only")
    route_keys = set((m, p) for m, p, _ in daemon.ROUTES)
    if set(daemon.ROUTE_CLI) != route_keys:
        fail("ROUTE_CLI keys must equal ROUTES (method, pattern) pairs")
    if ("GET", daemon.LESSON_GET_RE) not in daemon.ROUTE_CLI:
        fail("lesson route missing from ROUTE_CLI")


# ---- subprocess: daemon routes and the CLI twin ----------------------------

def test_routes_and_cli_twin():
    tmp = tempfile.mkdtemp()
    shutil.copy(LES_BANK, tmp)
    shutil.copy(SMP_BANK, tmp)
    proc, url, _ = start_daemon(tmp)
    try:
        status, body = get(url + "/lesson/lesson_bank")
        if status != 200:
            fail("GET /lesson/lesson_bank returned %d" % status)
        if "The Airway, Step By Step" not in body:
            fail("served lesson missing heading text")
        if 'id="the-airway-step-by-step"' not in body:
            fail("served lesson heading missing its slug anchor id")
        for href in ("/quiz/lesson_bank#q1", "/quiz/lesson_bank#q2"):
            if href not in body:
                fail("served lesson missing backlink %s" % href)
        if "No items reference this section yet." not in body:
            fail("orphan heading must render the locked orphan copy")
        for leak in ("CORRECT:", "WHY BEST", "Repositioning is first because"):
            if leak in body:
                fail("served lesson leaks answer-key material: %r" % leak)

        status, empty_body = get(url + "/lesson/sample_bank")
        if status != 200 or "No lesson yet" not in empty_body:
            fail("GET /lesson/sample_bank must render the empty state, got %d" % status)

        try:
            status404, nf_body = get(url + "/lesson/no-such-bank")
        except urllib.error.HTTPError as exc:
            status404, nf_body = exc.code, exc.read().decode("utf-8")
        if status404 != 404:
            fail("GET /lesson/no-such-bank must 404, got %d" % status404)
        if tmp in nf_body or "Traceback" in nf_body:
            fail("404 body leaked a filesystem path or traceback")

        # CLI twin: same render function, byte-identical document.
        cli_out = os.path.join(tmp, "lesson.html")
        res = subprocess.run(
            [sys.executable, os.path.join(ROOT, "itembank.py"), "lesson",
             os.path.join(tmp, "lesson_bank.md"), "--out", cli_out],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=30)
        if res.returncode != 0:
            fail("itembank lesson failed: " + res.stdout)
        if not re.search(r"[0-9]+ lesson section\(s\) -> ", res.stdout):
            fail("CLI success line missing: %r" % res.stdout)
        cli_page = open(cli_out, encoding="utf-8").read()
        if cli_page != body:
            fail("CLI twin and daemon route disagree byte-for-byte")

        # Quiz page: chip present under serve, absent on the static build.
        status, quiz_body = get(url + "/quiz/lesson_bank")
        if status != 200:
            fail("GET /quiz/lesson_bank returned %d" % status)
        if "Read the lesson" not in quiz_body:
            fail("served quiz page missing the lesson chip")
        if 'const LESSON_BASE = "/lesson/lesson_bank"' not in quiz_body:
            fail("served quiz page missing the lesson base constant")
        if 'href="${LESSON_BASE}#${q.lesson_slug}"' not in quiz_body:
            fail("served quiz chip href must compose LESSON_BASE#slug")
        if 'target="_blank"' not in quiz_body:
            fail("lesson chip must open in a new tab")
        m = re.search(r"const Q = (\[.*?\]);", quiz_body)
        if not m:
            fail("could not find the served item array")
        served = json.loads(m.group(1))
        if sum(1 for it in served if it.get("lesson_slug")) != 2:
            fail("served quiz item array must carry exactly 2 non-empty lesson slugs")
    finally:
        proc.kill()
        proc.wait()


def test_page_for_shapes_and_build():
    qs = itembank.load(LES_BANK)
    _, plain = quiz.page_for(LES_BANK, qs)
    if "Read the lesson" in plain:
        fail("page_for without a lesson base must carry no chip (D-12)")
    _, with_base = quiz.page_for(LES_BANK, qs, serve=True,
                                 lesson_base="/lesson/lesson_bank")
    if "Read the lesson" not in with_base:
        fail("page_for with a lesson base must carry the chip")

    build_out = os.path.join(tempfile.mkdtemp(), "q.html")
    res = subprocess.run(
        [sys.executable, os.path.join(ROOT, "itembank.py"), "build", LES_BANK, build_out],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=30)
    if res.returncode != 0:
        fail("itembank build failed: " + res.stdout)
    if "Read the lesson" in open(build_out, encoding="utf-8").read():
        fail("static build page must carry no lesson chip (D-12)")

    pin_at = TEMPLATE.find("location.hash")
    sort_at = TEMPLATE.find("Q.sort")
    if not (0 < pin_at < sort_at):
        fail("fragment-pin step must run before the shuffle")
    if "lesson" not in inspect.getsource(daemon.handle_quiz_get):
        fail("handle_quiz_get must supply the lesson base path")


test_slug()
test_parse_lesson()
test_prose_line_shaped_like_question_marker()
test_tag_does_not_corrupt_stem()
test_fingerprint_ignores_tag()
test_lesson03_compatibility_floor()
test_public_item_and_schema()
test_structural_rules()
test_routes_and_cli_twin()
test_page_for_shapes_and_build()
print("ok: lesson roundtrip (slug, parse, fingerprint, route, CLI twin, both link directions)")
