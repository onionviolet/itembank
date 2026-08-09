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
sys.path.insert(0, os.path.join(ROOT, "tests"))
import itembank                                            # noqa: E402
import protocol_roundtrip                                   # noqa: E402
from surfaces import daemon, lesson, quiz                   # noqa: E402
from surfaces.quiz_page import OFFLINE_JS                   # noqa: E402

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


def clean_mc(stem, ref=""):
    """A minimal otherwise-clean multiple-choice block: every lint-relevant
    field present, so the only findings a lesson check can add are its own.
    Missing [ID:]/[HASH:] warnings are expected and ignored by the lesson
    tests; no error or other warning may come from the item itself."""
    ref_line = "[LESSON-REF: %s]\n" % ref if ref else ""
    return (
        "Q1. %s   (difficulty: recall)\n%s"
        "[OBJECTIVE: emt:airway]\n"
        "A) One\nB) Two\nC) Three\nD) Four\n\n"
        "CORRECT: A\n\n"
        "WHY BEST: One is the keyed answer.\n\n"
        "KEY DISCRIMINATOR: One vs the rest.\n\n"
        "SECOND-BEST: B. Two is the runner-up; this would be correct if the "
        "question asked for two.\n\n"
        "DISTRACTOR ANALYSIS:\n"
        "- A) Correct: the keyed answer.\n"
        "- B) The runner-up; this would be correct if the question asked for two.\n"
        "- C) A filler; this would be correct if the question asked for three.\n"
        "- D) A filler; this would be correct if the question asked for four.\n\n"
        "TRAP: Picking the runner-up.\n\n"
        "CONFIDENCE: high\n"
        % (stem, ref_line))


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


# ---- plan 03-03: lesson lint codes and lint(questions, lesson=...) ---------

def assert_codes_declared(findings):
    for f in findings:
        if f.code not in itembank.LINT_CODES:
            fail("emitted code %r is not declared in LINT_CODES" % f.code)


def test_lesson_lint_codes_published():
    """The four lesson codes are all members of the one published set, which
    stays sorted and duplicate-free (D-05/D-06, plan 03-03 Task 1)."""
    need = {"item.lesson_ref_unknown", "lesson.duplicate_heading",
            "lesson.orphan_heading", "lesson.src_unreadable"}
    missing = need - set(itembank.LINT_CODES)
    if missing:
        fail("lesson lint codes not all published in LINT_CODES: missing %r"
             % sorted(missing))
    codes = itembank.LINT_CODES
    if list(codes) != sorted(codes):
        fail("LINT_CODES is not sorted")
    if len(set(codes)) != len(codes):
        fail("LINT_CODES has duplicates")


def test_lesson_lint_sentinel_exported():
    """LESSON_UNCHECKED is the module-level sentinel default that turns the
    lesson checks off; a caller that supplies lesson data passes whatever
    parse_lesson() returned, including its no-section None."""
    if not hasattr(itembank, "LESSON_UNCHECKED"):
        fail("LESSON_UNCHECKED sentinel is not exported by itembank")
    if "LESSON_UNCHECKED" not in itembank.__all__:
        fail("LESSON_UNCHECKED must be a member of itembank.__all__")


def test_lesson_lint_default_unchanged():
    """lint(qs) with no lesson argument behaves exactly as it did before this
    phase: the sentinel default skips every lesson check, so a lesson-bearing
    bank adds no lesson finding to the baseline output."""
    qs = itembank.load(LES_BANK)
    errors, warnings = itembank.lint(qs)
    if any(e.code.startswith("lesson.") or e.code == "item.lesson_ref_unknown"
           for e in errors):
        fail("default lint must not emit lesson errors: %r" % errors)
    if any(w.code.startswith("lesson.") for w in warnings):
        fail("default lint must not emit lesson warnings: %r" % warnings)


def test_lesson_lint_unknown_reference():
    """A LESSON-REF naming a heading that does not exist is an error, by item
    number, naming the reference key -- never a warning and never a
    render-time crash (D-05, ROADMAP SC3)."""
    tmp = tempfile.mkdtemp()
    bank = os.path.join(tmp, "ref_missing.md")
    open(bank, "w", encoding="utf-8").write(
        "## LESSON\n\n### Existing Heading\n\nprose\n\n"
        + clean_mc("Which is one?", "Missing Section"))
    qs = itembank.load(bank)
    lesson = itembank.parse_lesson(bank)
    if lesson is None or lesson["error"]:
        fail("test bank did not parse a clean lesson: %r" % lesson)
    errors, warnings = itembank.lint(qs, lesson=lesson)
    assert_codes_declared(errors + warnings)
    unknown = [e for e in errors if e.code == "item.lesson_ref_unknown"]
    if len(unknown) != 1:
        fail("expected exactly one unknown-reference error, got %r" % errors)
    e = unknown[0]
    if e.field != "lesson_ref":
        fail("unknown-reference field must be 'lesson_ref', got %r" % e.field)
    if e.item != "Q1":
        fail("unknown-reference item must be the item's own Qn number, got %r"
             % e.item)
    if "Missing Section" not in e.message:
        fail("unknown-reference message must name the referenced heading: %r"
             % e.message)
    if "does not match any lesson heading" not in e.message:
        fail("unknown-reference message must use the locked wording: %r"
             % e.message)
    if str(e) != "Q1: %s" % e.message:
        fail("str() must reproduce the historical tag-colon-message shape: %r"
             % str(e))
    if any(w.code == "item.lesson_ref_unknown" for w in warnings):
        fail("unknown-reference must land in errors, never warnings (SC3)")


def test_lesson_lint_no_section_means_every_ref_unknown():
    """lesson=None (parse_lesson's no-`## LESSON` result) is not a skip: a
    bank with no lesson section at all is a bank where every reference is
    unknown, each reported by its own Qn number."""
    tmp = tempfile.mkdtemp()
    bank = os.path.join(tmp, "no_section.md")
    open(bank, "w", encoding="utf-8").write(
        clean_mc("Which is one?", "Any Heading")
        + clean_mc("Which is two?", "Another Heading").replace("Q1.", "Q2.", 1))
    qs = itembank.load(bank)
    errors, warnings = itembank.lint(qs, lesson=None)
    assert_codes_declared(errors + warnings)
    unknown = [e for e in errors if e.code == "item.lesson_ref_unknown"]
    if len(unknown) != 2:
        fail("a bank with no lesson section must error on every reference, "
             "got %r" % errors)
    if sorted(e.item for e in unknown) != ["Q1", "Q2"]:
        fail("unknown-reference tags wrong: %r" % [e.item for e in unknown])
    if any(w.code == "item.lesson_ref_unknown" for w in warnings):
        fail("unknown-reference must land in errors, never warnings (SC3)")


