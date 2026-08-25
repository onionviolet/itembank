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
import subjects                                            # noqa: E402
from surfaces import daemon, lesson, quiz                   # noqa: E402
from surfaces.cli import SPEC_03_1                          # noqa: E402
from surfaces.quiz_page import OFFLINE_JS                   # noqa: E402

PUBLIC_ITEM_GOLDEN_PRE_13_5 = os.path.join(
    ROOT, "fixtures", "quiz_public_item_pre_13_5.json")


# ---- plan 03.1-06 Task 3: spec documents the new grammar; 09-02 fold ------


def test_spec_documents_new_grammar_constructs():
    """03.1-06 Task 3 Test 1: `itembank spec` output documents the new
    grammar -- ## TERMS + [[term]] (with the reserved zh= meta), [!KEY]
    (id/hash, cloze, Anki export), [!EXAMPLE], [!CHECK: <id>] (same-bank
    only), the Educational Objective line (private payload), and
    styles/<id>.md (Voice/Rules/Exemplar + locked house rows)."""
    spec = subprocess.run([sys.executable, os.path.join(ROOT, "itembank.py"),
                           "spec"], capture_output=True, text=True,
                          cwd=ROOT).stdout
    for needle, label in [("## TERMS", "TERMS"), ("[[term]]", "term ref"),
                          ("zh=", "reserved zh= meta"), ("[!KEY", "KEY"),
                          ("[!EXAMPLE", "EXAMPLE"), ("[!CHECK", "CHECK"),
                          ("Objective:", "Objective line"),
                          ("styles/", "style file")]:
        if needle not in spec:
            fail("spec must document %r for the new grammar (%s)"
                 % (needle, label))


def test_lesson_layout_folded_into_09_02():
    """03.1-06 Task 3 Test 2 (D-04, LESSON-17): 09-02-PLAN.md's Task 1
    action and artifacts enumerate the lesson_layout enum separate|inline in
    the subject_profiles entry contract -- EMT/Math separate, CS inline --
    with no registry version bump in this phase."""
    text = open(os.path.join(ROOT, ".planning", "phases",
                             "09-subject-invariant-loop-emt-math-cs-integration",
                             "09-02-PLAN.md"), encoding="utf-8").read()
    if "lesson_layout" not in text:
        fail("09-02-PLAN.md must name lesson_layout in the entry contract")
    if '"separate"' not in text or '"inline"' not in text:
        fail("09-02-PLAN.md must enumerate lesson_layout separate|inline")
    if not ("EMT" in text and "Math" in text and "CS" in text):
        fail("09-02-PLAN.md must commit EMT/Math separate and CS inline")


def test_spec_only_bank_round_trips_new_constructs():
    """03.1-06 Task 3 Test 3: a bank written from the spec alone parses and
    lints clean (zero errors) for the new grammar constructs."""
    bank = """# Spec-only fixture (synthetic)

## LESSON

### The Spec-Only Section

A [[glossary]] term used once in the prose, then a must-memorize card.

> [!KEY: The Spec Card]

{{cloze::The spec card}} front.

> [!EXAMPLE]

An example callout shows the shape.

> [!CHECK: q1]

## TERMS

glossary | a term defined in the lesson's own glossary | gloss

Q1. What does the spec-only bank exercise?

[OBJECTIVE: emt:probe.spec_only]
Objective: It exercises the grammar the spec documents.
[TYPE: mc]
A) the new grammar
B) the old grammar
C) the same grammar
CORRECT: A
WHY BEST: because every new construct parses
KEY DISCRIMINATOR: B is right when the constructs predate the spec
DISTRACTOR ANALYSIS: B would be correct only for a pre-3.1 bank
TRAP: none
CONFIDENCE: high

[LESSON-REF: The Spec-Only Section]
"""
    tmp = os.path.join(tempfile.mkdtemp(), "spec_only.md")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(bank)
    try:
        out = subprocess.run([sys.executable, os.path.join(ROOT, "itembank.py"),
                              "lint", tmp], capture_output=True, text=True,
                             cwd=ROOT)
        if out.returncode != 0 or "0 errors" not in out.stdout:
            fail("spec-only bank must lint with zero errors; got %r"
                 % out.stdout[-400:])
    finally:
        shutil.rmtree(os.path.dirname(tmp), ignore_errors=True)

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


# ---- plan 03.1-01 Task 2: template migration onto the shared visual system --
# 03.1-UI-SPEC §2 (Reader CSS LOCKED): LESSON_TEMPLATE stops carrying a
# private type system and composes theme_css + SHARED_CSS + LESSON_CSS.
# 03.1-UI-SPEC §12: byte identity covers the rendered content region with
# the shared <style> block explicitly excluded -- the exclusion is the
# recorded decision, not a convenient omission -- plus parse identity.

GOLDEN_CONTENT_P3 = os.path.join(ROOT, "fixtures",
                                 "lesson_golden_phase3_content.txt")
GOLDEN_PARSE_P3 = os.path.join(ROOT, "fixtures",
                               "lesson_golden_phase3_parse.json")


def _lesson_content_region(pg):
    """The rendered `__BODY__` region of LESSON_TEMPLATE -- the content
    between `<div class="card">` and the card's closing `</div>`. The page
    now carries the plan 03.1-04 style footer between the card and the
    closing wrapper, which this extraction skips. The card div carries the
    09-04 `id="lesson-content"` target; the opening tag is matched loosely
    so the attribute addition does not break the extraction."""
    m = re.search(
        r'<div class="card"[^>]*>(.*?)</div>\s*'
        r'<p class="style-foot">.*?</p>\s*</div></body></html>',
        pg, re.S)
    if not m:
        fail("lesson page has no <div class=\"card\"> content region")
    return m.group(1)


def test_lesson_style_composes_theme_shared_lesson():
    """Test 1: the rendered lesson page's <style> composes theme_css then
    SHARED_CSS then LESSON_CSS, and LESSON_TEMPLATE carries no private type
    system -- no font-size, font-family, line-height, or color literal
    (03.1-UI-SPEC §2 Reader CSS LOCKED)."""
    from surfaces.presentation import SHARED_CSS
    from surfaces.lesson import LESSON_CSS, LESSON_TEMPLATE
    pg = lesson.lesson_page(LES_BANK, itembank.load(LES_BANK),
                            itembank.parse_lesson(LES_BANK))
    m = re.search(r"<style>(.*?)</style>", pg, re.S)
    if not m:
        fail("lesson page carries no <style> block")
    style = m.group(1)
    theme_at = style.find(":root{")
    shared_at = style.find("*{box-sizing:border-box}")
    lesson_at = style.find(LESSON_CSS[:40])
    if shared_at < 0 or lesson_at < 0:
        fail("composed style missing SHARED_CSS or LESSON_CSS layer")
    if not (theme_at < shared_at < lesson_at):
        fail("style layers must compose theme_css then SHARED_CSS then "
             "LESSON_CSS (got %d, %d, %d)" % (theme_at, shared_at,
                                               lesson_at))
    for banned in ("font-size", "font-family", "line-height"):
        if banned in LESSON_TEMPLATE:
            fail("LESSON_TEMPLATE must not carry a %s literal "
                 "(03.1-UI-SPEC §2)" % banned)
    if re.search(r"#[0-9a-fA-F]{3,8}\b", LESSON_TEMPLATE):
        fail("LESSON_TEMPLATE must not carry a color literal")


def test_lesson_heading_ramp_locked():
    """Test 2: the locked heading ramp -- h1 text-display, h2 text-heading,
    h3 text-body at 600, with the asymmetric space-6/space-3 and
    space-5/space-2 margins (03.1-UI-SPEC §4 LOCKED)."""
    pg = lesson.lesson_page(LES_BANK, itembank.load(LES_BANK),
                            itembank.parse_lesson(LES_BANK))
    m = re.search(r"<style>(.*?)</style>", pg, re.S)
    style = m.group(1)
    ramp = {
        "h1{font-size:32px;font-weight:600;line-height:1.1;"
        "margin:0 0 var(--space-3)}":
            "h1 must render at text-display with margin space-3",
        "h2{font-size:20px;font-weight:600;line-height:1.2;"
        "margin:var(--space-6) 0 var(--space-3)}":
            "h2 must render at text-heading with margins space-6/space-3",
        "h3{font-size:16px;font-weight:600;line-height:1.4;"
        "margin:var(--space-5) 0 var(--space-2)}":
            "h3 must render at text-body 600 with margins space-5/space-2",
    }
    for rule, msg in ramp.items():
        if rule not in style:
            fail(msg + ": missing %r" % rule)
    if "font-size:18px;line-height:var(--leading-lesson)" not in style:
        fail("lesson prose must render at text-lesson 18px/1.65")
    if "max-width:var(--measure-prose)" not in style:
        fail("the prose column must cap at --measure-prose")
    if ".wrap{max-width:calc(var(--measure-prose) + 2 * var(--space-3) + 2 * var(--space-4))" not in style:
        fail("D1: the wrap cap must pay the .card 24px side padding so prose renders the contracted 531px")


def test_lesson_content_region_byte_identical_phase3():
    """Test 3: for a bank using none of the new constructs, the rendered
    content region is byte-identical to the Phase 3 golden with the shared
    <style> block explicitly excluded (03.1-UI-SPEC §12.1-§12.2 LOCKED --
    the exclusion is the recorded decision)."""
    golden = open(GOLDEN_CONTENT_P3, encoding="utf-8").read()
    pg = lesson.lesson_page(LES_BANK, itembank.load(LES_BANK),
                            itembank.parse_lesson(LES_BANK))
    content = _lesson_content_region(pg)
    if content != golden:
        fail("content region drifted from the Phase 3 golden "
             "(%d chars, expected %d; style block excluded per "
             "03.1-UI-SPEC §12)" % (len(content), len(golden)))


def test_lesson_parse_identity_phase3():
    """Test 4: the parsed question dicts and parsed lesson structure are
    byte-equal to the Phase 3 goldens -- the parse is what Directive §4.4
    actually protects (03.1-UI-SPEC §12.3). The lesson dict's `source` field
    is the bank's absolute path -- machine-dependent metadata, not lesson
    content -- so it is compared by basename only; every other field is
    byte-equal (a golden generated on one machine must not fail the floor
    on another)."""
    golden = json.load(open(GOLDEN_PARSE_P3, encoding="utf-8"))
    qs = itembank.load(LES_BANK)
    les = itembank.parse_lesson(LES_BANK)
    if json.dumps(qs, sort_keys=True) != json.dumps(golden["qs"],
                                                    sort_keys=True):
        fail("parsed question dicts drifted from the Phase 3 golden")
    now = dict(les)
    then = dict(golden["lesson"])
    # `source` is the absolute bank path (machine- and platform-dependent:
    # "C:\\Users\\..." on Windows, "/mnt/c/..." under WSL). Normalize
    # separators before comparing the basename so the floor is portable.
    def _base(path):
        return os.path.basename((path or "").replace("\\", "/"))
    if _base(now.pop("source", "")) != _base(then.pop("source", "")):
        fail("parsed lesson `source` basename drifted from the Phase 3 golden")
    if json.dumps(now, sort_keys=True) != json.dumps(then, sort_keys=True):
        fail("parsed lesson structure drifted from the Phase 3 golden")


# ---- plan 03.2-02: provenance grammar -- ## SOURCES, [SRC:], [OBJ:] -------
# D-11/D-20 (SEED-04/SEED-09): an additive ## SOURCES registry resolves
# [SRC:]/[OBJ:] ids; an unresolvable id is a lint error naming the id and the
# file; a duplicate registry id is a lint error; a bank using none of the
# constructs parses and renders byte-identically (the compatibility floor,
# Directive §4.4).

def provenance_clean_item():
    """A minimal otherwise-clean mc item carrying a resolvable [SRC:] and
    [OBJ:]: the item itself contributes no error, so the only provenance
    findings a test can observe are its own."""
    return (
        "Q1. Which finding suggests an at-risk airway?   (difficulty: application)\n"
        "[SRC: aaos12 p. 214]\n"
        "[OBJ: emt:airway]\n"
        "[OBJECTIVE: emt:airway]\n"
        "A) Snoring respirations with a weak effort\n"
        "B) Thirst\n"
        "C) Tachycardia\n"
        "D) Warm dry skin\n\n"
        "CORRECT: A\n\n"
        "WHY BEST: Snoring with a weak effort is obstruction with failing "
        "compensation.\n\n"
        "KEY DISCRIMINATOR: Air movement itself is threatened.\n\n"
        "SECOND-BEST: B. Thirst is a perfusion finding; this would be correct "
        "if the question asked about perfusion.\n\n"
        "DISTRACTOR ANALYSIS:\n"
        "- A) Correct: the keyed answer.\n"
        "- B) Perfusion.\n"
        "- C) Compensation.\n"
        "- D) Normal.\n\n"
        "TRAP: Any abnormal vital sign.\n\n"
        "CONFIDENCE: high\n")


