#!/usr/bin/env python3
"""Smoke-test the canonical study and Anki export surfaces, plus the Wave 0
semantic-DOM and sentinel-bank helpers Phase 4's later plans reuse.

The original study/export smoke checks are preserved byte-for-byte in
behavior; the additions are reusable infrastructure only: a synthetic
sentinel bank, an explanation fixture matching `runtime.explain_payload`'s
shape, and semantic-DOM helpers built on `tests/presentation_roundtrip.py`.

Standard library only, runnable as `python tests/surface_roundtrip.py`.
"""
import os
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "itembank.py"
BANK = ROOT / "fixtures" / "sample_bank.md"

sys.path.insert(0, str(ROOT))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import presentation_roundtrip                            # noqa: E402
import theme_roundtrip                                   # noqa: E402


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def run(*args):
    return subprocess.run([sys.executable, str(TOOL), *map(str, args)],
                          cwd=ROOT, check=True, capture_output=True, text=True)


# ---- reusable sentinel bank and explanation fixtures ------------------------

SENTINEL_BANK = """# Sentinel bank (synthetic)

Fully invented content so the Phase 4 harnesses never depend on the real
fixture bank's shape drifting.

Q1. One plus one equals?   (difficulty: recall)
[ID: sentinel-mc-0001]
[OBJECTIVE: Math / basics]
A) One
B) Two
C) Three
CORRECT: B
WHY BEST: One plus one is two.
KEY DISCRIMINATOR: It is simple arithmetic.
SECOND-BEST: A, if the question meant counting the addends.
TRAP: Counting the question itself.
CONFIDENCE: high

Q2. Explain what a sentinel value is.   (difficulty: analysis)
[ID: sentinel-short-0001]
[TYPE: short]
[OBJECTIVE: Math / basics]
MODEL: A sentinel is a marker value used to signal a boundary or end.
RUBRIC:
- Names a marker value
- States it signals a boundary or end
TRAP: Overcomplicating the definition.
CONFIDENCE: high
"""


def explain_fixture(qtype="mc"):
    """A dict in the exact `runtime.explain_payload()` output shape, for
    presentation assertions that must not need a real bank to run.
    """
    if qtype == "short":
        return {"answer_text": "A sentinel is a marker value.",
                "why": "", "disc": "", "second": "", "trap": "",
                "notes": [], "model": "A sentinel is a marker value.",
                "rubric": ["Names a marker value"]}
    return {"answer_text": "B) Two", "why": "One plus one is two.",
            "disc": "It is simple arithmetic.", "second": "A, if counting addends.",
            "trap": "Counting the question itself.",
            "notes": ["Arithmetic follows the operator."],
            "correct": ["B"], "da": {"A": "One is a single addend."}}


def sentinel_items():
    """The parsed sentinel bank, one dict per item -- cached on the module
    so repeated calls do not re-parse the source text.
    """
    if not hasattr(sentinel_items, "_cache"):
        import itembank
        sentinel_items._cache = itembank.parse_bank(SENTINEL_BANK)
    return sentinel_items._cache


def synthetic_q(kind):
    """A full parsed-shape question for one item type, with every
    explanation field populated -- the shape `model.parse_question` produces,
    hand-built so the plan 04-05 harness never depends on fixture-bank drift.
    """
    base = {"id": "syn-0001", "number": 1, "type": kind,
            "stem": "Synthetic stem.", "difficulty": "recall",
            "objective": "Math / basics", "lesson_ref": "",
            "lesson_slug": "", "item_id": "", "content_hash": "",
            "conf": "high", "why": "Synthetic why.",
            "disc": "Synthetic discriminator.",
            "second": "Synthetic second-best.", "trap": "Synthetic trap."}
    if kind in ("mc", "multi"):
        base.update({"opts": {"A": "Option one", "B": "Option two",
                              "C": "Option three"},
                     "correct": ["B"] if kind == "mc" else ["A", "C"],
                     "da": {"A": "Distractor A", "B": "Distractor B",
                            "C": "Distractor C"},
                     "select": 1 if kind == "mc" else 2,
                     "notes": ["Synthetic note."]})
    elif kind in ("table", "dnd"):
        base.update({"cats": ["Routine", "Emergency"],
                     "rows": [{"text": "Row one", "cat": "Routine"},
                              {"text": "Row two", "cat": "Emergency"}],
                     "notes": ["Synthetic note."]})
    elif kind == "build":
        base.update({"steps": ["Alpha", "Beta", "Gamma"],
                     "notes": ["Synthetic note."]})
    elif kind == "short":
        base.update({"model": "Synthetic model answer.",
                     "rubric": ["Rubric point one", "Rubric point two"],
                     "notes": ["Synthetic note."]})
    return base


