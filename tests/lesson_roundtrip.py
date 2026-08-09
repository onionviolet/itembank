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
from surfaces import daemon, lesson, quiz                   # noqa: E402
from surfaces.quiz_page import TEMPLATE                     # noqa: E402

LES_BANK = os.path.join(ROOT, "fixtures", "lesson_bank.md")
SMP_BANK = os.path.join(ROOT, "fixtures", "sample_bank.md")
SRC_BANK = os.path.join(ROOT, "fixtures", "lesson_src_bank.md")
SHARED_LESSON = os.path.join(ROOT, "fixtures", "lesson_shared.md")


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


def lesson_bank_text(directive, marker_heading="H"):
    """A minimal bank whose preamble carries `[LESSON-SRC: <directive>]`
    plus its own inline `## LESSON` section, so the RED state fails as a
    wrong `error == ''` and the directive branch must be proven to win over
    the inline section rather than merely coexist with it.
    """
    return ("[LESSON-SRC: %s]\n\n## LESSON\n\n### %s\n\nx\n\n"
            "Q1. s\nA) a\nB) b\nCORRECT: A\n"
            % (directive, marker_heading))


def broken_directive_bank(tmp, directive="nope.md"):
    """A real bank (title, preamble directive, well-formed items) whose
    `[LESSON-SRC:]` cannot be satisfied -- the fixture both the daemon route
    and the CLI twin must degrade on rather than raise.
    """
    p = os.path.join(tmp, "broken_bank.md")
    open(p, "w", encoding="utf-8").write(
        "# Broken source bank\n\n[LESSON-SRC: %s]\n\n"
        "Q1. Which way is up?   (difficulty: recall)\n"
        "A) Up\nB) Down\nC) Sideways\nD) None\n\nCORRECT: A\n\n"
        "WHY BEST: Up is up.\n\nKEY DISCRIMINATOR: Direction.\n\n"
        "SECOND-BEST: B. Down is down; this would be correct if the question "
        "asked which way is down.\n\nDISTRACTOR ANALYSIS:\n"
        "- A) Correct: the canonical direction.\n"
        "- B) The opposite; this would be correct if the question asked down.\n"
        "- C) Not the answer; this would be correct if the question asked sideways.\n"
        "- D) None; this would be correct if the question asked about nothing.\n\n"
        "TRAP: Picking a direction other than up.\n\nCONFIDENCE: high\n"
        % directive)
    return p


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


# ---- plan 03-02: [LESSON-SRC:] external source and path containment --------

def test_lesson_src_shared_parse():
    """A bank whose preamble carries `[LESSON-SRC:]` resolves its headings
    from that external file, with the identical key set an inline lesson
    returns (D-02's one-branch-in-the-loader cost ceiling)."""
    src = itembank.parse_lesson(SRC_BANK)
    if src is None:
        fail("lesson_src_bank did not parse a lesson")
    if src["error"] != "" or src["detail"] != "":
        fail("shared-source lesson must carry empty error/detail: %r" % src)
    shared = itembank.parse_lesson(SHARED_LESSON)
    if [h["text"] for h in src["headings"]] != [h["text"] for h in shared["headings"]]:
        fail("external-source headings differ from the shared file's: %r"
             % [h["text"] for h in src["headings"]])
    if len(src["headings"]) != 2:
        fail("shared fixture must carry exactly 2 headings, got %d"
             % len(src["headings"]))
    if os.path.basename(src["source"]) != "lesson_shared.md":
        fail("source must be the shared file, got %r" % src["source"])
    inline = itembank.parse_lesson(LES_BANK)
    if set(src) != set(inline):
        fail("external-source key set differs from inline key set: %r vs %r"
             % (sorted(src), sorted(inline)))
    qs = itembank.load(SRC_BANK)
    tagged = [q for q in qs if q["lesson_ref"]]
    if not tagged:
        fail("lesson_src_bank must carry at least one LESSON-REF item")
    if tagged[0]["lesson_slug"] not in [h["slug"] for h in src["headings"]]:
        fail("tagged item references a heading missing from the shared lesson")


def test_lesson_src_two_banks_share():
    """Two different banks pointing `[LESSON-SRC:]` at one shared file each
    resolve that one lesson -- the cross-bank case D-02 exists for."""
    tmp = tempfile.mkdtemp()
    open(os.path.join(tmp, "shared.md"), "w", encoding="utf-8").write(
        open(SHARED_LESSON, encoding="utf-8").read())
    lessons = []
    for i, name in enumerate(("bank_a.md", "bank_b.md"), 1):
        p = os.path.join(tmp, name)
        open(p, "w", encoding="utf-8").write(
            "[LESSON-SRC: shared.md]\n\n"
            "Q%d. same question %d\nA) a\nB) b\nCORRECT: A\n"
            % (i, i))
        lessons.append(itembank.parse_lesson(p))
    if any(l is None or l["error"] for l in lessons):
        fail("both banks must resolve the shared lesson: %r" % lessons)
    if [h["text"] for h in lessons[0]["headings"]] != \
       [h["text"] for h in lessons[1]["headings"]]:
        fail("two banks pointing at one shared file must see the same headings")