def provenance_bank(tmp, registry_rows, item_text):
    """A real bank (title, ## SOURCES registry, one item) for the provenance
    fixtures; the registry rows are pipe rows `id | locators`."""
    p = os.path.join(tmp, "prov.md")
    open(p, "w", encoding="utf-8").write(
        "# Provenance fixture (synthetic)\n\n## SOURCES\n\n" + registry_rows
        + "\n\n" + item_text)
    return p


def test_provenance_registry_parses_and_directives_resolve():
    """A ## SOURCES registry parses into {source_id: locators}; [SRC:] and
    [OBJ:] directives resolve against it with item tags; a bank whose
    directives all resolve lints clean of prov errors (D-11, SEED-04)."""
    import model
    tmp = tempfile.mkdtemp()
    try:
        bank = provenance_bank(
            tmp,
            "aaos12 | AAOS Emergency Care 12th ed., pp. 210-215\n"
            "emt:airway | EMT airway chapter, sect. 5\n",
            provenance_clean_item())
        ps = model.parse_sources(bank)
        if ps["sources"].get("aaos12") != \
                "AAOS Emergency Care 12th ed., pp. 210-215":
            fail("## SOURCES must parse aaos12 -> locators, got %r"
                 % ps["sources"])
        if ps["sources"].get("emt:airway") != "EMT airway chapter, sect. 5":
            fail("## SOURCES must parse emt:airway -> locators, got %r"
                 % ps["sources"])
        if [d["id"] for d in ps["srcs"]] != ["aaos12"]:
            fail("[SRC:] directive list wrong: %r" % ps["srcs"])
        if [d["obj"] for d in ps["objs"]] != ["emt:airway"]:
            fail("[OBJ:] directive list wrong: %r" % ps["objs"])
        if ps["srcs"][0]["item"] != "Q1" or ps["objs"][0]["item"] != "Q1":
            fail("directives must be tagged by their item, got %r / %r"
                 % (ps["srcs"][0]["item"], ps["objs"][0]["item"]))
        qs = itembank.load(bank)
        errors, warnings = itembank.lint(qs, sources=ps)
        assert_codes_declared(errors + warnings)
        if any(e.code.startswith("prov.") for e in errors):
            fail("resolved directives must emit no prov error: %r" % errors)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_provenance_lint_unknown_and_duplicate_ids():
    """An unresolvable [SRC:] or [OBJ:] id is a lint error naming the id and
    the file; a duplicate source id in the registry is a bank-level lint
    error (D-11, T-032-05)."""
    import model
    tmp = tempfile.mkdtemp()
    try:
        bank = provenance_bank(
            tmp,
            "aaos12 | AAOS Emergency Care 12th ed.\n"
            "aaos12 | AAOS Emergency Care 12th ed. (duplicate row)\n",
            provenance_clean_item()
            .replace("[SRC: aaos12 p. 214]", "[SRC: nope p. 1]")
            .replace("[OBJ: emt:airway]", "[OBJ: emt:nope]"))
        ps = model.parse_sources(bank)
        if ps["duplicates"] != ["aaos12"]:
            fail("duplicate registry ids must be reported, got %r"
                 % ps["duplicates"])
        qs = itembank.load(bank)
        errors, warnings = itembank.lint(qs, sources=ps)
        assert_codes_declared(errors + warnings)
        src = [e for e in errors if e.code == "prov.src_unknown"]
        if len(src) != 1:
            fail("expected exactly one prov.src_unknown, got %r" % errors)
        if "nope" not in src[0].message:
            fail("src_unknown must name the id: %r" % src[0].message)
        if os.path.basename(bank) not in src[0].message:
            fail("src_unknown must name the file: %r" % src[0].message)
        if src[0].item != "Q1":
            fail("src_unknown must be tagged by the item, got %r" % src[0].item)
        obj = [e for e in errors if e.code == "prov.obj_unknown"]
        if len(obj) != 1 or "emt:nope" not in obj[0].message \
                or os.path.basename(bank) not in obj[0].message:
            fail("obj_unknown must name the id and the file: %r" % obj)
        dup = [e for e in errors if e.code == "prov.src_duplicate"]
        if len(dup) != 1 or "aaos12" not in dup[0].message:
            fail("src_duplicate must name the duplicated id: %r" % dup)
        if dup[0].item != "BANK":
            fail("src_duplicate must be a bank-level finding, got %r"
                 % dup[0].item)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_provenance_lint_codes_published():
    """The three provenance codes are members of the one published set, which
    stays sorted and duplicate-free (D-16)."""
    need = {"prov.src_unknown", "prov.obj_unknown", "prov.src_duplicate"}
    missing = need - set(itembank.LINT_CODES)
    if missing:
        fail("provenance codes not all published in LINT_CODES: missing %r"
             % sorted(missing))
    codes = itembank.LINT_CODES
    if list(codes) != sorted(codes):
        fail("LINT_CODES is not sorted")
    if len(set(codes)) != len(codes):
        fail("LINT_CODES has duplicates")


def test_provenance_compatibility_floor():
    """A bank using none of ## SOURCES, [SRC:], or [OBJ:] renders
    byte-identically to the Phase 3.1 fixture (content region, style block
    excluded per 03.1-UI-SPEC §12) and parses identically -- the provenance
    grammar is additive (D-20, SEED-09)."""
    import model
    golden = open(GOLDEN_CONTENT_P3, encoding="utf-8").read()
    pg = lesson.lesson_page(LES_BANK, itembank.load(LES_BANK),
                            itembank.parse_lesson(LES_BANK))
    if _lesson_content_region(pg) != golden:
        fail("no-provenance bank content region drifted from the Phase 3 "
             "golden (style block excluded per 03.1-UI-SPEC §12)")
    plain_text = open(LES_BANK, encoding="utf-8").read()
    prov_text = plain_text.replace(
        "A short preamble paragraph before the lesson section.",
        "## SOURCES\n\n"
        "aaos12 | AAOS Emergency Care 12th ed., pp. 210-215\n\n"
        "A short preamble paragraph before the lesson section.", 1)
    prov_text = prov_text.replace(
        "[LESSON-REF: The Airway, Step By Step]\n[OBJECTIVE: emt:airway]\n",
        "[LESSON-REF: The Airway, Step By Step]\n"
        "[SRC: aaos12 p. 214]\n[OBJ: emt:airway]\n[OBJECTIVE: emt:airway]\n")
    tmp = tempfile.mkdtemp()
    try:
        prov_bank = os.path.join(tmp, "prov_compat.md")
        open(prov_bank, "w", encoding="utf-8").write(prov_text)
        plain_qs = itembank.parse_bank(plain_text)
        prov_qs = itembank.load(prov_bank)
        if json.dumps(plain_qs, sort_keys=True) != \
                json.dumps(prov_qs, sort_keys=True):
            fail("adding ## SOURCES/[SRC:]/[OBJ:] must not change the parse")
        golden_parse = json.load(open(GOLDEN_PARSE_P3, encoding="utf-8"))
        if json.dumps(prov_qs, sort_keys=True) != \
                json.dumps(golden_parse["qs"], sort_keys=True):
            fail("parsed question dicts drifted from the Phase 3 golden")
        ps = model.parse_sources(prov_bank)
        if "aaos12" not in ps["sources"] or not ps["srcs"] or not ps["objs"]:
            fail("the provenance-decorated copy must be read by parse_sources")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---- plan 03.2-04: winnowing paraphrase lint (D-13), style.unsourced_specific
# ---- (D-14), and the [CASE:]/[PREREQ:] grammar (D-15/D-16) -----------------

# The synthetic corpus file written beside each fixture bank (D-17: real
# corpora live outside the repo; in-repo fixtures stay synthetic). The first
# eight words are the verbatim phrase the copy fixture transcribes.
PARA_SOURCE = (
    "A patent airway is the single highest priority and must be opened before "
    "oxygen is administered in every case of respiratory distress. Chest "
    "compressions maintain perfusion during cardiac arrest while ventilations "
    "deliver oxygen to the lungs. The paramedic assesses responsiveness first "
    "and then checks breathing circulation and skin color before deciding on "
    "transport."
)
PARA_COPY_PHRASE = "A patent airway is the single highest priority"
PARA_FILLERS = ("florble", "squonk", "glorby", "zorch", "blinky",
                "wobble", "snargle", "grunkle", "fizzle")


def paraphrase_bank(tmp, corpus_text=PARA_SOURCE):
    """A bank plus a real source corpus file beside it. The bank's registry
    carries two ids that both resolve to the corpus file: `aaos12` (the copy
    fixture's source) and `overlap-src` (the overlap fixture's source)."""
    corpus_dir = os.path.join(tmp, "corpus")
    os.makedirs(corpus_dir, exist_ok=True)
    open(os.path.join(corpus_dir, "ch5.txt"), "w",
         encoding="utf-8").write(corpus_text)
    bank = os.path.join(tmp, "para.md")
    open(bank, "w", encoding="utf-8").write(
        "# Paraphrase fixture (synthetic)\n\n## SOURCES\n\n"
        "aaos12 | corpus/ch5.txt\noverlap-src | corpus/ch5.txt\n\n"
        + _para_item(1, "aaos12", PARA_COPY_PHRASE + ".")
        + "\n" + _para_item(2, "overlap-src", _overlap_candidate())
        + "\n" + _para_item(3, None,
                            "Normal lung sounds indicate adequate gas exchange "
                            "in the absence of distress."))
    return bank


def _para_item(number, src_id, why):
    """A minimal parseable mc item carrying an optional resolved [SRC:]."""
    src = "[SRC: %s corpus/ch5.txt]\n" % src_id if src_id else ""
    return ("Q%d. Which finding fits?   (difficulty: recall)\n"
            "%s[OBJECTIVE: emt:airway]\n"
            "A) Yes\nB) No\n\n"
            "CORRECT: A\n\n"
            "WHY BEST: %s\n\n"
            "CONFIDENCE: high\n" % (number, src, why))


def _overlap_candidate():
    """A high-overlap, low-run candidate: nine 6-word windows of the source,
    each broken by a filler word, so the candidate shares ~27 k-grams with
    the source (fingerprint Jaccard well above 0.25) while no verbatim run
    reaches 8 consecutive words (max run of 3 k-grams -> 6 words)."""
    words = PARA_SOURCE.split()
    starts = [0, 6, 12, 18, 24, 30, 36, 42, 47]  # 0-based 6-word windows
    parts = []
    for i, s in enumerate(starts):
        parts.append(" ".join(words[s:s + 6]))
        if i < len(starts) - 1:
            parts.append(PARA_FILLERS[i])
    return " ".join(parts)


def test_paraphrase_check_copy_overlap_and_pass():
    """Test 1: the winnowing-based check errors at >=8 consecutive copied
    words (prov.paraphrase_copy), warns above Jaccard 0.25
    (prov.paraphrase_overlap), and passes below both -- and the thresholds
    are tunable parameters (D-13, SEED-05)."""
    import model
    r = model.paraphrase_check(
        PARA_COPY_PHRASE + " more words here", PARA_SOURCE,
        winnow_threshold=8, jaccard_threshold=0.25)
    if not r["copy"] or r["copy_words"] < 8:
        fail("an 8+ word verbatim run must be a copy, got %r" % r)
    r2 = model.paraphrase_check(
        _overlap_candidate(), PARA_SOURCE,
        winnow_threshold=8, jaccard_threshold=0.25)
    if r2["copy"]:
        fail("the overlap candidate must not trip the copy check: %r" % r2)
    if not r2["overlap"] or r2["jaccard"] <= 0.25:
        fail("the overlap candidate must warn above Jaccard 0.25, got %r" % r2)
    if r2["copy_words"] >= 8:
        fail("the overlap candidate's longest verbatim run must stay under 8 "
             "words, got %d" % r2["copy_words"])
    r3 = model.paraphrase_check(
        "Independent prose that shares no phrase with the corpus at all.",
        PARA_SOURCE, winnow_threshold=8, jaccard_threshold=0.25)
    if r3["copy"] or r3["overlap"]:
        fail("an independent text must pass both checks, got %r" % r3)
    # The thresholds are parameters: lowering winnow_threshold turns the
    # overlap candidate's 6-word blocks into a copy; raising jaccard_threshold
    # silences the overlap warning.
    r4 = model.paraphrase_check(
        _overlap_candidate(), PARA_SOURCE,
        winnow_threshold=4, jaccard_threshold=0.25)
    if not r4["copy"]:
        fail("lowering winnow_threshold to 4 must catch 6-word runs, got %r"
             % r4)
    r5 = model.paraphrase_check(
        _overlap_candidate(), PARA_SOURCE,
        winnow_threshold=8, jaccard_threshold=0.5)
    if r5["overlap"]:
        fail("raising jaccard_threshold to 0.5 must silence the warning, got %r"
             % r5)