def served_quiz_html(bank_text=SENTINEL_BANK):
    """Render a served quiz page for `bank_text` through the existing
    `quiz.page_for(..., serve=True)` -- the same render the daemon serves, so
    semantic-DOM checks run against real current output without a server.
    """
    from surfaces.quiz import page_for
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "sentinel_bank.md")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(bank_text)
        import itembank
        qs = itembank.load(path)
        _, page = page_for(path, qs, serve=True, post_path="/quiz/sentinel_bank/answer",
                           lesson_base="", lesson_slugs=set())
        return page


def semantic_dom(html):
    """Parse `html` into the shared semantic DOM (presentation_roundtrip)."""
    return presentation_roundtrip.Dom(html)


# ---- preserved smoke checks + Wave 0 helper self-check ----------------------

def check_study_and_export():
    with tempfile.TemporaryDirectory() as tmp:
        study = Path(tmp) / "study.html"
        basic = Path(tmp) / "basic.tsv"
        cloze = Path(tmp) / "cloze.tsv"
        run("study", BANK, study)
        run("export", BANK, basic)
        run("export", BANK, cloze, "--format", "cloze")
        assert "Flashcards" in study.read_text(encoding="utf-8")
        assert "#notetype:Basic" in basic.read_text(encoding="utf-8")
        assert "#notetype:Cloze" in cloze.read_text(encoding="utf-8")
        assert "{{c1::" in cloze.read_text(encoding="utf-8")


def check_semantic_helpers():
    items = sentinel_items()
    if len(items) < 2:
        fail("sentinel bank parsed into %d items, expected at least 2" % len(items))
    if items[0]["type"] != "mc" or items[1]["type"] != "short":
        fail("sentinel bank item types are not mc/short: %r"
             % [q["type"] for q in items])
    ex = explain_fixture()
    if ex["correct"] != ["B"] or not ex["da"].get("A"):
        fail("explain_fixture does not match the sentinel mc shape: %r" % ex)
    ex = explain_fixture("short")
    if ex.get("model") != "A sentinel is a marker value." or not ex["rubric"]:
        fail("explain_fixture('short') is malformed: %r" % ex)

    page = served_quiz_html()
    dom = semantic_dom(page)
    presentation_roundtrip.assert_landmark(dom, "nav")
    # The question hierarchy is JS-rendered (one item at a time from the API),
    # so Wave 0 asserts the shell: the context region, the details disclosure,
    # the response host, and that the page really is a script-driven client.
    if not any(n["tag"] == "nav" and "data-surface-context" in n["attrs"]
               for n in dom.all("nav")):
        fail("served sentinel page has no data-surface-context region")
    if len(dom.details()) != 1:
        fail("served sentinel page must carry exactly one details disclosure")
    if dom.find("div", id="host") is None:
        fail("served sentinel page has no #host response container")
    if 'createElement("button")' not in page:
        fail("served sentinel page does not build controls in JavaScript")
    if not theme_roundtrip.surface_has_shared_theme(page):
        fail("served sentinel page carries no shared --accent theme block")