def test_lesson_src_missing_file():
    tmp = tempfile.mkdtemp()
    p = os.path.join(tmp, "b.md")
    open(p, "w", encoding="utf-8").write(lesson_bank_text("nope.md"))
    r = itembank.parse_lesson(p)
    if r is None:
        fail("a missing LESSON-SRC file must return a dict, not None")
    if r["error"] != "lesson.src_unreadable":
        fail("missing LESSON-SRC file error code wrong: %r" % r["error"])
    if not r["detail"]:
        fail("missing-file detail must be non-empty")


def test_lesson_src_traversal_refused():
    """A relative climb above the bank's directory is refused before any
    open -- proven by a real readable file above the bank whose distinctive
    text must never reach the returned dict (T-3-02)."""
    tmp = tempfile.mkdtemp()
    os.mkdir(os.path.join(tmp, "bank"))
    open(os.path.join(tmp, "secret.md"), "w", encoding="utf-8").write(
        "MARKER_DO_NOT_LEAK")
    p = os.path.join(tmp, "bank", "b.md")
    open(p, "w", encoding="utf-8").write(lesson_bank_text("../secret.md"))
    r = itembank.parse_lesson(p)
    if r is None or r["error"] != "lesson.src_unreadable":
        fail("a climb above the bank's directory must be refused: %r" % r)
    if "MARKER_DO_NOT_LEAK" in repr(r):
        fail("the refused file was opened despite the containment refusal")
    if "../secret.md" not in r["detail"]:
        fail("out-of-tree detail must name the offending path: %r" % r["detail"])


def test_lesson_src_absolute_refused():
    """An absolute directive value resolves to itself, so the same
    containment check catches it without a separate branch."""
    tmp = tempfile.mkdtemp()
    os.mkdir(os.path.join(tmp, "bank"))
    outside = os.path.join(tmp, "outside.md")
    open(outside, "w", encoding="utf-8").write("MARKER_DO_NOT_LEAK")
    p = os.path.join(tmp, "bank", "b.md")
    open(p, "w", encoding="utf-8").write(lesson_bank_text(outside))
    r = itembank.parse_lesson(p)
    if r is None or r["error"] != "lesson.src_unreadable":
        fail("an absolute path outside the bank's directory must be refused")
    if "MARKER_DO_NOT_LEAK" in repr(r):
        fail("an absolute outside path was opened despite the refusal")


def test_lesson_src_subdirectory_accepted():
    tmp = tempfile.mkdtemp()
    bank_dir = os.path.join(tmp, "bank")
    os.makedirs(os.path.join(bank_dir, "sub"))
    open(os.path.join(bank_dir, "sub", "lesson.md"), "w", encoding="utf-8").write(
        "# Sub lesson\n\n## LESSON\n\n### Heading Z\n\nProse.\n")
    p = os.path.join(bank_dir, "b.md")
    open(p, "w", encoding="utf-8").write(lesson_bank_text("sub/lesson.md"))
    r = itembank.parse_lesson(p)
    if r is None or r["error"] != "":
        fail("a subdirectory path inside the bank's directory must be accepted: %r"
             % r)
    if [h["text"] for h in r["headings"]] != ["Heading Z"]:
        fail("subdirectory lesson headings wrong: %r"
             % [h["text"] for h in r["headings"]])
    if os.path.basename(r["source"]) != "lesson.md":
        fail("subdirectory source wrong: %r" % r["source"])


def test_lesson_src_prefix_sibling_refused():
    """A sibling directory whose name merely starts with the bank's own
    directory must be refused -- the separator suffix is load-bearing, and
    a naive prefix test would read `<tmp>/bank-evil/...` for a bank inside
    `<tmp>/bank`."""
    tmp = tempfile.mkdtemp()
    bank_dir = os.path.join(tmp, "bank")
    os.makedirs(bank_dir)
    evil_dir = os.path.join(tmp, "bank-evil")
    os.makedirs(evil_dir)
    open(os.path.join(evil_dir, "lesson.md"), "w", encoding="utf-8").write(
        "MARKER_DO_NOT_LEAK")
    p = os.path.join(bank_dir, "b.md")
    open(p, "w", encoding="utf-8").write(lesson_bank_text("../bank-evil/lesson.md"))
    r = itembank.parse_lesson(p)
    if r is None or r["error"] != "lesson.src_unreadable":
        fail("a sibling sharing the bank dir's name prefix must be refused")
    if "MARKER_DO_NOT_LEAK" in repr(r):
        fail("the prefix-sibling file was opened")