def test_paraphrase_lint_codes_fire_and_never_echo_source_text():
    """Test 1 + Test 3 through the one lint surface: prov.paraphrase_copy
    errors, prov.paraphrase_overlap warns, an independent item passes -- and
    the lint report never contains a word of the source text, and lint writes
    no new file to disk (fingerprints only, D-13, T-032-12)."""
    import model
    tmp = tempfile.mkdtemp()
    try:
        bank = paraphrase_bank(tmp)
        ps = model.parse_sources(bank)
        qs = itembank.load(bank)
        before = set(os.listdir(tmp))
        errors, warnings = itembank.lint(qs, sources=ps, paraphrase={})
        after = set(os.listdir(tmp))
        if before != after:
            fail("lint must write nothing to disk (fingerprints only): %r"
                 % (before ^ after))
        codes = [e.code for e in errors]
        copy = [e for e in errors if e.code == "prov.paraphrase_copy"]
        if len(copy) != 1 or copy[0].item != "Q1":
            fail("expected exactly one prov.paraphrase_copy on Q1, got %r"
                 % errors)
        overlap = [w for w in warnings if w.code == "prov.paraphrase_overlap"]
        if len(overlap) != 1 or overlap[0].item != "Q2":
            fail("expected exactly one prov.paraphrase_overlap warning on Q2, "
                 "got %r" % warnings)
        clean = [e for e in errors + warnings
                 if e.item == "Q3" and e.code.startswith("prov.paraphrase")]
        if clean:
            fail("an independent item must pass the paraphrase checks: %r"
                 % clean)
        report = " ".join(str(e) + " " + str(w)
                          for e in errors for w in warnings)
        report += " ".join(str(e) for e in errors)
        report += " ".join(str(w) for w in warnings)
        for needle in (PARA_SOURCE, PARA_COPY_PHRASE,
                       " ".join(PARA_SOURCE.split()[:12])):
            if needle in report:
                fail("the lint report must never echo the source text")
        for code in ("prov.paraphrase_copy", "prov.paraphrase_overlap"):
            if code not in itembank.LINT_CODES:
                fail("paraphrase code %r must be a published LINT_CODES member"
                     % code)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_paraphrase_thresholds_are_settings_and_roundtrip():
    """Test 2: the thresholds are settings with defaults 8 and 0.25,
    registered in the schema and itembank.json, and round-tripping through
    the itembank config surface (D-13)."""
    import model
    from surfaces import settings as ssettings
    if ssettings.paraphrase_defaults() != \
            {"winnow_threshold": 8, "jaccard_threshold": 0.25}:
        fail("paraphrase_defaults() drifted: %r"
             % ssettings.paraphrase_defaults())
    if model.PARAPHRASE_DEFAULTS != \
            {"winnow_threshold": 8, "jaccard_threshold": 0.25}:
        fail("model.PARAPHRASE_DEFAULTS drifted: %r"
             % model.PARAPHRASE_DEFAULTS)
    schema = ssettings.load_schema()
    para = schema["properties"].get("paraphrase")
    if not para or "paraphrase" not in schema.get("required", []):
        fail("paraphrase is not a required top-level settings group")
    if para["properties"]["winnow_threshold"]["default"] != 8:
        fail("schema winnow_threshold default must be 8")
    if para["properties"]["jaccard_threshold"]["default"] != 0.25:
        fail("schema jaccard_threshold default must be 0.25")
    on_disk = json.load(open(os.path.join(ROOT, "itembank.json"),
                             encoding="utf-8"))
    if on_disk.get("paraphrase") != \
            {"winnow_threshold": 8, "jaccard_threshold": 0.25}:
        fail("itembank.json must carry the paraphrase defaults: %r"
             % on_disk.get("paraphrase"))
    tmp = tempfile.mkdtemp()
    try:
        shutil.copyfile(os.path.join(ROOT, "itembank.json"),
                        os.path.join(tmp, "itembank.json"))
        for key, value in (("paraphrase.winnow_threshold", "12"),
                           ("paraphrase.jaccard_threshold", "0.4")):
            r = subprocess.run(
                [sys.executable, os.path.join(ROOT, "itembank.py"),
                 "config", "set", key, value, "--base", tmp],
                capture_output=True, text=True, cwd=ROOT)
            if r.returncode != 0:
                fail("config set %s %s failed: %s"
                     % (key, value, r.stdout + r.stderr))
        loaded = ssettings.load_settings(tmp)
        if loaded["paraphrase"]["winnow_threshold"] != 12 or \
                loaded["paraphrase"]["jaccard_threshold"] != 0.4:
            fail("the paraphrase thresholds did not round-trip: %r"
                 % loaded["paraphrase"])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_unsourced_specific_requires_a_source():
    """Test 1: an item carrying a numeral, unit, or dose with no resolved
    [SRC:] errors with style.unsourced_specific; with a source it passes --
    a structural check registering into the closed LINT_CODES catalogue
    without opening it (D-14, T-032-13)."""
    import model
    item_text = (
        "Q1. What is the correct dose?   (difficulty: recall)\n"
        "[OBJECTIVE: emt:airway]\n"
        "A) 0.5 mg\nB) 1 mg\nC) 2 mg\n\n"
        "CORRECT: A\n\n"
        "WHY BEST: 0.5 mg is the correct dose.\n\n"
        "TRAP: Confusing the dose with the route.\n")
    tmp = tempfile.mkdtemp()
    try:
        bare = os.path.join(tmp, "bare.md")
        open(bare, "w", encoding="utf-8").write(
            "# Unsourced fixture (synthetic)\n\n"
            "## SOURCES\n\naaos12 | AAOS Emergency Care 12th ed.\n\n"
            + item_text)
        ps = model.parse_sources(bare)
        errors, _ = itembank.lint(itembank.load(bare), sources=ps)
        found = [e for e in errors if e.code == "style.unsourced_specific"]
        if len(found) != 1:
            fail("a numeral/unit/dose item without [SRC:] must error once, "
                 "got %r" % errors)
        if "0.5 mg" not in found[0].message:
            fail("the finding must name the specific fact: %r" % found[0].message)
        if "style.unsourced_specific" not in itembank.LINT_CODES:
            fail("style.unsourced_specific must be a published LINT_CODES "
                 "member")
        sourced = os.path.join(tmp, "sourced.md")
        open(sourced, "w", encoding="utf-8").write(
            "# Sourced fixture (synthetic)\n\n"
            "## SOURCES\n\naaos12 | AAOS Emergency Care 12th ed.\n\n"
            + item_text.replace("[OBJECTIVE: emt:airway]\n",
                                "[SRC: aaos12 p. 214]\n[OBJECTIVE: emt:airway]\n"))
        ps2 = model.parse_sources(sourced)
        errors2, _ = itembank.lint(itembank.load(sourced), sources=ps2)
        if any(e.code == "style.unsourced_specific" for e in errors2):
            fail("a resolved [SRC:] must satisfy the structural check: %r"
                 % errors2)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_case_and_prereq_grammar_parses_and_lints():
    """Test 2: [CASE:] groups parse and lint (unknown group id ->
    prov.case_unknown); [PREREQ:] edges lint for unresolvable targets
    (prov.prereq_unknown) and cycles (prov.prereq_cycle) via a small graph
    walk (D-15/D-16, SEED-06, T-032-14)."""
    import model
    clean_bank = (
        "# Edges fixture (synthetic)\n\n## CASES\n\n"
        "case_resp | Respiratory emergencies\n"
        "case_cardio | Cardiac emergencies\n\n"
        "Q1. Which is first?   (difficulty: recall)\n"
        "[CASE: case_resp]\n"
        "A) Airway\nB) Breathing\nCORRECT: A\n"
        "WHY BEST: Airway first.\n\n"
        "Q2. Which is next?   (difficulty: recall)\n"
        "[CASE: case_cardio]\n[PREREQ: case_resp]\n"
        "A) Compressions\nB) Defibrillation\nCORRECT: A\n"
        "WHY BEST: After the airway.\n")
    tmp = tempfile.mkdtemp()
    try:
        good = os.path.join(tmp, "edges_good.md")
        open(good, "w", encoding="utf-8").write(clean_bank)
        pc = model.parse_cases(good)
        if not pc or pc["cases"] != {
                "case_resp": "Respiratory emergencies",
                "case_cardio": "Cardiac emergencies"}:
            fail("## CASES must parse into {id: description}, got %r"
                 % (pc or {}).get("cases"))
        if [d["id"] for d in pc["case_directives"]] != \
                ["case_resp", "case_cardio"]:
            fail("[CASE:] directives must parse in order: %r"
                 % pc["case_directives"])
        if [d["target"] for d in pc["prereq_edges"]] != ["case_resp"]:
            fail("[PREREQ:] edges must parse: %r" % pc["prereq_edges"])
        errors, _ = itembank.lint(itembank.load(good), cases=pc)
        bad = [e for e in errors
               if e.code in ("prov.case_unknown", "prov.prereq_unknown",
                             "prov.prereq_cycle")]
        if bad:
            fail("a valid case/prereq bank must lint clean, got %r" % bad)
        bad_bank = (
            "# Bad edges fixture (synthetic)\n\n## CASES\n\n"
            "case_a | A\ncase_b | B\n\n"
            "Q1. Unknown group.   (difficulty: recall)\n"
            "[CASE: nope]\n"
            "A) Airway\nB) Breathing\nCORRECT: A\nWHY BEST: Airway first.\n\n"
            "Q2. Unknown target.   (difficulty: recall)\n"
            "[CASE: case_a]\n[PREREQ: nope]\n"
            "A) Airway\nB) Breathing\nCORRECT: A\nWHY BEST: Airway first.\n\n"
            "Q3. Cycle half.   (difficulty: recall)\n"
            "[CASE: case_a]\n[PREREQ: case_b]\n"
            "A) Airway\nB) Breathing\nCORRECT: A\nWHY BEST: Airway first.\n\n"
            "Q4. Cycle half.   (difficulty: recall)\n"
            "[CASE: case_b]\n[PREREQ: case_a]\n"
            "A) Airway\nB) Breathing\nCORRECT: A\nWHY BEST: Airway first.\n")
        bad = os.path.join(tmp, "edges_bad.md")
        open(bad, "w", encoding="utf-8").write(bad_bank)
        pc2 = model.parse_cases(bad)
        errors2, _ = itembank.lint(itembank.load(bad), cases=pc2)
        unknown_case = [e for e in errors2 if e.code == "prov.case_unknown"]
        if len(unknown_case) != 1 or "nope" not in unknown_case[0].message \
                or "edges_bad.md" not in unknown_case[0].message:
            fail("prov.case_unknown must name the id and the file: %r"
                 % errors2)
        unknown_prereq = [e for e in errors2
                          if e.code == "prov.prereq_unknown"]
        if len(unknown_prereq) != 1 or "nope" not in \
                unknown_prereq[0].message:
            fail("prov.prereq_unknown must name the id and the file: %r"
                 % errors2)
        cycles = [e for e in errors2 if e.code == "prov.prereq_cycle"]
        if len(cycles) != 1 or "case_b" not in cycles[0].message:
            fail("a case_a->case_b->case_a cycle must error, naming the path: "
                 "%r" % errors2)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_case_prereq_compatibility_floor():
    """Test 3 (D-20): a bank using none of the constructs parses
    byte-identically -- parse_cases returns None for it, lint adds no
    prov.case_*/prov.prereq_* finding, and adding ## CASES + [CASE:] does not
    change parse_bank's output (the grammar is additive)."""
    import model
    plain_text = open(LES_BANK, encoding="utf-8").read()
    if model.parse_cases(LES_BANK) is not None:
        fail("a bank with no CASE/PREREQ constructs must parse as None")
    errors, warnings = itembank.lint(itembank.load(LES_BANK), cases=None)
    if any(e.code.startswith(("prov.case_", "prov.prereq_"))
           for e in errors + warnings):
        fail("a cases-less bank must add no case/prereq finding: %r"
             % (errors + warnings))
    tmp = tempfile.mkdtemp()
    try:
        decorated = plain_text.replace(
            "A short preamble paragraph before the lesson section.",
            "## CASES\n\ndemo_case | A demo case\n\n"
            "A short preamble paragraph before the lesson section.", 1)
        decorated = decorated.replace(
            "[LESSON-REF: The Airway, Step By Step]\n",
            "[CASE: demo_case]\n[LESSON-REF: The Airway, Step By Step]\n", 1)
        prov_bank = os.path.join(tmp, "case_compat.md")
        open(prov_bank, "w", encoding="utf-8").write(decorated)
        plain_qs = itembank.parse_bank(plain_text)
        with_qs = itembank.load(prov_bank)
        if json.dumps(plain_qs, sort_keys=True) != \
                json.dumps(with_qs, sort_keys=True):
            fail("adding ## CASES/[CASE:] must not change the parse (D-20)")
        pc = model.parse_cases(prov_bank)
        if not pc or "demo_case" not in pc["cases"]:
            fail("the decorated copy must be read by parse_cases")
        errors2, _ = itembank.lint(with_qs, cases=pc)
        if any(e.code.startswith("prov.case_") for e in errors2):
            fail("a resolved [CASE:] must lint clean: %r" % errors2)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_d19_two_file_layout_prose_file_distinct_from_items_file():
    """D-19 (R5): in the two-file layout, the prose file an item-bearing bank
    points at ([LESSON-SRC:]) resolves to a path distinct from the bank file
    -- the separation the item-write/prose-write non-contention depends on
    (T-032-17)."""
    with tempfile.TemporaryDirectory() as td:
        prose = os.path.join(td, "prose.md")
        bank = os.path.join(td, "bank.md")
        open(prose, "w", encoding="utf-8").write(
            "# Shared lesson\n\n## LESSON\n\n### Section One\n\nTeaching text.")
        open(bank, "w", encoding="utf-8").write(
            "# Bank\n\n[LESSON-SRC: prose.md]\n\n"
            + clean_mc("Which is the keyed answer?"))
        L = itembank.parse_lesson(bank)
        if L is None:
            fail("D-19: the two-file bank must resolve an external lesson")
        if os.path.abspath(L["source"]) == os.path.abspath(bank):
            fail("D-19: the prose source must be the [LESSON-SRC:] file, not "
                 "the bank file")
        if os.path.abspath(L["source"]) != os.path.abspath(prose):
            fail("D-19: the prose source must resolve to the prose file: %r"
                 % L["source"])
        if not os.path.isfile(bank):
            fail("the bank file must stay intact")