def check_question_hierarchy():
    """Phase 4 Task 3: one sticky context line, one details disclosure, a
    single dominant stem h1, native controls, a reserved feedback region, and
    one primary next action per state (D-01 through D-03).
    """
    page = served_quiz_html()
    dom = semantic_dom(page)

    # Exactly one sticky context region with the four orientation fields.
    contexts = [n for n in dom.all("nav")
                if "data-surface-context" in n["attrs"]]
    if len(contexts) != 1:
        fail("expected exactly one data-surface-context region, got %d"
             % len(contexts))
    ctx = contexts[0]
    bank_span = dom.find("span", id="cx-bank")
    if bank_span is None or "Sentinel bank" not in bank_span["text"]:
        fail("context line missing bank context: %r"
             % (bank_span["text"] if bank_span else None))
    if not any(n["tag"] == "span" and "Item" in n["text"]
               for n in dom.all("span")):
        fail("context line missing item N of M progress")
    if not dom.find("span", id="cx-objective"):
        fail("context line missing the objective slot")
    if not dom.find("span", id="cx-mode"):
        fail("context line missing the session-mode slot")

    # Secondary metadata lives in exactly one native details disclosure.
    det = dom.details()
    if len(det) != 1:
        fail("expected exactly one details disclosure, got %d" % len(det))
    summaries = [n for n in dom.all("summary")]
    if not summaries or "Session details" not in summaries[0]["text"]:
        fail("details disclosure missing the locked summary label")

    # DOM order in the served client: context nav, then h1 stem, response
    # control (appended into body), role=status feedback region, then the
    # next-action container. The renderItem assembly proves the structural
    # order: stem h1 -> body(controls) -> feedback -> act.
    served_js_start = page.find('<script id="served">')
    served_js = page[served_js_start:]
    rstart = served_js.find("function renderItem(")
    if rstart < 0:
        fail("served client has no renderItem function")
    body_js = served_js[rstart:]
    h1_at = body_js.find('<h1 class="stem">')
    fb_at = body_js.find('fb.className = "feedback"')
    fb_role_at = body_js.find('fb.setAttribute("role", "status")')
    fb_append_at = body_js.find("card.appendChild(fb)")
    act_append_at = body_js.find("card.appendChild(act)")
    if not (0 < h1_at < fb_at < fb_role_at < fb_append_at < act_append_at):
        fail("served client DOM order is not context, h1, control, feedback, "
             "action (positions %d %d %d %d %d)"
             % (h1_at, fb_at, fb_role_at, fb_append_at, act_append_at))

    # Native controls: radio for mc, checkbox for multi, all 44px targets.
    if '"radio"' not in served_js or '"checkbox"' not in served_js:
        fail("served client must use native radio/checkbox inputs")
    if 'input.type = multi ? "checkbox" : "radio"' not in served_js:
        fail("served client must choose native input type per item kind")
    css = page[page.find("__THEME__"):]
    css = page[page.find("<style>") + len("<style>"):page.find("</style>")]
    for rule in (".choice{", ".opt{", "button.go{", "min-height:44px"):
        if rule not in css:
            fail("controls lack a 44px target rule (%r)" % rule)

    # Stem typography: 28px wide, 20px narrow; feedback 96px/120px.
    if "h1.stem{font-size:28px" not in css:
        fail("stem h1 must be 28px at desktop")
    if "h1.stem{font-size:20px" not in css:
        fail("stem h1 must reduce to 20px at narrow width")
    if ".feedback{min-height:96px" not in css:
        fail("feedback region must reserve 96px at desktop")
    if ".feedback{min-height:120px" not in css:
        fail("feedback region must reserve 120px at narrow width")

    # Reduced motion disables transitions and smooth scrolling.
    rm = presentation_roundtrip.reduced_motion_block(css)
    if rm is None or "scroll-behavior:auto" not in rm:
        fail("reduced-motion block must disable smooth scrolling")

    # One primary next action per state, and the locked state copy.
    for marker in ('b.textContent="Submit answer"',
                   "Checking answer&hellip;",
                   "Couldn't check that answer. Your selection",
                   "This session has no question ready.",
                   'b.textContent = "Try again"'):
        if marker not in served_js:
            fail("served client missing state copy/action: %r" % marker)

    # The h1 is the only heading in the shell (the old page title is gone).
    hs = dom.headings()
    if hs != []:
        fail("served shell must carry no static headings (stem is JS-rendered), "
             "got %r" % hs)


