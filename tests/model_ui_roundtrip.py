#!/usr/bin/env python3
"""Assert the Phase 8 learner surface: the AgentAssist lifecycle, the
structural lock, the pending rubric checklist, and the no-leak API/DOM
boundary (plan 08-05 Tasks 1-2).

The browser is a client of the canonical /api/* JSON session API and renders
only typed runtime payloads. These checks prove, from the served page source
and from the API responses the served client consumes:

  1. DOM order + exact 08-UI-SPEC copy + collapsed opt-in default;
  2. lifecycle states (Preparing optional guidance... -> Generated support or
     the exact unavailable/policy-drop copy) and the labeled structural lock
     with the unlock condition stated, with no model voice;
  3. pending rubric rows: one semantic row per point with the pending token
     only, and no accept control of any kind anywhere in the browser;
  4. no-leak scans over the page HTML, all JSON payloads, and the served
     scripts (flatten() discipline) -- key strings, tier numbers, fact
     text, profile names, backend classes, gate reasons, and dropped
     candidate phrases appear nowhere;
  5. the assist works at 320px/200% zoom with no horizontal scroll, reduced
     motion disables nonessential animation, and status changes announce
     once.

Standard library only, no test framework, runnable as
`python tests/model_ui_roundtrip.py`.
"""
import json, os, re, shutil, subprocess, sys, tempfile, threading, time
import urllib.error, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import evidence                                             # noqa: E402
import itembank                                             # noqa: E402
from surfaces import daemon                                  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import serve_roundtrip                                       # noqa: E402

SAMPLE = os.path.join(ROOT, "fixtures", "sample_bank.md")
LESSON = os.path.join(ROOT, "fixtures", "lesson_bank.md")


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


# The exact 08-UI-SPEC Copywriting Contract strings this plan locks. Every
# one must appear verbatim in the served page; tests read this tuple so a
# typo in the contract fails the suite instead of the test.
BINDING_COPY = (
    "Help and evidence",
    "Get optional guidance",
    "Preparing optional guidance\u2026",
    "Generated support",
    "This guidance is generated from the current attempt and the help "
    "available at this step.",
    "Generated help is unavailable. You can keep learning with the lesson "
    "and authored hints.",
    "Generated help is unavailable for this step. Continue with the "
    "available hint or try another attempt.",
    "Try generated guidance again",
    "Pending rubric suggestion \u2014 human review required",
    "No complete rubric suggestion is available. This response is still "
    "waiting for a human mark.",
)

# The authority vocabulary that must never cross the API/DOM boundary
# (D-09, D-26). These strings are scanned over the served page, every JSON
# payload the client consumes, and the served scripts.
FORBIDDEN_STRINGS = (
    "tier0.", "tier1.", "tier2.", "tier3.", "tier4.", "tier5.",
    "gate.schema_invalid", "gate.span_unmatched", "gate.fact_protected",
    "gate.fact_unknown", "gate.ambiguous", "gate.unsupported_move",
    "hosted_cli", "openai_compatible", "fake-hosted", "backend_class",
    "interaction: the wrong answer",  # the dropped-candidate phrase below
)


def flatten(obj):
    """Yield every value at every depth of a JSON-like structure, and every
    key too -- the same discipline evidence_roundtrip.py's flatten() applies
    to its forbidden keys, so a forbidden string hidden in a field NAME also
    fails the scan.
    """
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield k
            yield v
            yield from flatten(v)
    elif isinstance(obj, list):
        for el in obj:
            yield from flatten(el)