# ---- plan 03.1-01 Task 3: the one callout container -----------------------
# One blockquote-marker branch in _render_blocks(); KEY/EXAMPLE/NOTE/
# WARNING/CHECK render as kinds of the container, [!CHECK: <id>] renders the
# inert reserved slot, and any unknown kind degrades to the pre-change
# paragraph output byte-for-byte (D-18, 03.1-UI-SPEC §9.2-§9.4, §15).


def test_callout_kinds_render_locked_labels():
    """Test 1: the locked kinds render their exact labels and the [!CHECK:]
    slot carries the exact inert copy with no form, no key, and no scoring
    path (03.1-UI-SPEC §9.2-§9.4, §15)."""
    h = lesson.render_markdown(
        "> [!KEY] The key point body.\n\n"
        "> [!EXAMPLE] An example body.\n\n"
        "> [!NOTE] A note body.\n\n"
        "> [!WARNING] A warning body.\n")
    for want in ('class="callout callout-key"', "Key point",
                 'class="callout callout-example"', "Example",
                 'class="callout callout-note"', "Note",
                 'class="callout callout-warning"', "Warning"):
        if want not in h:
            fail("callout kind missing %r: %r" % (want, h))
    h2 = lesson.render_markdown(
        "> [!CHECK: airway-opa-01] Reserved slot.\n")
    if ("This check is available when you are reading with a session."
            not in h2):
        fail("the [!CHECK:] slot must render the exact inert copy "
             "(03.1-UI-SPEC §15): %r" % h2)
    for banned in ("airway-opa-01", "<form", "score_response", "scoring"):
        if banned in h2:
            fail("the [!CHECK:] slot must carry no key, form, or scoring "
                 "path (D-18): %r leaked in %r" % (banned, h2))


def test_callout_unknown_kind_degrades_to_paragraph():
    """Test 2: an unknown [!...] kind falls through to the paragraph branch
    and renders byte-identically to the pre-change renderer (explicit
    unknown-kind degradation, D-18)."""
    h = lesson.render_markdown("> [!NOPE] Just prose.\n")
    if h != "<p>&gt; [!NOPE] Just prose.</p>":
        fail("unknown callout kind must degrade to the pre-change paragraph "
             "render: %r" % h)


def test_callout_body_and_label_escaped():
    """Test 3: every rendered callout body is HTML-escaped -- a body carrying
    <script> or &lt; renders as escaped text with no executable tag
    (T-031-01, 03.1-UI-SPEC §11)."""
    h = lesson.render_markdown(
        "> [!KEY] <script>alert(1)</script> & <b>x</b>\n")
    if "<script>" in h or "<b>" in h:
        fail("callout body leaked executable markup: %r" % h)
    if "&lt;script&gt;" not in h or "&lt;b&gt;" not in h:
        fail("callout body must render escaped text: %r" % h)