# ---- plan 04-05 Task 1: canonical complete study payload -------------------

def check_study_item_choice_payload():
    """Test 1: mc/multi `study_item` carries public options plus answer_text,
    why, correct, every non-empty da rationale, second, disc, trap, and all
    notes -- exactly the runtime's own explain payload, no hand-picked copy.
    """
    from runtime import explain_payload
    from surfaces.study import study_item
    for kind in ("mc", "multi"):
        q = synthetic_q(kind)
        view = study_item(q)
        for key in ("id", "type", "stem", "objective"):
            if view.get(key) != q[key]:
                fail("%s study_item lost the stable %r shape: %r"
                     % (kind, key, view))
        if not view.get("options") or len(view["options"]) != 3:
            fail("%s study_item carries no public options list: %r"
                 % (kind, view))
        ex = view.get("explain")
        if not isinstance(ex, dict):
            fail("%s study_item has no explain member: %r" % (kind, view))
        expected = explain_payload(q, reveal=True)
        if ex != expected:
            fail("%s study_item explain diverges from runtime.explain_payload: "
                 "got %r expected %r" % (kind, ex, expected))
        if not ex["da"]:
            fail("%s study explain dropped every option rationale: %r"
                 % (kind, ex))
        if ex["notes"] != ["Synthetic note."]:
            fail("%s study explain lost notes: %r" % (kind, ex))


def check_study_item_nonchoice_payload():
    """Test 2: table/dnd/build/short cards preserve every field their
    explain_payload branch returns; empty optional fields stay empty rather
    than being fabricated.
    """
    from runtime import explain_payload
    from surfaces.study import study_item
    for kind in ("table", "dnd", "build", "short"):
        q = synthetic_q(kind)
        ex = study_item(q).get("explain")
        expected = explain_payload(q, reveal=True)
        if not isinstance(ex, dict):
            fail("%s study_item has no explain member: %r" % (kind, ex))
        if ex != expected:
            fail("%s study_item explain diverges from runtime.explain_payload: "
                 "got %r expected %r" % (kind, ex, expected))
    q = synthetic_q("short")
    q["model"] = ""
    q["rubric"] = []
    ex = study_item(q)["explain"]
    if ex != explain_payload(q, reveal=True):
        fail("empty optional short fields were fabricated: %r" % ex)
    if ex["model"] != "" or ex["rubric"] != []:
        fail("empty short fields did not stay empty: %r" % ex)


def check_study_item_sentinels_reach_reveal():
    """Test 3: a sentinel in every explanation field appears exactly once in
    the generated study data and exactly once in the rendered reveal output
    -- no independent hand-copied projection can drift.
    """
    from surfaces.study import study_item, study_page
    q = synthetic_q("mc")
    q["why"] = "SENTINEL_WHY"
    q["disc"] = "SENTINEL_DISC"
    q["second"] = "SENTINEL_SECOND"
    q["trap"] = "SENTINEL_TRAP"
    q["notes"] = ["SENTINEL_NOTE"]
    q["da"] = {"A": "SENTINEL_DA_A", "B": "SENTINEL_DA_B",
               "C": "SENTINEL_DA_C"}
    sentinels = ("SENTINEL_WHY", "SENTINEL_DISC", "SENTINEL_SECOND",
                 "SENTINEL_TRAP", "SENTINEL_NOTE",
                 "SENTINEL_DA_A", "SENTINEL_DA_B", "SENTINEL_DA_C")
    data = json.dumps(study_item(q), ensure_ascii=False)
    for s in sentinels:
        if data.count(s) != 1:
            fail("sentinel %r appears %d times in generated study data, "
                 "expected exactly once" % (s, data.count(s)))
    with tempfile.TemporaryDirectory() as tmp:
        bank = os.path.join(tmp, "sentinel_bank.md")
        with open(bank, "w", encoding="utf-8") as fh:
            fh.write("# Sentinel study bank\n\nQ1. Stem.\n"
                     "A) One\nB) Two\nC) Three\nCORRECT: B\n")
        page = study_page(bank, [q])
    m = re.search(r"const CARDS=(\[.*?\]);", page, re.S)
    if not m:
        fail("study page carries no embedded CARDS data element")
    embedded = m.group(1)
    for s in sentinels:
        if embedded.count(s) != 1:
            fail("sentinel %r appears %d times in the embedded study data, "
                 "expected exactly once" % (s, embedded.count(s)))
    start = page.find("<script")
    end = page.find("</script>", start) + len("</script>")
    visible = page[:start] + page[end:]
    for s in sentinels:
        if visible.count(s) != 1:
            fail("sentinel %r appears %d times in the rendered reveal output, "
                 "expected exactly once" % (s, visible.count(s)))