def test_lesson_lint_matching_ref_adds_nothing():
    """A reference whose slug exists among the lesson's headings adds no
    lesson finding at all -- errors or warnings."""
    tmp = tempfile.mkdtemp()
    bank = os.path.join(tmp, "ok.md")
    open(bank, "w", encoding="utf-8").write(
        "## LESSON\n\n### The Airway, Step By Step\n\nprose\n\n"
        + clean_mc("Which is one?", "The Airway, Step By Step"))
    qs = itembank.load(bank)
    lesson = itembank.parse_lesson(bank)
    errors, warnings = itembank.lint(qs, lesson=lesson)
    assert_codes_declared(errors + warnings)
    if any(e.code.startswith("lesson.") or e.code == "item.lesson_ref_unknown"
           for e in errors):
        fail("a matching reference must add no lesson error: %r" % errors)
    if any(w.code.startswith("lesson.") for w in warnings):
        fail("a fully-referenced lesson must add no lesson warning: %r"
             % warnings)


def test_lesson_lint_duplicate_heading():
    """Two headings whose texts differ but whose slugs collide are one error
    naming both heading texts and the shared slug -- a reference to either is
    ambiguous (D-06)."""
    tmp = tempfile.mkdtemp()
    bank = os.path.join(tmp, "dup.md")
    open(bank, "w", encoding="utf-8").write(
        "## LESSON\n\n### Airway, Step-By-Step!\n\nprose a\n\n"
        "### airway step by step\n\nprose b\n\n"
        + clean_mc("Which is one?", "The Airway, Step By Step"))
    qs = itembank.load(bank)
    lesson = itembank.parse_lesson(bank)
    slugs = [h["slug"] for h in lesson["headings"]]
    if len(slugs) != 2 or slugs[0] != slugs[1] or not slugs[0]:
        fail("fixture headings must collide on the same slug: %r" % slugs)
    errors, warnings = itembank.lint(qs, lesson=lesson)
    assert_codes_declared(errors + warnings)
    dup = [e for e in errors if e.code == "lesson.duplicate_heading"]
    if len(dup) != 1:
        fail("expected exactly one duplicate-heading error, got %r" % errors)
    e = dup[0]
    if e.item != "BANK":
        fail("duplicate-heading is a bank-level finding, got item %r" % e.item)
    for text in ("airway step by step", "Airway, Step-By-Step!", slugs[0]):
        if text not in e.message:
            fail("duplicate-heading message must name both headings and the "
                 "shared slug: %r" % e.message)
    if "collides with" not in e.message:
        fail("duplicate-heading message must use the locked wording: %r"
             % e.message)


def test_lesson_lint_orphan_heading():
    """A heading no item references is a warning and never an error: a lesson
    legitimately teaches more than it tests (D-06)."""
    tmp = tempfile.mkdtemp()
    bank = os.path.join(tmp, "orphan.md")
    open(bank, "w", encoding="utf-8").write(
        "## LESSON\n\n### Referenced Heading\n\nprose a\n\n"
        "### Background Reading\n\nprose b\n\n"
        + clean_mc("Which is one?", "Referenced Heading"))
    qs = itembank.load(bank)
    lesson = itembank.parse_lesson(bank)
    errors, warnings = itembank.lint(qs, lesson=lesson)
    assert_codes_declared(errors + warnings)
    orphan = [w for w in warnings if w.code == "lesson.orphan_heading"]
    if len(orphan) != 1:
        fail("expected exactly one orphan-heading warning, got %r" % warnings)
    w = orphan[0]
    if w.item != "BANK":
        fail("orphan-heading is a bank-level finding, got item %r" % w.item)
    if "Background Reading" not in w.message:
        fail("orphan-heading message must name the unreferenced heading: %r"
             % w.message)
    if "is not referenced by any item" not in w.message:
        fail("orphan-heading message must use the locked wording: %r"
             % w.message)
    if any(e.code == "lesson.orphan_heading" for e in errors):
        fail("an orphan heading is a warning and never an error (D-06)")
    if any(e.code.startswith("lesson.") for e in errors):
        fail("orphan input must produce no lesson error: %r" % errors)


def test_lesson_lint_src_unreadable():
    """An unreadable [LESSON-SRC:] appends exactly one error carrying the
    result's detail text, tagged BANK, and no heading-level findings -- there
    are no headings to check."""
    tmp = tempfile.mkdtemp()
    bank = os.path.join(tmp, "src_broken.md")
    open(bank, "w", encoding="utf-8").write(
        "[LESSON-SRC: missing_lesson.md]\n\n" + clean_mc("Which is one?"))
    qs = itembank.load(bank)
    lesson = itembank.parse_lesson(bank)
    if lesson is None or lesson["error"] != "lesson.src_unreadable":
        fail("fixture must produce the structured unreadable-source result: %r"
             % lesson)
    errors, warnings = itembank.lint(qs, lesson=lesson)
    assert_codes_declared(errors + warnings)
    src = [e for e in errors if e.code == "lesson.src_unreadable"]
    if len(src) != 1:
        fail("expected exactly one src_unreadable error, got %r" % errors)
    e = src[0]
    if e.item != "BANK":
        fail("src_unreadable is a bank-level finding, got item %r" % e.item)
    if lesson["detail"] not in e.message:
        fail("src_unreadable message must carry the result's detail: %r"
             % e.message)
    if "could not be read" not in e.message:
        fail("src_unreadable message must use the locked wording: %r"
             % e.message)
    if any(w.code.startswith("lesson.") for w in warnings) or \
       any(e2.code.startswith("lesson.") and e2.code != "lesson.src_unreadable"
           for e2 in errors):
        fail("no heading-level findings may accompany src_unreadable")