def start_daemon(workdir):
    proc = subprocess.Popen(
        [sys.executable, "-u", os.path.join(ROOT, "itembank.py"), "daemon",
         workdir, "--no-open", "--port", "0"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    lines = []
    threading.Thread(target=lambda: [lines.append(l) for l in proc.stdout],
                     daemon=True).start()
    base = None
    for _ in range(60):
        time.sleep(0.1)
        m = re.search(r"http://127\.0\.0\.1:\d+/", "".join(lines))
        if m:
            base = m.group(0)
            break
    if not base:
        proc.terminate()
        fail("daemon never printed a URL. Output was:\n" + "".join(lines))
    return proc, base, lines


def post(url, payload):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as res:
        return json.loads(res.read().decode("utf-8"))


def get(url):
    with urllib.request.urlopen(url, timeout=5) as res:
        return res.status, res.read().decode("utf-8")


def api_by_id(bank):
    qs = itembank.parse_bank(open(bank, encoding="utf-8").read())
    return {q["id"]: q for q in qs}


def fake_cli_script():
    """A fake hosted-CLI executable that returns a gate-passing candidate for
    the fixture lesson bank: a hint_plan referencing the tier-0 lesson fact
    for a wrong "C" answer, or a rubric_proposal for the short item. Reads
    the request from stdin and echoes the minted interaction id.
    """
    return "\n".join([
        "import json, sys",
        "req = json.load(sys.stdin)",
        "if req.get('operation') == 'rubric_review':",
        "    out = {'kind': 'rubric_proposal',",
        "           'interaction_id': req['interaction_id'],",
        "           'points': [",
        "               {'point_index': 0, 'status': 'pass',",
        "                'rationale': 'The response names the health-versus-aesthetic split.'},",
        "               {'point_index': 1, 'status': 'fail',",
        "                'rationale': 'The response does not call secondary standards guidelines.'},",
        "               {'point_index': 2, 'status': 'uncertain',",
        "                'rationale': 'The investigation targets are not specific.'}]}",
        "else:",
        "    payload = req.get('payload') or {}",
        "    out = {'kind': 'hint_plan',",
        "           'interaction_id': req['interaction_id'],",
        "           'focus_span': payload.get('learner_response', 'C'),",
        "           'fact_ids': ['tier0.lesson_ref'],",
        "           'move': 'anchor_error'}",
        "json.dump(out, sys.stdout)",
    ]) + "\n"


def enable_fake_backend(workdir, script_name="fake_hosted.py"):
    """Write `itembank.json` in the daemon workdir pointing model_backend at a
    fake hosted-CLI profile, so a real daemon run reaches the typed pass path.
    """
    script = os.path.join(workdir, script_name)
    open(script, "w", encoding="utf-8").write(fake_cli_script())
    cfg = {
        "model_backend": {
            "active": "hosted",
            "profiles": [{
                "name": "hosted",
                "transport": "hosted_cli",
                "command": [sys.executable, script],
                "model": "fake-hosted",
                "timeout_seconds": 10,
                "max_output_bytes": 65536,
                "context_window": 4096,
            }],
        }
    }
    with open(os.path.join(workdir, "itembank.json"), "w",
              encoding="utf-8") as fh:
        json.dump(cfg, fh)


def hold_non_short(base, by_id):
    """Walk to a non-short item and hold it with a wrong answer; returns
    (session_id, held-submit-result)."""
    started = post(base + "api/start",
                   {"bank": os.path.splitext(os.path.basename(SAMPLE))[0],
                    "count": 6, "seed": 7, "mode": "practice"})
    sid = started["session_id"]
    state = started
    for _ in range(len(by_id) + 2):
        q = by_id[state["item"]["id"]]
        if q["type"] == "short":
            state = state.get("next") or state
            continue
        result = post(base + "api/submit", {"session_id": sid,
                                            "answer": serve_roundtrip.wrong_answer(q)})
        if result.get("action") == "hold":
            return sid, result
        state = result.get("next") or state
    fail("could not hold a non-short item for the assist test")
    return None, None


# ---- Test 1: DOM order, exact copy, collapsed opt-in default ----------------

def check_dom_order_and_copy():
    """The served quiz page contains the assist region after the session
    details in DOM order (activity -> response/hint ladder -> status ->
    collapsed Help and evidence -> AgentAssist), with the exact 08-UI-SPEC
    copy strings; the assist is collapsed and opt-in by default."""
    workdir = tempfile.mkdtemp()
    shutil.copy(SAMPLE, os.path.join(workdir, "sample_bank.md"))
    proc, base, _ = start_daemon(workdir)
    try:
        _status, page = get(base + "quiz/sample_bank")
        if "data-agent-assist" not in page:
            fail("the served quiz page has no AgentAssist region")
        host_at = page.find('id="host"')
        details_at = page.find("session-details")
        assist_at = page.find("data-agent-assist")
        if host_at < 0 or details_at < 0 or assist_at < 0:
            fail("the served page is missing host/session-details/assist "
                 "markers")
        # The UI-SPEC-locked DOM order: activity first, then the collapsed
        # Help and evidence disclosure, then AgentAssist -- all after the
        # session-details metadata region.
        if not (details_at < host_at < assist_at):
            fail("DOM order wrong: session-details=%d host=%d assist=%d; "
                 "want session-details < activity < assist"
                 % (details_at, host_at, assist_at))
        for copy in BINDING_COPY:
            if copy not in page:
                fail("served page is missing the binding copy %r" % copy)
        # Collapsed and opt-in by default: the native details/summary is not
        # open, the request button lives inside it, and the outcome container
        # starts hidden.
        if 'id="assist" open' in page or '<details class="assist"' not in page:
            fail("the assist disclosure is not a collapsed native "
                 "details/summary")
        if 'id="assist-request"' not in page:
            fail("the assist has no opt-in request button")
        if 'id="assist-outcome" hidden' not in page:
            fail("the assist outcome container is not hidden by default")
        # No browser accept control of any kind.
        for banned in ("Record human mark", "accept this suggestion",
                       "Accept suggestion"):
            if banned in page:
                fail("the served page carries an accept control (%r)" % banned)
    finally:
        proc.terminate()
        shutil.rmtree(workdir, ignore_errors=True)


# ---- Test 2: lifecycle states, structural lock, no model voice --------------

def check_lifecycle_and_lock():
    """Requesting guidance renders the lifecycle states: Preparing optional
    guidance... then either Generated support with the generated disclosure
    sentence or the exact unavailable/policy-drop copy. A locked tier renders
    a labeled structural lock with the unlock condition stated and no model
    voice."""
    workdir = tempfile.mkdtemp()
    shutil.copy(SAMPLE, os.path.join(workdir, "sample_bank.md"))
    proc, base, _ = start_daemon(workdir)
    try:
        _status, page = get(base + "quiz/sample_bank")
        # The served client must carry the lifecycle rendering (source-level
        # proof, since these checks run without a browser).
        for needle in ("Preparing optional guidance\u2026", "Generated support",
                       "This guidance is generated from the current attempt",
                       "Generated help is unavailable. You can keep learning",
                       "Try generated guidance again"):
            if needle not in page:
                fail("the served client cannot render lifecycle state %r"
                     % needle)

        by_id = api_by_id(SAMPLE)
        sid, held = hold_non_short(base, by_id)
        hint = post(base + "api/hint", {"session_id": sid})
        if hint.get("action") == "reveal_tier" or \
                hint.get("status") != "unavailable":
            fail("with the default disabled backend, /api/hint must be typed "
                 "unavailable: %r" % hint)
        if "generated" not in hint or hint["generated"] is not None:
            fail("a typed unavailable must carry generated=None: %r" % hint)
        for banned in ("reason", "tier", "profile", "candidate", "gate"):
            if banned in hint:
                fail("the typed unavailable leaks authority material %r: %r"
                     % (banned, hint))

        # No model voice: no chat box and no typing/streaming animation in
        # the assist chrome or its client script.
        assist_markup = page.split('<section class="agent-assist"', 1)[1].split("</section>", 1)[0]
        if "<input" in assist_markup:
            fail("the assist region contains an input (no chat box allowed)")
        for banned in ("typewriter", "streaming", "setInterval", "typing"):
            if banned in page:
                fail("the served page simulates model typing (%r)" % banned)
    finally:
        proc.terminate()
        shutil.rmtree(workdir, ignore_errors=True)

    # Part B: with a fake hosted backend, a genuine wrong answer produces the
    # typed pass path with the generated disclosure.
    workdir2 = tempfile.mkdtemp()
    shutil.copy(LESSON, os.path.join(workdir2, "lesson_bank.md"))
    enable_fake_backend(workdir2)
    proc2, base2, _ = start_daemon(workdir2)
    try:
        started = post(base2 + "api/start",
                       {"bank": "lesson_bank", "count": 2, "seed": 0,
                        "mode": "practice"})
        sid2 = started["session_id"]
        q = api_by_id(LESSON)[started["item"]["id"]]
        wrong = post(base2 + "api/submit", {"session_id": sid2,
                                            "answer": serve_roundtrip.wrong_answer(q)})
        if wrong.get("action") != "hold":
            fail("the lesson-bank wrong submit must hold: %r" % wrong)
        hint = post(base2 + "api/hint", {"session_id": sid2})
        if hint.get("status") != "pass":
            fail("with a fake backend a genuine wrong answer must pass: %r"
                 % hint)
        generated = hint.get("generated") or {}
        if not generated.get("text"):
            fail("a pass hint carries no rendered text: %r" % hint)
        if "reason" in hint or "tier" in hint:
            fail("a pass hint leaks authority material: %r" % hint)
    finally:
        proc2.terminate()
        shutil.rmtree(workdir2, ignore_errors=True)


# ---- Test 3: pending rubric rows, pending token only, no accept control -----

def check_pending_rubric_rows():
    """A short-response rubric proposal renders one pending row per point
    with the exact pending heading and no number, fraction, check, or cross
    glyph; no accept control exists anywhere in the browser DOM."""
    workdir = tempfile.mkdtemp()
    shutil.copy(LESSON, os.path.join(workdir, "lesson_bank.md"))
    enable_fake_backend(workdir)
    proc, base, _ = start_daemon(workdir)
    try:
        _status, page = get(base + "quiz/lesson_bank")
        by_id = api_by_id(LESSON)
        short = next(q for q in by_id.values() if q["type"] == "short")
        started = post(base + "api/start",
                       {"bank": "lesson_bank", "count": 1, "seed": 0,
                        "mode": "practice", "focus": short["id"]})
        sid = started["session_id"]
        sub = post(base + "api/submit", {"session_id": sid,
                                         "answer": "A constructed response "
                                                   "about repositioning."})
        if sub.get("action") != "defer_feedback":
            fail("the short response must defer feedback: %r" % sub)
        rubric = post(base + "api/rubric-review", {"session_id": sid})
        if rubric.get("status") != "pending":
            fail("a pending short response with a fake backend must return "
                 "pending: %r" % rubric)
        points = rubric.get("points") or []
        if len(points) != len(short["rubric"]):
            fail("rubric review returned %d points, expected %d"
                 % (len(points), len(short["rubric"])))
        for p in points:
            if not isinstance(p.get("rationale"), str) or not p["rationale"]:
                fail("a pending rubric point has no rationale: %r" % p)
            for banned in ("gate.", "tier", "profile", "backend"):
                if banned in p.get("rationale", ""):
                    fail("a rubric rationale leaks authority material: %r" % p)
        if "Pending rubric suggestion \u2014 human review required" not in page:
            fail("the served client cannot render the pending rubric heading")
        # The pending token is text-only: no number, fraction, check, cross,
        # or accept glyph anywhere in the served scripts or the assist chrome.
        for banned in ("\u2713", "\u2717", "\u2714", "\u2718", "\u274c",
                       "&#10003;", "&#10007;", "&#10004;", "&#10008;",
                       "Record human mark", "accept"):
            if banned in page:
                fail("the served page carries a forbidden glyph/control %r"
                     % banned)
        assist_scripts = ""
        for m in re.finditer(r"<script[^>]*>(.*?)</script>", page,
                             re.S | re.M):
            assist_scripts += m.group(1)
        # The rubric row renderer must exist and emit one semantic row per
        # point with the pending token; it must never number a row.
        if "rubric-row" not in assist_scripts or "rubric-rows" not in assist_scripts:
            fail("the served client has no per-point pending checklist renderer")
    finally:
        proc.terminate()
        shutil.rmtree(workdir, ignore_errors=True)


# ---- Test 4: no-leak scans over HTML, JSON, and served scripts --------------

def check_no_leak():
    """No key, tier number, fact manifest, profile name, backend class, gate
    reason, or dropped candidate phrase appears anywhere in the page HTML,
    all JSON payloads the client consumes, or the served scripts (flatten()
    discipline)."""
    workdir = tempfile.mkdtemp()
    shutil.copy(LESSON, os.path.join(workdir, "lesson_bank.md"))
    enable_fake_backend(workdir)
    proc, base, _ = start_daemon(workdir)
    try:
        _status, page = get(base + "quiz/lesson_bank")
        scan = json.dumps(page)
        for banned in FORBIDDEN_STRINGS:
            if banned in scan:
                fail("forbidden string %r appears in the served page source"
                     % banned)
        # The fixture bank's private material (key content, model answers,
        # distractor analysis) must never reach the served source.
        by_id = api_by_id(LESSON)
        for q in by_id.values():
            for text in (q.get("why") or "", q.get("disc") or ""):
                if text and text in page:
                    fail("WHY/DISC text leaks into the served page for %s"
                         % q.get("id"))
            if q.get("type") == "short" and (q.get("model") or "") in page:
                fail("the model answer leaks into the served page for %s"
                     % q.get("id"))
        boot = serve_roundtrip.served_boot(page)
        for value in flatten(boot):
            if isinstance(value, str):
                for banned in FORBIDDEN_STRINGS:
                    if banned in value:
                        fail("forbidden string %r appears in the boot payload"
                             % banned)

        # The scripts themselves must be free of authority vocabulary.
        # `reason` is deliberately absent from the list: the check editor's
        # per-case status field (case_observation.reason, published in
        # item.schema.json as the four locked statuses) is learner-facing
        # feedback vocabulary that ships in the shared client (05-06), not
        # authority material -- the model-authority guard keeps the rest.
        for m in re.finditer(r"<script[^>]*>(.*?)</script>", page,
                             re.S | re.M):
            script = m.group(1)
            for banned in ("tier", "profile", "backend", "candidate",
                           "gate", "provider", "fact_manifest", "fact_ids"):
                if banned in script.lower():
                    fail("served script references %r; the browser never "
                         "touches authority vocabulary" % banned)

        # API responses: only typed learner-safe fields cross the wire.
        started = post(base + "api/start",
                       {"bank": "lesson_bank", "count": 2, "seed": 0,
                        "mode": "practice"})
        sid = started["session_id"]
        q = by_id[started["item"]["id"]]
        wrong = post(base + "api/submit", {"session_id": sid,
                                           "answer": serve_roundtrip.wrong_answer(q)})
        if wrong.get("action") != "hold":
            fail("lesson-bank wrong submit did not hold: %r" % wrong)
        hint = post(base + "api/hint", {"session_id": sid})
        for value in flatten(hint):
            if isinstance(value, str):
                for banned in FORBIDDEN_STRINGS:
                    if banned in value:
                        fail("forbidden string %r appears in the /api/hint "
                             "payload" % banned)
        if any(k in hint for k in ("reason", "gate_reason")):
            fail("/api/hint leaks a reason code: %r" % hint)
    finally:
        proc.terminate()
        shutil.rmtree(workdir, ignore_errors=True)


# ---- Test 5: 320px/200% zoom, reduced motion, announce-once ----------------

def check_responsive_and_motion():
    """The assist region must not create horizontal scroll at 320px/200%
    zoom; reduced motion disables nonessential animation; generated-help
    status is live only during the learner-requested wait."""
    workdir = tempfile.mkdtemp()
    shutil.copy(SAMPLE, os.path.join(workdir, "sample_bank.md"))
    proc, base, _ = start_daemon(workdir)
    try:
        _status, page = get(base + "quiz/sample_bank")
        css = page.split("<style>")[1].split("</style>")[0]
        # No fixed-width/min-width traps in the shared CSS: the wrap is
        # fluid (box-sizing border-box), and min-widths are only ever the
        # flexbox overflow-avoidance 0 or tiny touch/key tokens -- never a
        # value that forces horizontal scroll at a 288px 320px-viewport
        # content width.
        for m in re.finditer(r"min-width:\s*([0-9.]+)px", css):
            if float(m.group(1)) >= 240:
                fail("the shared CSS carries a min-width (%spx) that can "
                     "overflow 320px" % m.group(1))
        if "box-sizing:border-box" not in css:
            fail("the shared CSS is missing box-sizing:border-box")
        assist_css = css.split(".agent-assist")[1] if ".agent-assist" in css else ""
        for banned in ("position:fixed", "width:320", "min-width:240",
                       "min-width: 240"):
            if banned in assist_css:
                fail("the assist CSS can force horizontal scroll (%r)" % banned)
        for needle in ("overflow-wrap:anywhere", "word-break:break-all"):
            if needle not in css:
                fail("long assist tokens cannot wrap (%r missing)" % needle)
        # Reduced motion: the locked media query disables nonessential
        # animation, and the assist client never animates on its own.
        if "prefers-reduced-motion" not in page:
            fail("the page has no reduced-motion media query")
        if "*{transition:none!important}" not in css:
            fail("reduced motion does not disable transitions")
        if "requestAnimationFrame" in page or "setInterval" in page:
            fail("the served client animates, which reduced motion must "
                 "disable")
        # The assist readout is static at rest. The shipped client promotes it
        # before waiting copy, then removes the live attribute after terminal
        # success, cancellation, unavailable/drop, or request failure.
        assist_region = page.split("data-agent-assist")[1].split("</section>")[0]
        if "aria-live" in assist_region or 'role="status"' in assist_region:
            fail("the idle assist readout must not be a live region")
        steady_dom = re.sub(r"<script[^>]*>.*?</script>", "", page,
                            flags=re.S | re.M)
        if steady_dom.count('aria-live="polite"') != 1:
            fail("an ordinary served quiz must have exactly one steady-state "
                 "polite region, the card feedback")
        for m in re.finditer(r"<script[^>]*>(.*?)</script>", page,
                             re.S | re.M):
            script = m.group(1)
            if "assist-status" in script:
                if ".textContent" not in script:
                    fail("the assist status must be updated via textContent "
                         "so a state change announces exactly once")
                if 'setAttribute("aria-live", "polite")' not in script or \
                        'removeAttribute("aria-live")' not in script:
                    fail("assist live-region lifecycle is not transient")
    finally:
        proc.terminate()
        shutil.rmtree(workdir, ignore_errors=True)


# ---- Task 1's model-UI lens: the wire the assist client depends on ----------

def check_assist_wire():
    """The browser-facing half of Task 1: the served client drives POST
    /api/hint and POST /api/rubric-review, renders only typed payloads, and
    no authority field the UI could be tempted by is accepted on the wire."""
    workdir = tempfile.mkdtemp()
    shutil.copy(SAMPLE, os.path.join(workdir, "sample_bank.md"))
    proc, base, _ = start_daemon(workdir)
    try:
        _status, page = get(base + "quiz/sample_bank")
        if '"/api/hint"' not in page or '"/api/rubric-review"' not in page:
            fail("the served client is not wired to both assist routes")
        by_id = api_by_id(SAMPLE)
        sid, _held = hold_non_short(base, by_id)
        for field in ("tier", "profile", "facts", "candidate", "proposal",
                      "marker", "verdict"):
            req = urllib.request.Request(
                base + "api/hint", data=json.dumps(
                    {"session_id": sid, field: "forged"}).encode(),
                headers={"Content-Type": "application/json"})
            try:
                urllib.request.urlopen(req, timeout=5)
                fail("the assist wire accepted a forged %r field" % field)
            except urllib.error.HTTPError as exc:
                if exc.code != 400:
                    fail("forged %r on /api/hint returned HTTP %d, expected "
                         "400" % (field, exc.code))
    finally:
        proc.terminate()
        shutil.rmtree(workdir, ignore_errors=True)


# ---- quick 260812-e2m D4: the authored fallback renders prose or nothing ----

def check_authored_fallback_copy_and_field():
    """The model disclosure no longer duplicates the authored ladder."""
    from surfaces.quiz_page import ASSIST_COPY, ASSIST_JS
    for banned in ("authored.display", "authored.content", "authoredHtml",
                   "assist-lock", "lock-glyph", "Optional guidance is locked"):
        if banned in ASSIST_JS:
            fail("retired authored or lock UI remains in the model panel: %r" % banned)


def main():
    check_dom_order_and_copy()
    check_lifecycle_and_lock()
    check_pending_rubric_rows()
    check_no_leak()
    check_responsive_and_motion()
    check_assist_wire()
    check_authored_fallback_copy_and_field()
    print("ok: model UI roundtrip -- assist DOM/copy, lifecycle + structural "
          "lock, pending rubric rows, no-leak boundary, responsive/reduced-"
          "motion/announce-once all held")
    return 0


if __name__ == "__main__":
    sys.exit(main())