def check_study_script_safety():
    """Test 4: bank text containing HTML or a script terminator is serialized
    inert and later rendered through escaping -- it can never close the data
    element or execute.
    """
    from surfaces.study import study_page
    hostile = ("Q1. <script>alert(1)</script> stem?  (difficulty: recall)\n"
               "A) <img src=x onerror=alert(2)>\nB) Two\nC) Three\n"
               "CORRECT: B\n"
               "WHY BEST: </script><script>alert(3)</script>\n"
               "CONFIDENCE: high\n")
    with tempfile.TemporaryDirectory() as tmp:
        bank = os.path.join(tmp, "hostile_bank.md")
        with open(bank, "w", encoding="utf-8") as fh:
            fh.write("# Hostile bank\n\n" + hostile)
        import itembank
        qs = itembank.parse_bank(open(bank, encoding="utf-8").read())
        page = study_page(bank, qs)
    if page.count("<script") != 1 or page.count("</script>") != 1:
        fail("hostile bank text closed or duplicated the page script element "
             "(<script count %d, </script> count %d)"
             % (page.count("<script"), page.count("</script>")))
    if "\\u003c/script\\u003e" not in page:
        fail("hostile serialization did not escape the script terminator")
    if "&lt;script&gt;alert(1)&lt;/script&gt;" not in page:
        fail("rendered stem was not escaped text")
    if '<img src=x onerror=alert(2)>' in page.replace("&lt;", "<").replace(
            "&gt;", ">"):
        fail("hostile option text reached the page as executable markup")


def check_study_empty_and_error_states():
    """Test 5: empty input renders the shared state panel with the exact
    empty copy; a malformed card renders an error state that keeps bank
    context and a retry/back action instead of a blank page.
    """
    from surfaces.study import study_page
    with tempfile.TemporaryDirectory() as tmp:
        bank = os.path.join(tmp, "empty_bank.md")
        with open(bank, "w", encoding="utf-8") as fh:
            fh.write("# Empty study bank\n\nNo questions here.\n")
        page = study_page(bank, [])
        if "No study cards match this bank." not in page:
            fail("empty study page is missing the locked empty copy")
        if 'role="status"' not in page:
            fail("empty study state is not in a persistent status region")
        if 'data-state="empty"' not in page:
            fail("empty study state does not use the shared state panel")
    with tempfile.TemporaryDirectory() as tmp:
        bank = os.path.join(tmp, "broken_bank.md")
        with open(bank, "w", encoding="utf-8") as fh:
            fh.write("# Broken study bank\n\nQ1. ???\n")
        page = study_page(bank, [{"type": "mc"}])
        if ("This card could not be shown. Move to the next card or reload."
                not in page):
            fail("render-error study page lacks the recovery copy")
        if "Broken study bank" not in page:
            fail("render-error study page lost bank context")
        if 'data-state="bad"' not in page:
            fail("render-error study page does not use the shared error panel")
        if not re.search(r'class="go[^"]*"[^>]*>\s*Reload', page) \
                and "Choose another bank" not in page:
            fail("render-error study page has no retry/back action")


def main():
    check_study_and_export()
    check_semantic_helpers()
    check_question_hierarchy()
    check_study_item_choice_payload()
    check_study_item_nonchoice_payload()
    check_study_item_sentinels_reach_reveal()
    check_study_script_safety()
    check_study_empty_and_error_states()
    print("study and export surfaces + Phase 4 question hierarchy: ok")


if __name__ == "__main__":
    main()