# ---- plan 03-03 Task 3: the coupling guards --------------------------------
# 03-RESEARCH.md Pitfall 3's failure mode: a code that exists in three places
# minus one, where the missing one is a file nobody was looking at. These tests
# lock all three couplings -- the tuple, the schema enum, and the accepted
# namespace prefixes -- so a drift fails locally rather than in CI.

def test_lint_codes_schema_enum_contains_all_codes():
    """Every member of LINT_CODES is a member of the published code enum, so
    the next code added without a schema entry fails locally. The failure
    names the offending members -- the whole value of this test is that it
    says which file to edit."""
    lint_schema = json.load(open(os.path.join(ROOT, "schemas",
                                              "lint_error.schema.json"),
                                 encoding="utf-8"))
    enum = set(lint_schema["properties"]["code"]["enum"])
    missing = set(itembank.LINT_CODES) - enum
    if missing:
        fail("LINT_CODES members missing from schemas/lint_error.schema.json's "
             "code enum: %s" % ", ".join(sorted(missing)))


def test_schema_enum_has_no_undeclared_codes():
    """The reverse containment too: the enum carries no member that is not a
    published code, so a stale enum entry cannot survive."""
    lint_schema = json.load(open(os.path.join(ROOT, "schemas",
                                              "lint_error.schema.json"),
                                 encoding="utf-8"))
    enum = set(lint_schema["properties"]["code"]["enum"])
    undeclared = enum - set(itembank.LINT_CODES)
    if undeclared:
        fail("schemas/lint_error.schema.json's code enum carries members "
             "missing from LINT_CODES: %s" % ", ".join(sorted(undeclared)))


def test_lint_codes_namespace_prefixes_match_protocol():
    """Every namespace prefix appearing in LINT_CODES is one the protocol
    test's accepted set contains -- read from that module, never restated
    here, so the two cannot drift."""
    accepted = set(protocol_roundtrip.LINT_PREFIXES)
    prefixes = {c.split(".", 1)[0] for c in itembank.LINT_CODES}
    unknown = prefixes - accepted
    if unknown:
        fail("namespace prefixes not accepted by tests/protocol_roundtrip.py: %s"
             % ", ".join(sorted(unknown)))


def test_broken_lesson_fixtures_validate_against_schema():
    """Run the linter over each broken lesson fixture as a subprocess with
    JSON output and push every entry through schema_validate.validate -- the
    same validator CI calls. Tolerate the expected non-zero exit and validate
    the parsed output rather than trusting the exit code, so an empty or
    truncated document cannot pass."""
    import schema_validate
    lint_schema = json.load(open(os.path.join(ROOT, "schemas",
                                              "lint_error.schema.json"),
                                 encoding="utf-8"))
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    for bank in (os.path.join(ROOT, "fixtures", "broken_bank.md"),
                 os.path.join(ROOT, "fixtures", "lesson_broken_src_bank.md")):
        r = subprocess.run(
            [sys.executable, os.path.join(ROOT, "itembank.py"), "lint", bank,
             "--json"],
            capture_output=True, text=True, encoding="utf-8", env=env)
        if r.returncode == 0:
            fail("lint exited 0 on deliberately broken fixture %s" % bank)
        payload = json.loads(r.stdout)
        if not payload["errors"] and not payload["warnings"]:
            fail("lint --json on %s produced an empty document" % bank)
        for key in ("errors", "warnings"):
            for i, entry in enumerate(payload[key]):
                errs = schema_validate.validate(entry, lint_schema)
                if errs:
                    fail("%s %s[%d] fails lint_error.schema.json: %s"
                         % (bank, key, i, errs))


def test_unknown_reference_is_error_not_warning():
    """The machine-checkable form of ROADMAP SC3: the unknown-reference
    finding lands in the errors list and never the warnings list, so a future
    well-meaning downgrade to a warning fails a test rather than quietly
    weakening the phase's acceptance gate."""
    tmp = tempfile.mkdtemp()
    bank = os.path.join(tmp, "ref_missing.md")
    open(bank, "w", encoding="utf-8").write(
        "## LESSON\n\n### Existing Heading\n\nprose\n\n"
        + clean_mc("Which is one?", "Missing Section"))
    qs = itembank.load(bank)
    errors, warnings = itembank.lint(qs, lesson=itembank.parse_lesson(bank))
    if not any(e.code == "item.lesson_ref_unknown" for e in errors):
        fail("unknown-reference must appear in the errors list (ROADMAP SC3)")
    if any(w.code == "item.lesson_ref_unknown" for w in warnings):
        fail("unknown-reference must never appear in the warnings list (SC3)")


# ---- plan 03-04 Task 1: blocks -- fenced code, lists, tables ----------------
# D-08's deliberately small block scope, and the Phase 9 seam: a fenced block
# carrying an info string must render as a pre/code element with a
# `language-<info>` class, source preserved verbatim apart from HTML escaping,
# so Phase 9 attaches KaTeX and the run button by selector without re-parsing.

def test_render_fenced_code_with_language():
    h = lesson.render_markdown("```python\nx = 1\n```\n")
    if "<pre" not in h or "language-python" not in h:
        fail("fenced code must render a pre/code element with the language "
             "class: %r" % h)
    if "x = 1" not in h:
        fail("fenced code content missing: %r" % h)


def test_render_fenced_code_without_language():
    h = lesson.render_markdown("```\nplain\n```\n")
    if "<pre" not in h or "language-" in h:
        fail("a fenced block with no info string must carry no language "
             "class: %r" % h)
    if "plain" not in h:
        fail("plain fenced content missing: %r" % h)


def test_render_fenced_code_verbatim_against_inline_pass():
    src = ("```text\n**not bold** _not italic_ `not code` [not](a link)\n"
           "# not a heading\n- not a list item\n```\n")
    h = lesson.render_markdown(src)
    for want in ("**not bold**", "_not italic_", "`not code`", "[not](a link)",
                 "# not a heading", "- not a list item"):
        if want not in h:
            fail("inline pass mangled fenced content: missing %r in %r"
                 % (want, h))
    for banned in ("<strong>", "<em>", "<a ", "<h2", "<ul", "<li>"):
        if banned in h:
            fail("inline pass reached inside a fence: %r in %r" % (banned, h))


def test_render_fenced_code_escaped():
    h = lesson.render_markdown("```html\n<script>x</script> & y\n```\n")
    if "&lt;script&gt;" not in h or "&amp;" not in h:
        fail("fenced content must be HTML-escaped: %r" % h)
    if "<script>" in h:
        fail("fenced content leaked raw markup: %r" % h)