def test_existing_block_branches_byte_identical_without_callouts():
    """Test 4: the existing fenced-code, heading, list, and table branches
    produce byte-identical output to the pre-change golden for prose with
    none of the new constructs (03.1-UI-SPEC §12.4)."""
    src = ("### H\n\nprose **bold**\n\n- a\n- b\n\n"
           "| x | y |\n| --- | --- |\n| 1 | 2 |\n\n"
           "```py\nx = 1\n```\n")
    golden = ('<section id="h"><h2>H</h2><p>prose <strong>bold</strong></p>'
              "\n<ul><li>a</li><li>b</li></ul>\n"
              '<div class="scroll lesson-table-scroll" tabindex="0" '
              'role="region" aria-label="Lesson table"><table><thead><tr>'
              '<th scope="col">x</th><th scope="col">y</th>'
              "</tr></thead><tbody><tr><td>1</td><td>2</td></tr></tbody>"
              "</table></div>\n"
              '<div class="scroll" data-code-block="1" data-lang="py">'
              '<span class="lang">py</span>'
              '<pre><code class="language-py">x = 1</code></pre>'
              '<p class="run-unavailable">Run this example in the local app. '
              "The source remains available here.</p></div>"
              "</section>")
    h = lesson.render_markdown(src)
    if h != golden:
        fail("existing block branches drifted from the pre-change golden: "
             "%r" % h)


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
    card = '<div class="card"'
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
    the render function produces, which is what the daemon route sends.
    Both surfaces resolve the subject profile through the same selector
    (plan 09-05), so the test resolves it identically before rendering."""
    out = os.path.join(tempfile.mkdtemp(), "c1.html")
    res = run_lesson([LES_BANK, "--out", out])
    if res.returncode != 0:
        fail("lesson failed: " + res.stdout + res.stderr)
    qs = itembank.load(LES_BANK)
    profile = subjects.select_profile(
        qs, subjects.load_registry(os.path.dirname(LES_BANK)))
    page = lesson.lesson_page(LES_BANK, qs, itembank.parse_lesson(LES_BANK),
                              profile=profile)
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
                 'class="warn"',
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
    # The shared style block legitimately carries the --warn token for other
    # surfaces; the contract is that the plain empty state renders no warn
    # note element and substitutes no .warn rule (plan 03.1-01 migrated the
    # lesson page onto SHARED_CSS; the style block is excluded from the §12
    # byte-identity floor).
    if 'class="warn"' in pg or ".warn{" in pg:
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
    types_at = s.find("THE EIGHT ITEM TYPES")
    if tag_at < 0 or types_at < 0 or tag_at > types_at:
        fail("LESSON-REF must be listed in the shared-fields block")


def test_spec_names_every_lesson_lint_code():
    """The spec names all six lesson codes and each is a published LINT_CODES
    member -- the code list is derived, never restated, so a rename fails here
    instead of leaving the contract describing a code that no longer exists
    (T-3-08). The two Phase 6.2 gate codes (lesson.invalid_gate,
    lesson.check_ref_unknown) are documented in the additive SPEC_03_1
    section; the four Phase 3 codes live in the base SPEC. The error/warning
    split and each trigger are stated too."""
    s = itembank.SPEC + "\n" + SPEC_03_1
    lesson_codes = [c for c in itembank.LINT_CODES
                    if c.startswith("lesson.") or c == "item.lesson_ref_unknown"]
    if len(lesson_codes) != 6:
        fail("expected exactly 6 lesson lint codes, got %d: %r"
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
    for keep in ("THE EIGHT ITEM TYPES", "DISTRACTOR ANALYSIS",
                 "THE RULE THAT SURVIVES EVERY TYPE", "[ID:]", "[HASH:]"):
        if keep not in s:
            fail("existing SPEC substring lost: %r" % keep)


# ---- plan 03.1-02: TERMS parse, refs, and terms/key lint -------------------

def terms_bank(tmp=None, terms_text=None, lesson_body="", item=None):
    """A real bank file carrying an optional `## TERMS` block and optional
    lesson body, so parse_terms and the terms lint pass run over the same
    on-disk shape every real caller uses."""
    tmp = tmp or tempfile.mkdtemp()
    bank = os.path.join(tmp, "terms_bank.md")
    parts = ["# Terms bank\n"]
    if terms_text is not None:
        parts.append("## TERMS\n\n%s\n" % terms_text.strip())
    if lesson_body:
        parts.append("## LESSON\n\n%s\n" % lesson_body.strip())
    parts.append((item or clean_mc("Which is one?")).strip() + "\n")
    open(bank, "w", encoding="utf-8").write("\n".join(parts))
    return bank


def test_parse_terms_basic():
    """A `## TERMS` block of pipe rows parses into slug-keyed records with
    canonical/aliases/def plus recognised meta (xlat), the reserved zh= is
    dropped from the record, and [[term]] refs are collected from the lesson
    body with their lesson_slug() values."""
    bank = terms_bank(
        terms_text=("Airway | The passage from mouth to lungs | Air passage | zh=Zhōngwén\n"
                    "OPA | A rigid curved adjunct that holds the tongue off the pharynx | "
                    "Oropharyngeal airway | xlat=气道\n"),
        lesson_body="### Intro\n\nSee [[Airway]] and [[OPA]].",
    )
    t = itembank.parse_terms(bank)
    if t is None:
        fail("parse_terms returned None for a bank with ## TERMS")
    if sorted(t["terms"]) != ["airway", "opa"]:
        fail("term slugs wrong: %r" % sorted(t["terms"]))
    aw = t["terms"]["airway"]
    if aw["canonical"] != "Airway" or aw["def"] != "The passage from mouth to lungs":
        fail("airway record wrong: %r" % aw)
    if aw["aliases"] != ["Air passage"]:
        fail("aliases wrong: %r" % aw["aliases"])
    opa = t["terms"]["opa"]
    if opa["aliases"] != ["Oropharyngeal airway"] or opa["xlat"] != "气道":
        fail("opa record wrong: %r" % opa)
    if any("zh" in str(v).lower() for v in aw.values()):
        fail("reserved zh= must be dropped from the term record: %r" % aw)
    if [r["text"] for r in t["refs"]] != ["Airway", "OPA"]:
        fail("[[term]] refs wrong: %r" % t["refs"])
    if [r["slug"] for r in t["refs"]] != ["airway", "opa"]:
        fail("ref slugs must use lesson_slug: %r" % t["refs"])
    if t["empty"] is not False:
        fail("a two-row TERMS block must not be marked empty")


def test_parse_terms_absent_and_question_parse_unchanged():
    """A bank without `## TERMS` returns None, and adding a TERMS block does
    not change load()/parse_bank() output (D-23 additive floor)."""
    if itembank.parse_terms(SMP_BANK) is not None:
        fail("sample_bank has no ## TERMS section; parse_terms should be None")
    tmp = tempfile.mkdtemp()
    base = clean_mc("Which is one?")
    p_plain = os.path.join(tmp, "plain.md")
    open(p_plain, "w", encoding="utf-8").write(base)
    p_terms = os.path.join(tmp, "terms.md")
    open(p_terms, "w", encoding="utf-8").write(
        "# Tagged\n\n## TERMS\n\nAirway | The passage\n\n" + base)
    plain_qs = itembank.parse_bank(open(p_plain, encoding="utf-8").read())
    terms_qs = itembank.parse_bank(open(p_terms, encoding="utf-8").read())
    if plain_qs != terms_qs:
        fail("a ## TERMS block must not change parse_bank output")
    if itembank.load(p_terms) != itembank.load(p_plain):
        fail("load() must be identical with or without a TERMS block")


def test_terms_meta_captured_and_marked_ignored():
    """The reserved zh= meta and an unknown meta key are captured and marked
    ignored, and neither appears in any parsed output field the renderer
    consumes (D-24, LESSON-16)."""
    bank = terms_bank(
        terms_text="Airway | The passage | zh=Zhōngwén | xlat=气道 | mystery=1")
    t = itembank.parse_terms(bank)
    rec = t["terms"]["airway"]
    for field in ("canonical", "aliases", "def", "xlat", "see"):
        if "zh" in str(rec[field]).lower() or "mystery" in str(rec[field]).lower():
            fail("ignored meta must not leak into record fields: %r" % rec)
    if rec["xlat"] != "气道":
        fail("recognised xlat= meta must populate the record: %r" % rec)
    keys = sorted({i["key"] for i in t["ignored"]})
    if keys != ["mystery", "zh"]:
        fail("ignored meta keys wrong: %r" % keys)
    if any(i["row"] != "Airway" for i in t["ignored"]):
        fail("ignored meta must record its owning row: %r" % t["ignored"])


def test_terms_lint_unknown_ref_and_no_block():
    """A [[term]] with no matching ## TERMS entry is a BANK error naming the
    ref; a bank with no TERMS block at all makes every ref unknown."""
    tmp = tempfile.mkdtemp()
    bank = terms_bank(tmp, terms_text="Airway | The passage",
                      lesson_body="See [[Missing]].")
    qs = itembank.load(bank)
    errors, warnings = itembank.lint(qs, lesson=itembank.parse_lesson(bank),
                                     terms=itembank.parse_terms(bank))
    assert_codes_declared(errors + warnings)
    unknown = [e for e in errors if e.code == "terms.unknown_ref"]
    if len(unknown) != 1 or unknown[0].item != "BANK":
        fail("unknown ref must be a single BANK error: %r" % errors)
    if "Missing" not in unknown[0].message:
        fail("unknown-ref message must name the ref: %r" % unknown[0].message)
    if unknown[0].field != "refs":
        fail("unknown-ref field must be 'refs', got %r" % unknown[0].field)

    bank2 = terms_bank(tmp, terms_text=None, lesson_body="See [[Airway]].")
    qs2 = itembank.load(bank2)
    errors2, _ = itembank.lint(qs2, lesson=itembank.parse_lesson(bank2),
                               terms=itembank.parse_terms(bank2))
    unknown2 = [e for e in errors2 if e.code == "terms.unknown_ref"]
    if len(unknown2) != 1:
        fail("a bank with no TERMS block must flag every ref unknown: %r"
             % errors2)


def test_terms_lint_empty_block_and_duplicate_slug():
    """A zero-entry ## TERMS block is a warning and still renders nothing; two
    term keys or aliases that slug-collide are an error."""
    tmp = tempfile.mkdtemp()
    bank = terms_bank(tmp, terms_text="", lesson_body="See [[Airway]].")
    qs = itembank.load(bank)
    errors, warnings = itembank.lint(qs, lesson=itembank.parse_lesson(bank),
                                     terms=itembank.parse_terms(bank))
    empty = [w for w in warnings if w.code == "terms.empty_block"]
    if len(empty) != 1 or empty[0].item != "BANK":
        fail("zero-entry TERMS block must warn exactly once: %r" % warnings)
    if [w for w in warnings
            if w.code.startswith(("terms.", "key."))
            and w.code != "terms.empty_block"]:
        fail("empty-block bank must produce no other terms/key warnings: %r"
             % warnings)

    bank2 = terms_bank(tmp, terms_text="Air-way | One\nAir Way | Two")
    qs2 = itembank.load(bank2)
    errors2, _ = itembank.lint(qs2, lesson=itembank.parse_lesson(bank2),
                               terms=itembank.parse_terms(bank2))
    dup = [e for e in errors2 if e.code == "terms.duplicate_slug"]
    if len(dup) != 1 or dup[0].item != "BANK":
        fail("slug-colliding terms must be a BANK error: %r" % errors2)
    if "air-way" not in dup[0].message:
        fail("duplicate-slug message must name the colliding slug: %r"
             % dup[0].message)

    bank3 = terms_bank(tmp, terms_text="OPA | One | Oropharyngeal airway\n"
                                       "Opa | Two")
    qs3 = itembank.load(bank3)
    errors3, _ = itembank.lint(qs3, lesson=itembank.parse_lesson(bank3),
                               terms=itembank.parse_terms(bank3))
    if len([e for e in errors3 if e.code == "terms.duplicate_slug"]) != 1:
        fail("an alias slug-colliding with a term must be an error: %r"
             % errors3)


def test_terms_lint_key_in_rationale_and_duplicate_id():
    """A [!KEY] marker inside an item rationale is an error tagged by that
    item's Qn number (D-05); duplicate [!KEY] ids in the lesson body are a
    BANK error."""
    tmp = tempfile.mkdtemp()
    item = clean_mc("Which is one?").replace(
        "WHY BEST: One is the keyed answer.",
        "WHY BEST: One is the keyed answer. [!KEY: opa-1]")
    bank = terms_bank(tmp, terms_text="Airway | The passage", item=item)
    qs = itembank.load(bank)
    errors, _ = itembank.lint(qs, lesson=itembank.parse_lesson(bank),
                              terms=itembank.parse_terms(bank))
    key = [e for e in errors if e.code == "key.in_rationale"]
    if len(key) != 1 or key[0].item != "Q1" or key[0].field != "why":
        fail("key.in_rationale must be tagged by item and field: %r" % key)

    bank2 = terms_bank(
        tmp, terms_text="Airway | The passage",
        lesson_body="> [!KEY: opa-1] First card\n\n> [!KEY: opa-1] Second card")
    qs2 = itembank.load(bank2)
    errors2, _ = itembank.lint(qs2, lesson=itembank.parse_lesson(bank2),
                               terms=itembank.parse_terms(bank2))
    dup_id = [e for e in errors2 if e.code == "key.duplicate_id"]
    if len(dup_id) != 1 or dup_id[0].item != "BANK":
        fail("duplicate [!KEY] ids must be a BANK error: %r" % errors2)
    if "opa-1" not in dup_id[0].message:
        fail("duplicate-id message must name the id: %r" % dup_id[0].message)


def test_terms_lint_sentinel_exported_and_default_unchanged():
    """TERMS_UNCHECKED is the exported sentinel default; lint(qs) without it
    emits no terms/key finding (the additive pattern LESSON_UNCHECKED set)."""
    if not hasattr(itembank, "TERMS_UNCHECKED"):
        fail("TERMS_UNCHECKED sentinel is not exported by itembank")
    if "TERMS_UNCHECKED" not in itembank.__all__:
        fail("TERMS_UNCHECKED must be a member of itembank.__all__")
    qs = itembank.load(LES_BANK)
    errors, warnings = itembank.lint(qs)
    for f in errors + warnings:
        if f.code.startswith(("terms.", "key.")):
            fail("default lint must not emit terms/key findings: %r" % f)


def test_glossable_gate():
    """The runtime glossable() gate refuses a term whose definition would
    leak keyed answer material -- the correct option label, a short item's
    model answer, or the canonical key -- and admits an unrelated
    definition; it is pure and deterministic (D-20, UI-SPEC §8.4)."""
    mc = clean_mc("Which one is the key?").replace("CORRECT: A", "CORRECT: B")
    short = ("Q2. State the opening manoeuvre.   (difficulty: recall)\n"
             "[TYPE: short]\n"
             "MODEL: The head-tilt lifts the tongue.\n\n"
             "RUBRIC:\n- Names the manoeuvre.\n- States what it does.\n\n"
             "CONFIDENCE: high\n")
    qs = itembank.parse_bank(mc + short)
    if len(qs) != 2:
        fail("glossable fixture bank must parse to 2 items, got %d" % len(qs))

    leaky_option = {"canonical": "Runner-up", "aliases": [], "def": (
        "Two is the runner-up and would win if the stem changed.")}
    if itembank.glossable(qs, leaky_option) is not False:
        fail("a def containing the correct option label must be suppressed")
    leaky_model = {"canonical": "Manoeuvre", "aliases": [], "def": (
        "The head-tilt lifts the tongue. It opens the airway.")}
    if itembank.glossable(qs, leaky_model) is not False:
        fail("a def containing a short item's model answer must be suppressed")
    leaky_key = {"canonical": "Keyed", "aliases": [], "def": (
        "The keyed letter is B, placed with the stem.")}
    if itembank.glossable(qs, leaky_key) is not False:
        fail("a def containing the canonical key must be suppressed")
    clean = {"canonical": "Airway", "aliases": [], "def": (
        "The passage from mouth to lungs.")}
    if itembank.glossable(qs, clean) is not True:
        fail("an unrelated definition must pass the gate")
    if itembank.glossable(qs, clean) != itembank.glossable(qs, clean):
        fail("glossable must be deterministic across calls")
    if itembank.glossable(qs, {"canonical": "Empty", "aliases": [], "def": ""}) \
            is not True:
        fail("an empty definition must pass the gate (nothing to leak)")


# ---- plan 03.1-02 Task 3: glossary appendix, inline gloss, /gloss route ----

def gloss_bank(tmp, terms_text, lesson_body, item=None, settings_text=None):
    """A real bank with optional `## TERMS` and `## LESSON` plus an optional
    bank-adjacent itembank.json (reader settings), laid out under `tmp`."""
    bank = os.path.join(tmp, "gloss_bank.md")
    if settings_text:
        open(os.path.join(tmp, "itembank.json"), "w", encoding="utf-8").write(
            settings_text)
    parts = ["# Gloss bank\n"]
    if terms_text:
        parts.append("## TERMS\n\n%s\n" % terms_text.strip())
    if lesson_body:
        parts.append("## LESSON\n\n%s\n" % lesson_body.strip())
    parts.append((item or clean_mc("Which is one?").replace(
        "CORRECT: A", "CORRECT: C")).strip() + "\n")
    open(bank, "w", encoding="utf-8").write("\n".join(parts))
    return bank


def test_glossary_appendix_renders_after_lesson():
    """The glossary appendix renders as a `<dl>` in `<section
    id="glossary">` under an `<h2>Glossary</h2>`, with `<dt
    id="term-<slug>">` anchors matching the trigger slugs, after the last
    lesson section; a bank with no `## TERMS` renders no glossary at all
    (UI-SPEC §9.1)."""
    tmp = tempfile.mkdtemp()
    bank = gloss_bank(
        tmp,
        terms_text=("Airway | The passage from mouth to lungs.\n"
                    "OPA | The rigid tube holds the tongue off the pharynx.\n"),
        lesson_body="### Airway Basics\n\nSee [[Airway]] and [[OPA]].")
    pg = lesson.lesson_page(bank, itembank.load(bank),
                            itembank.parse_lesson(bank))
    if '<section id="glossary"><h2>Glossary</h2>' not in pg:
        fail("glossary appendix section/heading missing")
    if '<dt id="term-airway">' not in pg or '<dt id="term-opa">' not in pg:
        fail("glossary dt anchors missing")
    gloss_at = pg.find('<section id="glossary">')
    lesson_section_at = pg.rfind("<section id=", 0, gloss_at)
    if not (0 < lesson_section_at < gloss_at):
        fail("glossary must render after the last lesson section "
             "(%d vs %d)" % (lesson_section_at, gloss_at))

    plain = lesson.lesson_page(SMP_BANK, itembank.load(SMP_BANK),
                               itembank.parse_lesson(SMP_BANK))
    if 'id="glossary"' in plain or "<h2>Glossary</h2>" in plain:
        fail("a bank with no ## TERMS must render no glossary section")


def test_gloss_triggers_panels_and_no_leak():
    """[[term]] renders a Popover-API trigger with the dotted underline and a
    matching `[popover]` panel; a term whose definition would leak a keyed
    answer renders as bare text with no element, class, data-* or held
    per-term trace, and the generic held line appears at most once (D-20,
    UI-SPEC §8.1/§8.4)."""
    tmp = tempfile.mkdtemp()
    bank = gloss_bank(
        tmp,
        terms_text=("Airway | The passage from mouth to lungs.\n"
                    "One | Three is the keyed answer.\n"),
        lesson_body="### Basics\n\nSee [[Airway]] and [[One]].")
    pg = lesson.lesson_page(bank, itembank.load(bank),
                            itembank.parse_lesson(bank))
    if 'popovertarget="gloss-airway"' not in pg:
        fail("glossable term must render a popover trigger")
    if 'aria-details="gloss-airway"' not in pg:
        fail("trigger must carry aria-details")
    if '<div id="gloss-airway" class="gloss" popover>' not in pg:
        fail("glossable term must ship its popover panel")
    if "text-decoration:underline dotted" not in pg:
        fail("trigger must carry the dotted-underline treatment")
    if 'popovertarget="gloss-one"' in pg:
        fail("suppressed term must have no trigger")
    if 'aria-details="gloss-one"' in pg:
        fail("suppressed term must leave no accessible-name trace")
    if "and One." not in pg:
        fail("suppressed term must render as bare text, got %r" %
             pg[pg.find("See"):pg.find("See") + 60])
    if '<dt id="term-one">' in pg:
        fail("suppressed term must be absent from the glossary appendix")
    if pg.count("Some definitions are held until you answer.") != 1:
        fail("the generic held line must appear exactly once")
    if "Definitions are unavailable right now." not in pg:
        fail("the vendored in-sitting fetch hook must carry the unavailable copy")


def test_gloss_marks_and_print_modes():
    """gloss_marks all|first-use|none and print_gloss appendix|inline alter
    the rendered output exactly as the spec tables describe; the inline
    print reflow ships as a print-media block (UI-SPEC §8.2, §10.1, §14)."""
    import json
    tmp = tempfile.mkdtemp()
    body = ("### Basics\n\nFirst [[Airway]].\n\nSecond [[Airway]].")
    terms = "Airway | The passage from mouth to lungs.\n"

    bank = gloss_bank(tmp, terms, body)
    pg = lesson.lesson_page(bank, itembank.load(bank),
                            itembank.parse_lesson(bank))
    if pg.count('<button type="button" class="term"') != 2:
        fail("gloss_marks all must mark every occurrence, got %d"
             % pg.count('<button type="button" class="term"'))

    bank = gloss_bank(tmp, terms, body,
                      settings_text=json.dumps({"reader": {"gloss_marks":
                                                           "first-use"}}))
    pg = lesson.lesson_page(bank, itembank.load(bank),
                            itembank.parse_lesson(bank))
    if pg.count('<button type="button" class="term"') != 1:
        fail("gloss_marks first-use must mark one occurrence per section")

    bank = gloss_bank(tmp, terms, body,
                      settings_text=json.dumps({"reader": {"gloss_marks":
                                                           "none"}}))
    pg = lesson.lesson_page(bank, itembank.load(bank),
                            itembank.parse_lesson(bank))
    if '<button type="button" class="term"' in pg:
        fail("gloss_marks none must leave every term as plain prose")
    if '<section id="glossary">' not in pg:
        fail("gloss_marks none must keep the glossary appendix as the path")

    bank = gloss_bank(tmp, terms, body,
                      settings_text=json.dumps({"reader": {"print_gloss":
                                                           "inline"}}))
    pg = lesson.lesson_page(bank, itembank.load(bank),
                            itembank.parse_lesson(bank))
    if "display:block!important" not in pg:
        fail("print_gloss inline must reflow popovers as printed notes")


def test_gloss_placement_hover_and_key_link_contract():
    """Phase 13.5-05: placement is complete, hover is optional, and lookup
    links to a matching key card without acquiring a scheduler control."""
    tmp = tempfile.mkdtemp()
    body = ("### Basics\n\nRead [[Airway]].\n\n"
            "> [!KEY] Airway point\n"
            "> [ID: 1111111111111111]\n"
            "> The [[Airway]] must stay open.\n")
    bank = gloss_bank(tmp, "Airway | The passage from mouth to lungs.\n", body)
    pg = lesson.lesson_page(bank, itembank.load(bank),
                            itembank.parse_lesson(bank))
    for needle in ("position-area:block-end span-inline-end",
                   "position-try-fallbacks:flip-block,flip-inline",
                   "(max-width:767px) and (pointer:coarse)",
                   '#gloss-airway{--gloss-anchor:--anchor-airway}',
                   'href="#key-1111111111111111">Also a key point</a>',
                   'dataset.glossOpen = "hover"', "Back to the text"):
        if needle not in pg:
            fail("phase 13.5 gloss contract missing %r" % needle)
    panel = pg[pg.index('<div id="gloss-airway"'):
               pg.index('</div>', pg.index('<div id="gloss-airway"'))]
    if "Add to review" in panel or "<form" in panel:
        fail("the transient gloss lookup must carry no scheduler control")

    off = gloss_bank(
        tmp, "Airway | The passage from mouth to lungs.\n", body,
        settings_text=json.dumps({"reader": {"gloss_hover": "off"}}))
    off_pg = lesson.lesson_page(off, itembank.load(off),
                                itembank.parse_lesson(off))
    if 'dataset.glossOpen = "hover"' in off_pg:
        fail("gloss_hover off must omit the hover-intent script")

    original = lesson.lesson_slug
    try:
        lesson.lesson_slug = lambda _text: "bad]slug"
        if lesson._gloss_trigger_html("unsafe", "bad]slug") != "unsafe":
            fail("an unsafe CSS slug must degrade to plain prose")
        if lesson._gloss_anchor_css({"bad]slug"}):
            fail("an unsafe CSS slug must emit no anchor rule")
    finally:
        lesson.lesson_slug = original


def test_scroll_contract_and_reader_nav_modes():
    """Phase 13.5-06: scroll clearance is shared and auto nav starts at four sections."""
    tmp = tempfile.mkdtemp()
    three = "\n\n".join("### S%d\n\nBody." % n for n in range(1, 4))
    four = "\n\n".join("### S%d\n\nBody." % n for n in range(1, 5))
    bank3 = gloss_bank(tmp, "Airway | Definition.\n", three)
    page3 = lesson.lesson_page(bank3, itembank.load(bank3), itembank.parse_lesson(bank3))
    if 'class="reader-nav' in page3:
        fail("reader_nav auto must not render for three sections")
    bank4 = gloss_bank(tmp, "Airway | Definition.\n", four)
    page4 = lesson.lesson_page(bank4, itembank.load(bank4), itembank.parse_lesson(bank4))
    if page4.count('class="reader-nav nav-rail"') != 1:
        fail("reader_nav auto must render one wide-rail-capable nav at four sections")
    if page4.count('class="nav-n"') != 4 or "min-height:44px" not in page4:
        fail("reader nav must number all sections and expose 44px link rows")
    if "scroll-margin-top:calc(var(--sticky-h,0px) + var(--space-2))" not in page4:
        fail("reader targets must carry the shared sticky clearance")

    quiz_source = inspect.getsource(lesson).replace(" ", "")
    if "section[id],#glossarydt" not in quiz_source:
        fail("reader scroll targets must include sections and glossary entries")


def test_gloss_example_layout_and_reader_nav():
    """example_layout parallel adds the layout class to [!EXAMPLE]
    callouts; reader_nav column renders the sections nav (UI-SPEC §7.3,
    §9.3, §14)."""
    import json
    tmp = tempfile.mkdtemp()
    body = ("### Basics\n\n> [!EXAMPLE] One worked example.\n")
    bank = gloss_bank(tmp, "Airway | The passage from mouth to lungs.\n",
                      body)
    pg = lesson.lesson_page(bank, itembank.load(bank),
                            itembank.parse_lesson(bank))
    if 'class="callout callout-example example-parallel"' in pg:
        fail("default example_layout must be stacked (no parallel class)")

    bank = gloss_bank(
        tmp, "Airway | The passage from mouth to lungs.\n", body,
        settings_text=json.dumps({"reader": {"example_layout": "parallel"}}))
    pg = lesson.lesson_page(bank, itembank.load(bank),
                            itembank.parse_lesson(bank))
    if 'class="callout callout-example example-parallel"' not in pg:
        fail("example_layout parallel must add the layout class")

    bank = gloss_bank(
        tmp, "Airway | The passage from mouth to lungs.\n",
        "### Basics\n\nProse.\n\n### Advanced\n\nMore.\n",
        settings_text=json.dumps({"reader": {"reader_nav": "column"}}))
    pg = lesson.lesson_page(bank, itembank.load(bank),
                            itembank.parse_lesson(bank))
    if 'class="reader-nav"' not in pg or "Sections in this lesson" not in pg:
        fail("reader_nav column must render the sections nav")
    if 'href="#basics"' not in pg or 'href="#advanced"' not in pg:
        fail("reader nav must link every heading by slug")


def test_gloss_route_and_cli_twin():
    """GET /gloss/<stem>/<slug> serves a glossable definition and records a
    term_lookup event; unknown and suppressed slugs 404 with no event; the
    CLI twin `itembank gloss <bank> <term>` reaches the same resolution
    (SURF-04)."""
    tmp = tempfile.mkdtemp()
    bank = gloss_bank(
        tmp,
        terms_text=("Airway | The passage from mouth to lungs.\n"
                    "One | Three is the keyed answer.\n"),
        lesson_body="### Basics\n\nSee [[Airway]] and [[One]].")
    proc, url, _ = start_daemon(tmp)
    try:
        status, body = get(url + "/gloss/gloss_bank/airway")
        if status != 200:
            fail("GET /gloss/<stem>/<slug> returned %d" % status)
        if "The passage from mouth to lungs." not in body:
            fail("gloss route body missing the definition")
        if "Back to the question" not in body:
            fail("gloss route body missing the back link")

        for slug in ("nope", "one"):
            try:
                get(url + "/gloss/gloss_bank/" + slug)
                fail("GET /gloss for %r must 404" % slug)
            except urllib.error.HTTPError as exc:
                if exc.code != 404:
                    fail("GET /gloss for %r returned %d, not 404"
                         % (slug, exc.code))
    finally:
        proc.kill()
        proc.wait()

    log = itembank.log_path(tmp)
    lookups = [e for e in itembank.events(log)
               if e["event_type"] == "term_lookup"]
    if len(lookups) != 1 or lookups[0]["term_slug"] != "airway":
        fail("the route must record exactly one term_lookup for the served "
             "slug, got %r" % lookups)
    if lookups[0]["source"] != "session":
        fail("the route must record source='session': %r" % lookups[0])

    res = subprocess.run(
        [sys.executable, os.path.join(ROOT, "itembank.py"), "gloss", bank,
         "Airway"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=30)
    if res.returncode != 0 or "The passage from mouth to lungs." not in res.stdout:
        fail("itembank gloss must print the definition, got %r" % res.stdout)
    res2 = subprocess.run(
        [sys.executable, os.path.join(ROOT, "itembank.py"), "gloss", bank,
         "nope"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=30)
    if res2.returncode == 0:
        fail("itembank gloss on an unknown term must exit non-zero")
    res3 = subprocess.run(
        [sys.executable, os.path.join(ROOT, "itembank.py"), "gloss", bank,
         "One"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=30)
    if res3.returncode == 0:
        fail("itembank gloss on a suppressed term must exit non-zero")


def test_reader_settings_registered_in_schema():
    """The four reader settings are registered in schemas/settings.schema.json
    with their locked defaults and this phase's owner stamp (UI-SPEC §14)."""
    schema = json.load(open(os.path.join(ROOT, "schemas",
                                         "settings.schema.json"),
                            encoding="utf-8"))
    reader = schema.get("properties", {}).get("reader")
    if not reader or reader.get("type") != "object":
        fail("settings schema missing the reader group")
    expected = {
        "reader_nav": "auto", "example_layout": "stacked",
        "print_gloss": "appendix", "gloss_marks": "all",
        "gloss_hover": "on",
    }
    owners = {"reader_nav": 13.5, "gloss_hover": 13.5}
    props = reader.get("properties", {})
    for key, default in expected.items():
        sub = props.get(key)
        if not sub or sub.get("default") != default:
            fail("reader setting %r missing or default %r != %r"
                 % (key, sub.get("default") if sub else None, default))
        if sub.get("x-itembank-phase") != owners.get(key, 3.1):
            fail("reader setting %r carries the wrong phase owner" % key)
    if "reader" not in schema.get("required", []):
        fail("reader must be a top-level required settings key")