def test_lesson_src_wins_over_inline():
    """A bank carrying both an inline `## LESSON` section and a
    `[LESSON-SRC:]` directive resolves to the external file's headings, and
    the precedence is stated in the function's docstring."""
    tmp = tempfile.mkdtemp()
    open(os.path.join(tmp, "shared.md"), "w", encoding="utf-8").write(
        "# Shared\n\n## LESSON\n\n### External Heading\n\nExternal prose.\n")
    p = os.path.join(tmp, "b.md")
    open(p, "w", encoding="utf-8").write(
        lesson_bank_text("shared.md", marker_heading="Inline Heading"))
    r = itembank.parse_lesson(p)
    headings = [h["text"] for h in r["headings"]] if r else r
    if r is None or headings != ["External Heading"]:
        fail("an external source must win over an inline section: %r" % headings)
    doc = inspect.getdoc(itembank.parse_lesson) or ""
    if "external" not in doc or "inline" not in doc:
        fail("parse_lesson docstring must state the external-over-inline precedence")


def test_lesson_src_stays_out_of_lint_namespace():
    if "lesson.src_unreadable" in itembank.LINT_CODES:
        fail("lesson.src_unreadable must stay unpublished until plan 03-03")


# ---- subprocess: daemon routes and the CLI twin ----------------------------

def test_lesson_src_degraded_daemon_and_cli():
    """A bank whose `[LESSON-SRC:]` cannot be read serves a 200 degraded
    page on the daemon route and the byte-identical page from `itembank
    lesson`, both printing/rendering the empty state plus the locked warning
    note -- one degraded-state policy, and never an exception (T-3-04)."""
    tmp = tempfile.mkdtemp()
    bank = broken_directive_bank(tmp)
    proc, url, _ = start_daemon(tmp)
    try:
        status, body = get(url + "/lesson/broken_bank")
    finally:
        proc.kill()
        proc.wait()
    if status != 200:
        fail("a broken LESSON-SRC must serve 200, got %d" % status)
    for want in ("No lesson yet",
                 "var(--warn)",
                 "The external lesson file for this bank could not be read."):
        if want not in body:
            fail("degraded page missing %r" % want)
    if "<code>nope.md</code>" not in body:
        fail("degraded page must show the unreadable source path in a code "
             "element: %s" % body[body.find("warn"):body.find("warn") + 300])
    for leak in ("CORRECT:", "WHY BEST", "Up is up."):
        if leak in body:
            fail("degraded page leaks answer-key material: %r" % leak)
    if "white-space:nowrap" in body or "text-overflow" in body:
        fail("degraded page must not force no-wrap or ellipsis truncation")
    if "overflow-wrap" not in body:
        fail("the wrapping code element needs an overflow-wrap rule")

    cli_out = os.path.join(tmp, "broken.html")
    res = subprocess.run(
        [sys.executable, os.path.join(ROOT, "itembank.py"), "lesson", bank,
         "--out", cli_out],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=30)
    if res.returncode != 0:
        fail("itembank lesson on a broken directive failed: " + res.stdout)
    if not re.search(r"0 lesson section\(s\) -> ", res.stdout):
        fail("CLI must print 0 sections for the degraded state: %r" % res.stdout)
    cli_page = open(cli_out, encoding="utf-8").read()
    if cli_page != body:
        fail("CLI twin and daemon route disagree on the degraded state")


def test_lesson_plain_empty_state_has_no_warning():
    pg = lesson.lesson_page(SMP_BANK, itembank.load(SMP_BANK),
                            itembank.parse_lesson(SMP_BANK))
    if "No lesson yet" not in pg:
        fail("plain empty state missing heading")
    if "var(--warn)" in pg:
        fail("plain empty state must not carry the warning note")
    if "white-space:nowrap" in pg or "text-overflow" in pg:
        fail("plain empty state must not force no-wrap or ellipsis truncation")


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
test_lesson_src_shared_parse()
test_lesson_src_two_banks_share()
test_lesson_src_missing_file()
test_lesson_src_traversal_refused()
test_lesson_src_absolute_refused()
test_lesson_src_subdirectory_accepted()
test_lesson_src_prefix_sibling_refused()
test_lesson_src_wins_over_inline()
test_lesson_src_stays_out_of_lint_namespace()
test_lesson_src_degraded_daemon_and_cli()
test_lesson_plain_empty_state_has_no_warning()
test_routes_and_cli_twin()
test_page_for_shapes_and_build()
print("ok: lesson roundtrip (slug, parse, fingerprint, LESSON-SRC, degraded state, route, CLI twin, both link directions)")