def test_render_fenced_code_unterminated():
    h = lesson.render_markdown("```python\nunterminated\n")
    if "<pre" not in h or "unterminated" not in h:
        fail("an unterminated fence must render to the end of the section "
             "rather than raising: %r" % h)


def test_render_lists():
    h = lesson.render_markdown("- one\n- two\n")
    if "<ul>" not in h or h.count("<li>") != 2:
        fail("dash list must render an unordered list with one item per "
             "line: %r" % h)
    h = lesson.render_markdown("1. one\n2. two\n")
    if "<ol>" not in h or h.count("<li>") != 2:
        fail("digit list must render an ordered list with one item per "
             "line: %r" % h)


def test_render_table():
    h = lesson.render_markdown("| a | b |\n| --- | --- |\n| 1 | 2 |\n")
    if "<table" not in h or "<th" not in h or "<td" not in h:
        fail("a pipe table with a separator row must render as a table: %r"
             % h)


def test_render_malformed_table_falls_back_to_paragraph():
    h = lesson.render_markdown("a | b but no table here\n")
    if "<table" in h or "<p" not in h:
        fail("a lone pipe line must render as a paragraph: %r" % h)
    h2 = lesson.render_markdown("| a | b |\n| 1 | 2 |\n")
    if "<table" in h2:
        fail("a run with no separator row must not render a table: %r" % h2)
    h3 = lesson.render_markdown("| a | b |\n| --- | --- |\n| 1 | 2 | 3 |\n")
    if "<table" in h3:
        fail("a row with a different cell count must fall back to a "
             "paragraph: %r" % h3)


def test_render_overflow_containers():
    src = open(os.path.join(ROOT, "surfaces", "lesson.py"),
               encoding="utf-8").read()
    if "overflow-x:auto" not in src:
        fail("the reader must style wide code and tables with their own "
             "horizontal scroll container")
    code = "\n".join(l for l in src.splitlines()
                     if not l.lstrip().startswith("#"))
    if re.search(r"white-space:nowrap|text-overflow", code):
        fail("the reader must never force no-wrap or ellipsis truncation "
             "on lesson prose")


def test_render_deep_heading_same_size():
    h = lesson.render_markdown("#### deeper than the grammar\n")
    if "<h2>deeper than the grammar</h2>" not in h:
        fail("a heading deeper than ### must render at the same Display "
             "size as a section heading: %r" % h)


def test_lesson_bank_fixture_renders_all_block_kinds():
    pg = lesson.lesson_page(LES_BANK, itembank.load(LES_BANK),
                            itembank.parse_lesson(LES_BANK))
    for want in ("<table", "<ul>", "<ol>", "<pre", "language-text",
                 "&lt;img onerror=y&gt;", "&amp;"):
        if want not in pg:
            fail("fixture lesson page missing %r" % want)
    if pg.count("<pre") < 2:
        fail("fixture must carry two fenced blocks, got %d"
             % pg.count("<pre"))


def test_lesson_shared_fixture_carries_math_seam():
    shared = itembank.parse_lesson(SHARED_LESSON)
    h = lesson.render_markdown(shared["body"])
    if "language-math" not in h:
        fail("the shared fixture must carry the math fence Phase 9 attaches "
             "to")


# ---- plan 03-04 Task 2: inlines -- emphasis, inline code, links ------------
# The inline pass runs over placeholder-protected, already-escaped text only:
# code spans are lifted first so they are never re-scanned, escaping happens
# before emphasis and link patterns so a markup-shaped stem or heading can
# never reach the page as markup, and only a relative path or an http/https
# URL becomes a clickable anchor (T-3-11).

def test_render_inline_emphasis():
    h = lesson.render_markdown("a **b** c _d_ e\n")
    if "<strong>b</strong>" not in h or "<em>d</em>" not in h:
        fail("double markers must render strong and single markers em: %r"
             % h)


def test_render_inline_code():
    h = lesson.render_markdown("use `x < y` here\n")
    if "<code" not in h or "&lt;" not in h:
        fail("inline code must render as an escaped code element: %r" % h)
    if "<strong>" in h:
        fail("inline code content must never be re-scanned for inline "
             "patterns: %r" % h)


def test_render_links():
    h = lesson.render_markdown("see [the notes](notes.md)\n")
    if "<a " not in h or "notes.md" not in h:
        fail("a relative link must render as an anchor: %r" % h)
    h = lesson.render_markdown("see [x](javascript:alert(1))\n")
    if "<a " in h:
        fail("a scheme-bearing link target must render as plain text: %r"
             % h)
    h = lesson.render_markdown("see [docs](https://example.com/a?x=1&y=2)\n")
    if "<a " not in h or "&amp;" not in h:
        fail("an https link must render with an escaped target: %r" % h)


def test_render_prose_escaped():
    h = lesson.render_markdown("an <img onerror=y> tag & an amp\n")
    if "&lt;img" not in h or "&amp;" not in h or "<img" in h:
        fail("markup-shaped prose must render escaped: %r" % h)


def test_render_word_boundary_emphasis():
    h = lesson.render_markdown("snake_case_name stays whole\n")
    if "<em>" in h:
        fail("an underscore inside an identifier must not split the word: %r"
             % h)


def test_render_malformed_markers_do_not_raise():
    lesson.render_markdown("unmatched ** and _ and ` here\n")


def test_render_heading_markup_slug_vs_visible():
    h = lesson.render_markdown('### What about <B> & "Q"?\n\nProse.\n')
    if 'id="what-about-b-q"' not in h:
        fail("heading anchor id must come from the slug of the plain text: "
             "%r" % h)
    if 'What about &lt;B&gt; &amp; &quot;Q&quot;?' not in h:
        fail("heading visible text must carry the escaped characters: %r"
             % h)


def test_lesson_bank_fixture_renders_inlines():
    pg = lesson.lesson_page(LES_BANK, itembank.load(LES_BANK),
                            itembank.parse_lesson(LES_BANK))
    for want in ("<strong>name</strong>", "<em>repeat</em>",
                 "<code>run report</code>",
                 '<a href="call-checklist.md">',
                 "&lt;script&gt;", 'onerror=&quot;x&quot;'):
        if want not in pg:
            fail("fixture lesson page missing inline rendering %r" % want)