# ---- plan 03.1-03 Task 1: [!KEY] blocks, shared id minting, key lint ------

def key_bank(tmp, lesson_body, item=None, intro=""):
    """A bank whose lesson body carries `> [!KEY]` callouts plus one clean
    item, laid out under `tmp`."""
    bank = os.path.join(tmp, "key_bank.md")
    parts = ["# Key bank\n"]
    if intro:
        parts.append(intro.strip() + "\n")
    parts.append("## LESSON\n\n%s\n" % lesson_body.strip())
    parts.append((item or clean_mc("Which is one?")).strip() + "\n")
    open(bank, "w", encoding="utf-8").write("\n".join(parts))
    return bank


def test_parse_key_blocks():
    """`> [!KEY]` callouts in the lesson parse into {id, hash, title, body,
    cloze, section_slug}; a lesson with none returns an empty list; the
    question parse is untouched."""
    tmp = tempfile.mkdtemp()
    body = ("### Airway\n\n"
            "> [!KEY] OPA indications\n"
            "> [ID: 1111111111111111]\n"
            "> [HASH: sha256:abcdef]\n"
            "> The OPA is indicated when the tongue obstructs.\n\n"
            "> [!KEY]\n"
            "> Memorize {{cloze}} inline.\n\n"
            "### More\n\nProse.\n")
    bank = key_bank(tmp, body)
    keys = itembank.parse_key_blocks(bank)
    if len(keys) != 2:
        fail("expected 2 key blocks, got %r" % keys)
    first = keys[0]
    if first["id"] != "1111111111111111" or first["hash"] != "sha256:abcdef":
        fail("key id/hash directives wrong: %r" % first)
    if first["title"] != "OPA indications":
        fail("key title wrong: %r" % first)
    if "tongue obstructs" not in first["body"]:
        fail("key body wrong: %r" % first)
    if first["cloze"] is not False or first["section_slug"] != "airway":
        fail("first key cloze/section wrong: %r" % first)
    second = keys[1]
    if second["cloze"] is not True or second["title"] != "":
        fail("second key cloze/title wrong: %r" % second)
    if "Memorize" not in second["body"]:
        fail("second key body wrong: %r" % second)

    plain = key_bank(tmp, "### Airway\n\nJust prose.\n")
    if itembank.parse_key_blocks(plain) != []:
        fail("a lesson with no key blocks must parse to []")


def test_key_id_minting_shared_namespace():
    """`itembank id-assign` mints [!KEY] ids through the same taken set as
    item ids: a key never collides with an existing item id, the minted
    [ID:]/[HASH:] land in the bank text, a second run is a no-op, and no
    separate key-id function exists (research Pitfall 5)."""
    tmp = tempfile.mkdtemp()
    item = clean_mc("Which is one?") + "[ID: aaaaaaaaaaaaaaaa]\n"
    bank = key_bank(
        tmp,
        "### Airway\n\n> [!KEY] OPA indications\n"
        "> The OPA holds the tongue off the pharynx.\n",
        item=item)
    res = subprocess.run(
        [sys.executable, os.path.join(ROOT, "itembank.py"), "id-assign", bank],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=30)
    if res.returncode != 0:
        fail("id-assign failed: " + res.stdout)
    text = open(bank, encoding="utf-8").read()
    key_id_m = re.search(r"> \[ID: ([0-9a-f]{16})\]", text)
    if not key_id_m:
        fail("id-assign did not mint a [ID:] into the key block:\n%s" % text)
    if key_id_m.group(1) == "aaaaaaaaaaaaaaaa":
        fail("key id collided with the item's id")
    if "> [HASH: sha256:" not in text:
        fail("id-assign did not record the key's [HASH:]")

    before = text
    res2 = subprocess.run(
        [sys.executable, os.path.join(ROOT, "itembank.py"), "id-assign", bank],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=30)
    if open(bank, encoding="utf-8").read() != before:
        fail("a second id-assign run must be a byte-identical no-op")
    model_src = open(os.path.join(ROOT, "model.py"), encoding="utf-8").read()
    if re.search(r"def new_key_id|def key_id\(", model_src):
        fail("a separate key-id function must not exist")


def test_key_lint_no_front_missing_id_duplicate():
    """key.no_front errors on a body with neither title nor cloze;
    key.missing_id/key.missing_hash warn on unminted blocks; key.duplicate_id
    fires when two blocks share an [ID:] (D-05, UI-SPEC §16)."""
    tmp = tempfile.mkdtemp()
    bank = key_bank(
        tmp,
        "### Airway\n\n"
        "> [!KEY]\n> A body with no title and no cloze.\n\n"
        "> [!KEY] Titled\n> Fine body.\n\n"
        "> [!KEY] Id'd\n> [ID: 2222222222222222]\n> Has id, no hash.\n")
    qs = itembank.load(bank)
    errors, warnings = itembank.lint(
        qs, lesson=itembank.parse_lesson(bank),
        terms=itembank.parse_terms(bank),
        keys=itembank.parse_key_blocks(bank))
    no_front = [e for e in errors if e.code == "key.no_front"]
    if len(no_front) != 1 or no_front[0].item != "BANK":
        fail("key.no_front must be a single BANK error: %r" % errors)
    missing_id = [w for w in warnings if w.code == "key.missing_id"]
    if len(missing_id) != 2:
        fail("unminted key blocks must warn key.missing_id, got %r" % warnings)
    missing_hash = [w for w in warnings if w.code == "key.missing_hash"]
    if len(missing_hash) != 1:
        fail("an id'd block without a hash must warn key.missing_hash, got %r"
             % warnings)

    bank2 = key_bank(
        tmp,
        "### Airway\n\n"
        "> [!KEY] One\n> [ID: 1111111111111111]\n> First body.\n\n"
        "> [!KEY] Two\n> [ID: 1111111111111111]\n> Second body.\n")
    qs2 = itembank.load(bank2)
    errors2, _ = itembank.lint(
        qs2, lesson=itembank.parse_lesson(bank2),
        terms=itembank.parse_terms(bank2),
        keys=itembank.parse_key_blocks(bank2))
    dup = [e for e in errors2 if e.code == "key.duplicate_id"]
    if len(dup) != 1 or dup[0].item != "BANK":
        fail("shared [ID:] across key blocks must be a BANK error: %r"
             % errors2)


# ---- plan 03.1-03 Task 3: key card, key_review route, drill print ---------

def test_key_card_renders_runtime_and_degraded():
    """A [!KEY] block renders as the index card: id anchor, Ledger footer,
    {{cloze}} shown as enclosed text, and a real Add-to-review form when the
    daemon serves it; without the runtime the form is absent and the exact
    degraded copy renders instead of a dead control (UI-SPEC §9.2/§15)."""
    tmp = tempfile.mkdtemp()
    bank = key_bank(
        tmp,
        "### Airway\n\n"
        "> [!KEY] OPA indications\n"
        "> [ID: 1111111111111111]\n"
        "> [HASH: sha256:abc]\n"
        "> The OPA is {{indicated when the tongue obstructs}}.\n")
    qs = itembank.load(bank)
    pg = lesson.lesson_page(bank, qs, itembank.parse_lesson(bank),
                            runtime=True)
    if '<section class="callout callout-key" id="key-1111111111111111">' \
            not in pg:
        fail("key card section/anchor missing")
    if "Key point" not in pg:
        fail("key card label missing")
    if "key: 1111111111111111 \u00b7 exports to Anki" not in pg:
        fail("key card Ledger footer missing")
    if '<form method="post" action="/key/1111111111111111/review"' not in pg:
        fail("key card review form missing")
    if "Add to review" not in pg:
        fail("Add to review control missing")
    if "{{indicated when the tongue obstructs}}" in pg:
        fail("{{cloze}} must render as its enclosed text on screen")
    if "The OPA is indicated when the tongue obstructs." not in pg:
        fail("cloze enclosed text must be visible")

    pg2 = lesson.lesson_page(bank, qs, itembank.parse_lesson(bank))
    if ("Review scheduling is unavailable without the runtime. Run itembank "
            "export anki to take this key to Anki.") not in pg2:
        fail("static render must carry the exact unavailable copy")
    if "<form" in pg2:
        fail("static render must omit the review form, never disable it")

    bank2 = key_bank(
        tmp,
        "### Airway\n\n> [!KEY] Untagged\n> A body with no id.\n")
    pg3 = lesson.lesson_page(bank2, itembank.load(bank2),
                             itembank.parse_lesson(bank2), runtime=True)
    if "exports to Anki" in pg3 or "<form" in pg3:
        fail("an id-less key card must omit footer and review control "
             "(%s)" % pg3[pg3.find("callout-key"):pg3.find("callout-key") + 200])