def test_full_page_escapes_markup_shaped_bank():
    """The phase's Tampering assertion, proved rather than trusted: a bank
    whose heading, prose, table cell, list item and item stem all carry
    markup-shaped text renders the escaped forms and never the raw forms --
    including in the anchor id derived from the heading and in the backlink
    row derived from the stem. This project's threat model is one local
    user with no adversary, so the discipline is correctness first: a stray
    angle bracket in a stem must not break the page."""
    tmp = tempfile.mkdtemp()
    bank = os.path.join(tmp, "inject.md")
    open(bank, "w", encoding="utf-8").write(
        "# Inject bank\n\n"
        "## LESSON\n\n"
        "### A & <B> Heading\n\n"
        "Prose with <img onerror=y> and & amp.\n\n"
        "| Cell | Value |\n| --- | --- |\n| <td> | & |\n\n"
        "- <li> item\n\n"
        "Q1. Stem with <script> alert(1) </script>?   (difficulty: recall)\n"
        "[LESSON-REF: A & <B> Heading]\n"
        "A) One\nB) Two\nC) Three\nD) Four\n\n"
        "CORRECT: A\n\n"
        "WHY BEST: One is the keyed answer.\n\n"
        "KEY DISCRIMINATOR: One vs the rest.\n\n"
        "SECOND-BEST: B. Two is the runner-up; this would be correct if the "
        "question asked for two.\n\n"
        "DISTRACTOR ANALYSIS:\n"
        "- A) Correct: the keyed answer.\n"
        "- B) The runner-up; this would be correct if the question asked for two.\n"
        "- C) A filler; this would be correct if the question asked for three.\n"
        "- D) A filler; this would be correct if the question asked for four.\n\n"
        "TRAP: Picking the runner-up.\n\n"
        "CONFIDENCE: high\n")
    qs = itembank.load(bank)
    L = itembank.parse_lesson(bank)
    pg = lesson.lesson_page(bank, qs, L)
    for want in ("A &amp; &lt;B&gt; Heading",
                 'id="a-b-heading"',
                 "&lt;img onerror=y&gt;",
                 "&amp; amp",
                 "&lt;td&gt;",
                 "&lt;li&gt; item",
                 "Stem with &lt;script&gt; alert(1) &lt;/script&gt;"):
        if want not in pg:
            fail("escaped form missing from the full page: %r" % want)
    # The raw forms must not appear AS CONTENT: the table/list/heading
    # markup tags legitimately contain "<td>", "<li>" and "<B>", so the
    # leak fingerprints are the doubled or adjacent sequences only raw
    # content would produce.
    for banned in ("<img onerror", "<td><td>", "<li><li>", "<script> alert",
                   "<B> Heading"):
        if banned in pg:
            fail("raw markup-shaped text reached the page: %r" % banned)


# ---- plan 03-05: --ref filtering and the CLI output contract ---------------

def run_lesson(args):
    """Run `itembank lesson ...` as a subprocess so the hard stop's exit
    status and stderr are both observable."""
    return subprocess.run(
        [sys.executable, os.path.join(ROOT, "itembank.py"), "lesson"] + args,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30)


def test_lesson_ref_filters_one_section():
    """`--ref` renders exactly the matched heading's section and its
    backlinks and nothing else -- the same document narrowed, not a second
    layout (D-11)."""
    qs = itembank.load(LES_BANK)
    L = itembank.parse_lesson(LES_BANK)
    full = lesson.lesson_page(LES_BANK, qs, L)
    one = lesson.lesson_page(LES_BANK, qs, L, ref=L["headings"][0]["text"])
    if not isinstance(one, str) or len(one) >= len(full):
        fail("--ref must narrow the page (got %d vs %d chars)"
             % (len(one) if isinstance(one, str) else -1, len(full)))
    if L["headings"][1]["text"] in one:
        fail("the other heading's prose must be absent from the filtered page")
    if one.count('<section id="') != 1:
        fail("the filtered page must contain exactly one section, got %d"
             % one.count('<section id="'))
    if "No items reference this section yet." in one:
        fail("the other heading's orphan backlinks must be absent")
    card = '<div class="card">'
    if one[:one.index(card)] != full[:full.index(card)]:
        fail("the filtered page must keep the full page's chrome and byline")


def test_lesson_ref_slug_variants_resolve():
    """Casing, spacing and punctuation differences in the caller's text
    resolve through the one slugifier to the same section (D-03) -- the
    exact assertion that proves the slug is doing the matching, not raw
    string comparison."""
    qs = itembank.load(LES_BANK)
    L = itembank.parse_lesson(LES_BANK)
    full = lesson.lesson_page(LES_BANK, qs, L)
    exact = lesson.lesson_page(LES_BANK, qs, L, ref=L["headings"][0]["text"])
    if not isinstance(exact, str) or len(exact) >= len(full):
        fail("the exact-text --ref must narrow the page")
    for variant in ("the airway step by step", "The  Airway,  Step By Step",
                    "the-airway step-by-step"):
        if lesson.lesson_page(LES_BANK, qs, L, ref=variant) != exact:
            fail("ref variant %r must resolve to the exact section (D-03)"
                 % variant)


def test_lesson_ref_miss_signals_none():
    """A ref naming no heading returns None from the render function -- the
    caller (`cmd_lesson`) turns that into the hard stop, so the render
    function itself carries no process-exit path (T-3-12)."""
    qs = itembank.load(LES_BANK)
    L = itembank.parse_lesson(LES_BANK)
    if lesson.lesson_page(LES_BANK, qs, L, ref="no such heading") is not None:
        fail("a no-match --ref must signal a miss, not render a document")
    if lesson.lesson_page(SMP_BANK, itembank.load(SMP_BANK),
                          itembank.parse_lesson(SMP_BANK),
                          ref="anything") is not None:
        fail("--ref against a bank with no lesson section is the same miss")


def test_lesson_ref_no_ref_renders_everything():
    """No ref -- and an empty ref -- render the whole lesson exactly as the
    daemon route does; filtering is opt-in."""
    qs = itembank.load(LES_BANK)
    L = itembank.parse_lesson(LES_BANK)
    full = lesson.lesson_page(LES_BANK, qs, L)
    if lesson.lesson_page(LES_BANK, qs, L, ref=None) != full:
        fail("no ref must render the whole lesson")
    if lesson.lesson_page(LES_BANK, qs, L, ref="") != full:
        fail("an empty --ref must render the whole lesson")


def test_lesson_ref_cli_match_exits_zero_count_one():
    """`itembank lesson <bank> --ref <heading>` exits 0 and reports the one
    section it actually rendered (D-11)."""
    out = os.path.join(tempfile.mkdtemp(), "r1.html")
    res = run_lesson([LES_BANK, "--ref", "The Airway, Step By Step",
                      "--out", out])
    if res.returncode != 0:
        fail("--ref on a matching heading failed: " + res.stderr + res.stdout)
    if "1 lesson section(s) -> " not in res.stdout:
        fail("--ref success line must report 1 section: %r" % res.stdout)
    if not os.path.exists(out):
        fail("--ref must write the filtered page")
    if open(out, encoding="utf-8").read().count('<section id="') != 1:
        fail("filtered file must contain exactly one section")


def test_lesson_ref_cli_slug_variant_byte_identical():
    """The same heading typed with different casing, spacing and punctuation
    writes a byte-identical file to the exact-text run -- the slugifier is
    what reconciles them."""
    tmp = tempfile.mkdtemp()
    exact = os.path.join(tmp, "exact.html")
    variant = os.path.join(tmp, "variant.html")
    r1 = run_lesson([LES_BANK, "--ref", "The Airway, Step By Step",
                     "--out", exact])
    r2 = run_lesson([LES_BANK, "--ref", "the airway,  step  by step",
                     "--out", variant])
    if r1.returncode != 0 or r2.returncode != 0:
        fail("slug-variant runs must both exit 0: %r / %r"
             % (r1.stderr, r2.stderr))
    if open(exact, encoding="utf-8").read() != \
       open(variant, encoding="utf-8").read():
        fail("slug-variant output must be byte-identical to the exact-text run")


def test_lesson_ref_cli_miss_hard_stops():
    """A --ref naming no heading exits non-zero with the locked message
    naming both the requested text and the bank, and writes no file."""
    out = os.path.join(tempfile.mkdtemp(), "r2.html")
    res = run_lesson([LES_BANK, "--ref", "no such heading", "--out", out])
    if res.returncode == 0:
        fail("a no-match --ref must exit non-zero")
    if "no lesson heading matching" not in res.stderr:
        fail("hard-stop message missing from stderr: %r" % res.stderr)
    if repr("no such heading") not in res.stderr or LES_BANK not in res.stderr:
        fail("hard-stop message must name the requested text and the bank: %r"
             % res.stderr)
    if os.path.exists(out):
        fail("a hard stop must not write the output file")


def test_lesson_ref_cli_no_lesson_bank_miss():
    """An explicit --ref against a bank with no lesson section at all is the
    same miss, on the same locked terms -- never a silent empty render."""
    res = run_lesson([SMP_BANK, "--ref", "anything"])
    if res.returncode == 0:
        fail("--ref against a bank with no lesson must hard-stop")
    if "no lesson heading matching" not in res.stderr:
        fail("no-lesson --ref must use the locked miss message: %r"
             % res.stderr)


def test_lesson_route_selects_no_section():
    """The daemon route passes no ref: the browser's way to reach a section
    is the fragment D-07 locked, never a query parameter, so no second
    selection mechanism exists."""
    if "ref" in inspect.signature(daemon.handle_lesson_get).parameters:
        fail("the lesson route handler must not accept a ref")
    if "ref=" in inspect.getsource(daemon.handle_lesson_get):
        fail("the lesson route handler must not pass a ref to the render")


def test_lesson_page_carries_no_exit_path():
    if "sys.exit" in inspect.getsource(lesson.lesson_page):
        fail("lesson_page must carry no process-exit path")


# ---- plan 03-05 Task 2: the CLI's observable contract ---------------------

def test_lesson_cli_default_output_path():
    """No --out writes beside the bank with a lesson-suffixed HTML name
    derived from the bank's own name, exactly as cmd_study derives its
    default -- one derivation rule for sibling commands."""
    tmp = tempfile.mkdtemp()
    bank = os.path.join(tmp, "lesson_bank.md")
    shutil.copy(LES_BANK, bank)
    res = run_lesson([bank])
    if res.returncode != 0:
        fail("lesson with no --out failed: " + res.stdout + res.stderr)
    expected = os.path.join(tmp, "lesson_bank_lesson.html")
    if not os.path.exists(expected):
        fail("default output path not written: %r" % expected)
    if "2 lesson section(s) -> " not in res.stdout:
        fail("default run must report the heading count: %r" % res.stdout)


def test_lesson_cli_out_creates_containing_directory():
    """--out into a nested directory that does not exist creates it, the way
    cmd_study's default-output derivation does."""
    tmp = tempfile.mkdtemp()
    nested = os.path.join(tmp, "sub", "dir", "c.html")
    res = run_lesson([LES_BANK, "--out", nested])
    if res.returncode != 0:
        fail("lesson --out into a new directory failed: " + res.stdout + res.stderr)
    if not os.path.exists(nested):
        fail("--out must create the containing directory")


def test_lesson_cli_exactly_one_status_line():
    """Exactly one status line in the locked count-arrow-path form, and
    nothing else -- no progress line, no per-section output, no document on
    stdout (E5)."""
    out = os.path.join(tempfile.mkdtemp(), "c1.html")
    res = run_lesson([LES_BANK, "--out", out])
    if res.returncode != 0:
        fail("lesson failed: " + res.stdout + res.stderr)
    locked = [l for l in res.stdout.splitlines()
              if re.match(r"^[0-9]+ lesson section\(s\) -> ", l)]
    if len(locked) != 1:
        fail("exactly one locked status line expected, got %d: %r"
             % (len(locked), res.stdout))
    if len(res.stdout.splitlines()) != 1:
        fail("no progress or per-section output allowed: %r" % res.stdout)