def test_key_review_route_and_cli():
    """POST /key/<id>/review records a key_review event and announces
    'Added to review.'; an unknown key 404s with no event; the CLI twin
    reaches the same recording path (SURF-04)."""
    tmp = tempfile.mkdtemp()
    bank = key_bank(
        tmp,
        "### Airway\n\n"
        "> [!KEY] OPA indications\n"
        "> [ID: 1111111111111111]\n"
        "> [HASH: sha256:abc]\n"
        "> The OPA is indicated when the tongue obstructs.\n")
    proc, url, _ = start_daemon(tmp)
    try:
        req = urllib.request.Request(
            url + "/key/1111111111111111/review", method="POST")
        with urllib.request.urlopen(req, timeout=5) as res:
            body = res.read().decode("utf-8")
        if "Added to review." not in body:
            fail("review POST must announce Added to review: %r" % body)
        try:
            urllib.request.urlopen(
                urllib.request.Request(
                    url + "/key/9999999999999999/review", method="POST"),
                timeout=5)
            fail("unknown key id must 404")
        except urllib.error.HTTPError as exc:
            if exc.code != 404:
                fail("unknown key id returned %d, not 404" % exc.code)
    finally:
        proc.kill()
        proc.wait()

    log = itembank.log_path(tmp)
    reviews = [e for e in itembank.events(log)
               if e["event_type"] == "key_review"]
    if len(reviews) != 1 or reviews[0]["key_id"] != "1111111111111111":
        fail("the route must record exactly one key_review, got %r" % reviews)
    if "score" in reviews[0]:
        fail("a key_review event must carry no score key")

    cli = subprocess.run(
        [sys.executable, os.path.join(ROOT, "itembank.py"), "key-review",
         bank, "1111111111111111"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=30)
    if cli.returncode != 0 or "Added to review." not in cli.stdout:
        fail("key-review CLI twin failed: %r" % cli.stdout)
    reviews2 = [e for e in itembank.events(log)
                if e["event_type"] == "key_review"]
    if len(reviews2) != 2:
        fail("the CLI twin must record its own key_review event")


def test_drill_print_blanks_clozes_and_answers_last():
    """?print=drill blanks cloze content server-side and prints the Answers
    list at the end: no answer text appears above it (UI-SPEC §10.2)."""
    tmp = tempfile.mkdtemp()
    bank = key_bank(
        tmp,
        "### Airway\n\n"
        "> [!KEY] OPA indications\n"
        "> [ID: 1111111111111111]\n"
        "> [HASH: sha256:abc]\n"
        "> The OPA is {{indicated when the tongue obstructs}}.\n")
    qs = itembank.load(bank)
    pg = lesson.lesson_page(bank, qs, itembank.parse_lesson(bank),
                            runtime=True, drill=True)
    answers_at = pg.find('<section id="answers">')
    if answers_at < 0 or "<h2>Answers</h2>" not in pg:
        fail("drill page missing the Answers section")
    above = pg[:answers_at]
    if "indicated when the tongue obstructs" in above:
        fail("an answer is visible above the Answers list")
    if "{{" in above:
        fail("drill page must blank every cloze marker above the answers")
    if "indicated when the tongue obstructs" not in pg[answers_at:]:
        fail("the Answers list must carry the keyed bodies")


# ---- plan 03.1-04 Task 3: the style footer and the degraded style copy ----

def test_lesson_page_style_footer():
    """Task 3 Test 1: a lesson page rendered under a resolved named style
    carries the exact footer `style: <id> \u00b7 rendered by render_style`;
    a lesson with no style file carries `style: house` and never claims
    render_style (03.1-UI-SPEC 9.6, 15)."""
    tmp = tempfile.mkdtemp()
    try:
        styled = os.path.join(tmp, "styled.md")
        open(styled, "w", encoding="utf-8").write(
            "# Styled bank\n\n[STYLE: checked-prose]\n\n## LESSON\n\n"
            "### A heading\n\nProse.\n\n"
            "Q1. s\nA) a\nB) b\nCORRECT: A\n")
        pg = lesson.lesson_page(styled, itembank.load(styled),
                                itembank.parse_lesson(styled))
        if "style: checked-prose \u00b7 rendered by render_style" not in pg:
            fail("named-style page must carry the 9.6 footer")

        plain = os.path.join(tmp, "plain.md")
        open(plain, "w", encoding="utf-8").write(
            "# Plain bank\n\n## LESSON\n\n### A heading\n\nProse.\n\n"
            "Q1. s\nA) a\nB) b\nCORRECT: A\n")
        pg2 = lesson.lesson_page(plain, itembank.load(plain),
                                 itembank.parse_lesson(plain))
        if "style: house" not in pg2:
            fail("no-style page must carry the `style: house` footer")
        if "rendered by render_style" in pg2:
            fail("house fallback footer must not claim render_style")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_lesson_page_degraded_style_copy():
    """Task 3 Test 4: a bank whose resolved style file is missing renders
    the degraded --warn copy echoing the author-written id (never a
    resolved absolute path), falls back to the house footer, and leaves the
    reason to lint (03.1-UI-SPEC 9.6)."""
    tmp = tempfile.mkdtemp()
    try:
        bank = os.path.join(tmp, "broken_style.md")
        open(bank, "w", encoding="utf-8").write(
            "# Broken style bank\n\n[STYLE: no-such-style]\n\n## LESSON\n\n"
            "### A heading\n\nProse.\n\n"
            "Q1. s\nA) a\nB) b\nCORRECT: A\n")
        pg = lesson.lesson_page(bank, itembank.load(bank),
                                itembank.parse_lesson(bank))
        expected = ("The style file no-such-style could not be read. "
                    "This lesson is shown in the house style. Run itembank "
                    "lint %s for details." % os.path.basename(bank))
        if expected not in pg:
            fail("degraded style page must carry the 9.6 warn copy")
        if "style: house" not in pg:
            fail("degraded style page must fall back to the house footer")
        if "no-such-style \u00b7 rendered" in pg:
            fail("degraded page must not claim the missing style rendered it")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---- quick 260812-e2m D2: every preamble section ends at the next heading ---
# `## TERMS`, `## SOURCES` and `## CASES` all scanned rows to the END of the
# preamble with no stop at the next level-two heading, so a registry placed
# above `## LESSON` swallowed the lesson body: table rows became glossary
# entries, and (because the sources/cases scans accept a one-cell row) every
# prose line became a source id and a case id. One bounded-section helper
# with three callers is the fix; these are its assertions.

ORDER_BANK = os.path.join(ROOT, "fixtures", "terms_above_lesson_bank.md")


def _reordered_bank(tmp):
    """The same fixture with `## LESSON` moved above `## TERMS` -- section
    order in the preamble must not change the parse."""
    text = open(ORDER_BANK, encoding="utf-8").read()
    head, rest = text.split("## TERMS", 1)
    terms_block, lesson_block = rest.split("## LESSON", 1)
    body, item = lesson_block.split("Q1.", 1)
    path = os.path.join(tmp, "lesson_above_terms_bank.md")
    open(path, "w", encoding="utf-8").write(
        head + "## LESSON" + body + "## TERMS" + terms_block + "Q1." + item)
    return path


def test_preamble_section_stops_at_next_heading():
    """Test 1: with `## TERMS` above `## LESSON`, terms come only from the
    TERMS rows -- no lesson table row is minted as a glossary entry."""
    t = itembank.parse_terms(ORDER_BANK)
    if t is None:
        fail("the ordering fixture carries a ## TERMS section; parse_terms "
             "must not return None")
    if sorted(t["terms"]) != ["sprocket", "widget"]:
        fail("terms must come only from the TERMS section rows, got %r "
             "(a lesson table row was read as a term)" % sorted(t["terms"]))
    # The refs scan still reads the lesson body, wherever the body sits.
    if [r["slug"] for r in t["refs"]] != ["widget", "sprocket"]:
        fail("[[term]] refs must still be collected from the lesson body: %r"
             % t["refs"])


def test_preamble_section_order_is_free():
    """Test 3: the same bank with the two sections in the other order yields
    the identical terms dict."""
    tmp = tempfile.mkdtemp()
    try:
        other = _reordered_bank(tmp)
        a = itembank.parse_terms(ORDER_BANK)
        b = itembank.parse_terms(other)
        if json.dumps(a["terms"], sort_keys=True) != \
                json.dumps(b["terms"], sort_keys=True):
            fail("section order in the preamble changed the parse: %r vs %r"
                 % (sorted(a["terms"]), sorted(b["terms"])))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_preamble_section_boundary_lints_clean():
    """Test 2: linting the ordering fixture emits no duplicate-slug finding,
    because the colliding slugs were never real terms."""
    import model
    qs = itembank.load(ORDER_BANK)
    errors, warnings = model.lint(
        qs, lesson=itembank.parse_lesson(ORDER_BANK),
        terms=itembank.parse_terms(ORDER_BANK))
    for finding in list(errors) + list(warnings):
        if getattr(finding, "code", "") == "terms.duplicate_slug":
            fail("a lesson table row produced a terms.duplicate_slug "
                 "finding: %s" % finding)
    if errors:
        fail("the ordering fixture must lint with no errors: %r"
             % [str(e) for e in errors])


def test_no_terms_bank_matches_phase3_golden():
    """Test 4: a bank with no `## TERMS` section parses byte-identically to
    the recorded Phase 3 golden -- the additive floor proven against an
    artifact, never against a freshly computed value (Directive \u00a74.4)."""
    if itembank.parse_terms(LES_BANK) is not None:
        fail("fixtures/lesson_bank.md carries no ## TERMS section; "
             "parse_terms must return None")
    golden = json.load(open(GOLDEN_PARSE_P3, encoding="utf-8"))
    if json.dumps(itembank.load(LES_BANK), sort_keys=True) != \
            json.dumps(golden["qs"], sort_keys=True):
        fail("a bank with no TERMS section drifted from the Phase 3 golden "
             "parse")
    content = _lesson_content_region(
        lesson.lesson_page(LES_BANK, itembank.load(LES_BANK),
                           itembank.parse_lesson(LES_BANK)))
    if content != open(GOLDEN_CONTENT_P3, encoding="utf-8").read():
        fail("a bank with no TERMS section drifted from the Phase 3 golden "
             "content region")


def test_runnable_live_region_count():
    """Four runnable readouts stay static; the page status is the sole
    steady-state polite region and every Run control names its own readout."""
    ctx = {"runtime": True, "run_languages": ["python"],
           "run_session_id": "synthetic-session", "code_seq": [0]}
    blocks = "\n".join("```python\nprint(%d)\n```" % n for n in range(4))
    body = lesson.render_markdown(blocks, ctx)
    if body.count('class="run-status"') != 4:
        fail("four runnable fences must render four status readouts")
    if body.count('aria-live="off"') != 4:
        fail("every idle runnable readout must be aria-live=off")
    if 'aria-live="polite"' in body or 'role="status"' in body:
        fail("runnable blocks must not add steady-state polite regions")
    for n in range(1, 5):
        if 'aria-describedby="run-status-%d"' % n not in body or \
                'id="run-status-%d"' % n not in body:
            fail("Run control %d must describe its own status readout" % n)


def test_plain_bank_public_item_matches_pre_13_5_golden():
    """The complete key-free public item projection remains byte-identical
    to the independently captured parent-of-Phase-13.5 fixture."""
    text = ("# Synthetic compatibility bank\n\n" +
            clean_mc("Which synthetic option is keyed?"))
    work = tempfile.mkdtemp()
    try:
        path = os.path.join(work, "plain.md")
        open(path, "w", encoding="utf-8").write(text)
        if itembank.parse_terms(path) is not None or \
                itembank.parse_lesson(path) is not None:
            fail("compatibility bank must contain neither TERMS nor LESSON")
        item = itembank.public_item(itembank.load(path)[0])
        actual = json.dumps(item, ensure_ascii=False,
                            separators=(",", ":")).encode("utf-8")
        expected = open(PUBLIC_ITEM_GOLDEN_PRE_13_5, "rb").read().rstrip(b"\n")
        if actual != expected:
            fail("plain-bank public item drifted from the pre-13.5 golden")
        golden = json.loads(expected.decode("utf-8"))
        for banned in ("key", "correct", "why", "rationale", "terms",
                       "lesson", "explain"):
            if banned in golden:
                fail("pre-13.5 public item golden leaks top-level %s" % banned)
    finally:
        shutil.rmtree(work, ignore_errors=True)


def test_sources_and_cases_share_the_boundary():
    """Test 5: the same boundary holds for the `## SOURCES` and `## CASES`
    registries -- a lesson table row (or a line of lesson prose) below either
    section is not a source and not a case."""
    import model
    ps = model.parse_sources(ORDER_BANK)
    if sorted(ps["sources"]) != ["fixture-note"]:
        fail("## SOURCES swallowed the lesson body: %r" % sorted(ps["sources"]))
    pc = model.parse_cases(ORDER_BANK)
    if sorted(pc["cases"]) != ["fixture-case"]:
        fail("## CASES swallowed the lesson body: %r" % sorted(pc["cases"]))


def test_fenced_pipe_row_is_not_a_row():
    """Test 6: a pipe row inside a fenced code block within a preamble
    section is not a row of that section."""
    import model
    t = itembank.parse_terms(ORDER_BANK)
    if "fencepost" in t["terms"]:
        fail("a pipe row inside a fenced block was read as a term row: %r"
             % sorted(t["terms"]))
    tmp = tempfile.mkdtemp()
    try:
        bank = os.path.join(tmp, "fenced_sources_bank.md")
        open(bank, "w", encoding="utf-8").write(
            "# Fenced registry rows (synthetic)\n\n## SOURCES\n\n"
            "real-note | Invented note, page 1\n\n"
            "```text\nfenced-note | Not a source row\n```\n\n"
            "## LESSON\n\n### H\n\nProse.\n\n"
            + clean_mc("Which is one?"))
        ps = model.parse_sources(bank)
        if sorted(ps["sources"]) != ["real-note"]:
            fail("a fenced pipe row was read as a source row: %r"
                 % sorted(ps["sources"]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


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
test_lesson_style_composes_theme_shared_lesson()
test_lesson_heading_ramp_locked()
test_lesson_content_region_byte_identical_phase3()
test_lesson_parse_identity_phase3()
test_callout_kinds_render_locked_labels()
test_callout_unknown_kind_degrades_to_paragraph()
test_callout_body_and_label_escaped()
test_existing_block_branches_byte_identical_without_callouts()
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
test_parse_terms_basic()
test_parse_terms_absent_and_question_parse_unchanged()
test_terms_meta_captured_and_marked_ignored()
test_terms_lint_unknown_ref_and_no_block()
test_terms_lint_empty_block_and_duplicate_slug()
test_terms_lint_key_in_rationale_and_duplicate_id()
test_terms_lint_sentinel_exported_and_default_unchanged()
test_glossable_gate()
test_glossary_appendix_renders_after_lesson()
test_gloss_triggers_panels_and_no_leak()
test_gloss_marks_and_print_modes()
test_gloss_placement_hover_and_key_link_contract()
test_scroll_contract_and_reader_nav_modes()
test_gloss_example_layout_and_reader_nav()
test_gloss_route_and_cli_twin()
test_reader_settings_registered_in_schema()
test_parse_key_blocks()
test_key_id_minting_shared_namespace()
test_key_lint_no_front_missing_id_duplicate()
test_key_card_renders_runtime_and_degraded()
test_key_review_route_and_cli()
test_drill_print_blanks_clozes_and_answers_last()
test_lesson_page_style_footer()
test_lesson_page_degraded_style_copy()
test_spec_documents_new_grammar_constructs()
test_lesson_layout_folded_into_09_02()
test_spec_only_bank_round_trips_new_constructs()
test_provenance_registry_parses_and_directives_resolve()
test_provenance_lint_unknown_and_duplicate_ids()
test_provenance_lint_codes_published()
test_provenance_compatibility_floor()
test_paraphrase_check_copy_overlap_and_pass()
test_paraphrase_lint_codes_fire_and_never_echo_source_text()
test_paraphrase_thresholds_are_settings_and_roundtrip()
test_unsourced_specific_requires_a_source()
test_case_and_prereq_grammar_parses_and_lints()
test_case_prereq_compatibility_floor()
test_d19_two_file_layout_prose_file_distinct_from_items_file()
test_preamble_section_stops_at_next_heading()
test_preamble_section_order_is_free()
test_preamble_section_boundary_lints_clean()
test_no_terms_bank_matches_phase3_golden()
test_runnable_live_region_count()
test_plain_bank_public_item_matches_pre_13_5_golden()
test_sources_and_cases_share_the_boundary()
test_fenced_pipe_row_is_not_a_row()
print("ok: lesson roundtrip (slug, parse, fingerprint, LESSON-SRC, degraded state, route, CLI twin, both link directions, lesson lint, coupling guards, provenance grammar + compatibility floor, preamble section boundary)")