def test_lesson_cli_no_lesson_bank_writes_empty_and_exits_zero():
    """A bank with no lesson section writes the empty-state page and exits
    0 with a count of 0 -- the same degraded-state policy as the route, not
    a second one (T-3-04)."""
    out = os.path.join(tempfile.mkdtemp(), "c2.html")
    res = run_lesson([SMP_BANK, "--out", out])
    if res.returncode != 0:
        fail("a bank with no lesson section must exit 0: "
             + res.stdout + res.stderr)
    if "0 lesson section(s) -> " not in res.stdout:
        fail("no-lesson run must report 0 sections: %r" % res.stdout)
    if "No lesson yet" not in open(out, encoding="utf-8").read():
        fail("no-lesson run must write the empty-state page")


def test_lesson_cli_broken_src_writes_degraded_and_exits_zero():
    """A bank whose external lesson source cannot be read writes the
    degraded page and exits 0 with a count of 0 (T-3-04)."""
    out = os.path.join(tempfile.mkdtemp(), "c3.html")
    bank = os.path.join(ROOT, "fixtures", "lesson_broken_src_bank.md")
    res = run_lesson([bank, "--out", out])
    if res.returncode != 0:
        fail("a broken LESSON-SRC must exit 0: " + res.stdout + res.stderr)
    if "0 lesson section(s) -> " not in res.stdout:
        fail("broken-source run must report 0 sections: %r" % res.stdout)
    pg = open(out, encoding="utf-8").read()
    if "No lesson yet" not in pg or "var(--warn)" not in pg:
        fail("broken-source run must write the degraded warning page")


def test_lesson_cli_src_bank_reports_heading_count():
    """An external-source bank reports the heading count its lesson actually
    carries (2 in the shared fixture)."""
    out = os.path.join(tempfile.mkdtemp(), "c4.html")
    bank = os.path.join(ROOT, "fixtures", "lesson_src_bank.md")
    res = run_lesson([bank, "--out", out])
    if res.returncode != 0:
        fail("external-source lesson failed: " + res.stdout + res.stderr)
    if "2 lesson section(s) -> " not in res.stdout:
        fail("external-source run must report its heading count: %r"
             % res.stdout)


def test_lesson_cli_file_byte_identical_to_render():
    """The machine-readable form of D-07: the CLI's written file equals what
    the render function produces, which is what the daemon route sends."""
    out = os.path.join(tempfile.mkdtemp(), "c1.html")
    res = run_lesson([LES_BANK, "--out", out])
    if res.returncode != 0:
        fail("lesson failed: " + res.stdout + res.stderr)
    page = lesson.lesson_page(LES_BANK, itembank.load(LES_BANK),
                              itembank.parse_lesson(LES_BANK))
    if open(out, encoding="utf-8").read() != page:
        fail("CLI file must equal the render function's output byte-for-byte")


def test_lesson_help_lists_ref_and_out():
    res = subprocess.run(
        [sys.executable, os.path.join(ROOT, "itembank.py"), "lesson",
         "--help"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30)
    if res.returncode != 0:
        fail("lesson --help failed: " + res.stderr)
    if "--ref" not in res.stdout or "--out" not in res.stdout:
        fail("lesson --help must list both --ref and --out: %r" % res.stdout)


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
        # Served quiz pages carry BOOT metadata only (plan 04-01 Test 1): the
        # resolving lesson-slug set moves from the per-item array into BOOT,
        # and the served client blanks chips for slugs outside it.
        m = re.search(r"const BOOT = (\{.*?\});", quiz_body)
        if not m:
            fail("could not find the served BOOT metadata")
        boot = json.loads(m.group(1))
        if sorted(boot.get("lesson_slugs") or []) != [
                "the-airway-step-by-step", "when-to-call-for-help"]:
            fail("served BOOT must carry every resolving lesson slug, got %r"
                 % boot.get("lesson_slugs"))
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

    # --force dead-anchor gap (D-12): an item whose LESSON-REF does not
    # resolve to a heading must have its served slug blanked even when the
    # lint gate is bypassed, so the chip is omitted rather than linking to a
    # dead anchor. (Regression for the gap the verifier found in 03-01.)
    dangling = list(qs)
    dangling[1]["lesson_slug"] = "missing-section"
    _, dangling_page = quiz.page_for(LES_BANK, dangling, serve=True,
                                     lesson_base="/lesson/lesson_bank",
                                     lesson_slugs={"the-airway-step-by-step"})
    m = re.search(r"const BOOT = (\{.*?\});", dangling_page)
    if not m:
        fail("could not find the served BOOT metadata in the dangling page")
    boot = json.loads(m.group(1))
    if boot.get("lesson_slugs") != ["the-airway-step-by-step"]:
        fail("dangling LESSON-REF must restrict BOOT lesson_slugs, got %r"
             % boot.get("lesson_slugs"))
    _, no_headings = quiz.page_for(LES_BANK, qs, serve=True,
                                   lesson_base="/lesson/lesson_bank",
                                   lesson_slugs=set())
    m0 = re.search(r"const BOOT = (\{.*?\});", no_headings)
    if not m0:
        fail("could not find the served BOOT metadata in the no-headings page")
    if json.loads(m0.group(1)).get("lesson_slugs"):
        fail("chip slugs must all be blank when no lesson heading resolves (--force)")

    build_out = os.path.join(tempfile.mkdtemp(), "q.html")
    res = subprocess.run(
        [sys.executable, os.path.join(ROOT, "itembank.py"), "build", LES_BANK, build_out],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=30)
    if res.returncode != 0:
        fail("itembank build failed: " + res.stdout)
    if "Read the lesson" in open(build_out, encoding="utf-8").read():
        fail("static build page must carry no lesson chip (D-12)")

    pin_at = OFFLINE_JS.find("location.hash")
    sort_at = OFFLINE_JS.find("Q.sort")
    if not (0 < pin_at < sort_at):
        fail("fragment-pin step must run before the shuffle")
    if "lesson" not in inspect.getsource(daemon.handle_quiz_get):
        fail("handle_quiz_get must supply the lesson base path")


# ---- plan 03-06: spec-coverage assertions (LESSON-05) ---------------------

def test_spec_documents_lesson_grammar():
    """Every construct the LESSON grammar must state appears in model.SPEC --
    the format contract an authoring agent reads with no source access
    (LESSON-05). The strings assert meaning, not style: each is the plainest
    way the rule can be stated, and a future rewrite that changes the meaning
    fails here instead of shipping a spec that lies."""
    s = itembank.SPEC
    for want in (
        "## LESSON",                      # the section marker
        "###",                            # the subheading level
        "first `Qn.`",                    # placement above the first question
        "without a lesson section parses exactly as it",  # no-lesson promise
        "[LESSON-SRC:",                   # the external-source directive
        "relative to the bank file",      # path resolution rule
        "outside the bank",               # containment refusal
        "takes precedence",               # external wins over inline
        "[LESSON-REF:",                   # the item tag
        "lowercased",                     # slug rule
        "whitespace",                     # slug rule
        "punctuation",                    # slug rule
        "collide",                        # collision is predictable
        "literal text",                   # what does not render
        "info string",                    # fenced-block convention
        "later phase",                    # the Phase 9 seam
        "parses as a real question",      # the one constraint
        "stays in the prose",             # the one constraint
    ):
        if want not in s:
            fail("SPEC must document %r for the LESSON grammar" % want)


def test_spec_lists_reader_scope():
    """The spec names exactly the constructs plan 03-04 shipped in
    render_markdown(): headings, paragraphs, lists, tables, inline code,
    fenced code, bold/italic and links -- nothing else."""
    s = itembank.SPEC
    for want in ("headings", "paragraphs", "lists", "tables", "inline code",
                 "fenced code", "bold", "italic", "links"):
        if want not in s:
            fail("SPEC must name %r in the rendered-markdown scope" % want)


def test_spec_item_tag_lives_in_shared_fields():
    """The item tag is a shared field, not only a mention inside the lesson
    section: it must appear before the type list starts, where an author
    reading the shared fields sees it without reaching the new section."""
    s = itembank.SPEC
    tag_at = s.find("[LESSON-REF:")
    types_at = s.find("THE FIVE ITEM TYPES")
    if tag_at < 0 or types_at < 0 or tag_at > types_at:
        fail("LESSON-REF must be listed in the shared-fields block")


def test_spec_names_every_lesson_lint_code():
    """The spec names all four lesson codes and each is a published LINT_CODES
    member -- the code list is derived, never restated, so a rename fails here
    instead of leaving the contract describing a code that no longer exists
    (T-3-08). The error/warning split and each trigger are stated too."""
    s = itembank.SPEC
    lesson_codes = [c for c in itembank.LINT_CODES
                    if c.startswith("lesson.") or c == "item.lesson_ref_unknown"]
    if len(lesson_codes) != 4:
        fail("expected exactly 4 lesson lint codes, got %d: %r"
             % (len(lesson_codes), lesson_codes))
    for c in lesson_codes:
        if c not in s:
            fail("SPEC must name published lint code %r" % c)
    for want in ("error", "warning", "collide", "no heading",
                 "missing", "no item references"):
        if want not in s:
            fail("SPEC must state the lint severity split and triggers: %r"
                 % want)


def test_spec_existing_contract_intact():
    """Every existing substring other tests and CI rely on survives the
    additive rewrite (T-3-14)."""
    s = itembank.SPEC
    for keep in ("THE FIVE ITEM TYPES", "DISTRACTOR ANALYSIS",
                 "THE RULE THAT SURVIVES EVERY TYPE", "[ID:]", "[HASH:]"):
        if keep not in s:
            fail("existing SPEC substring lost: %r" % keep)


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
test_lesson_lint_codes_published()
test_lesson_lint_sentinel_exported()
test_lesson_lint_default_unchanged()
test_lesson_lint_unknown_reference()
test_lesson_lint_no_section_means_every_ref_unknown()
test_lesson_lint_matching_ref_adds_nothing()
test_lesson_lint_duplicate_heading()
test_lesson_lint_orphan_heading()
test_lesson_lint_src_unreadable()
test_lint_codes_schema_enum_contains_all_codes()
test_schema_enum_has_no_undeclared_codes()
test_lint_codes_namespace_prefixes_match_protocol()
test_broken_lesson_fixtures_validate_against_schema()
test_unknown_reference_is_error_not_warning()
test_render_fenced_code_with_language()
test_render_fenced_code_without_language()
test_render_fenced_code_verbatim_against_inline_pass()
test_render_fenced_code_escaped()
test_render_fenced_code_unterminated()
test_render_lists()
test_render_table()
test_render_malformed_table_falls_back_to_paragraph()
test_render_overflow_containers()
test_render_deep_heading_same_size()
test_lesson_bank_fixture_renders_all_block_kinds()
test_lesson_shared_fixture_carries_math_seam()
test_render_inline_emphasis()
test_render_inline_code()
test_render_links()
test_render_prose_escaped()
test_render_word_boundary_emphasis()
test_render_malformed_markers_do_not_raise()
test_render_heading_markup_slug_vs_visible()
test_lesson_bank_fixture_renders_inlines()
test_full_page_escapes_markup_shaped_bank()
test_lesson_ref_filters_one_section()
test_lesson_ref_slug_variants_resolve()
test_lesson_ref_miss_signals_none()
test_lesson_ref_no_ref_renders_everything()
test_lesson_ref_cli_match_exits_zero_count_one()
test_lesson_ref_cli_slug_variant_byte_identical()
test_lesson_ref_cli_miss_hard_stops()
test_lesson_ref_cli_no_lesson_bank_miss()
test_lesson_route_selects_no_section()
test_lesson_page_carries_no_exit_path()
test_lesson_cli_default_output_path()
test_lesson_cli_out_creates_containing_directory()
test_lesson_cli_exactly_one_status_line()
test_lesson_cli_no_lesson_bank_writes_empty_and_exits_zero()
test_lesson_cli_broken_src_writes_degraded_and_exits_zero()
test_lesson_cli_src_bank_reports_heading_count()
test_lesson_cli_file_byte_identical_to_render()
test_lesson_help_lists_ref_and_out()
test_lesson_src_degraded_daemon_and_cli()
test_lesson_plain_empty_state_has_no_warning()
test_routes_and_cli_twin()
test_page_for_shapes_and_build()
test_spec_documents_lesson_grammar()
test_spec_lists_reader_scope()
test_spec_item_tag_lives_in_shared_fields()
test_spec_names_every_lesson_lint_code()
test_spec_existing_contract_intact()
print("ok: lesson roundtrip (slug, parse, fingerprint, LESSON-SRC, degraded state, route, CLI twin, both link directions, lesson lint, coupling guards)")
