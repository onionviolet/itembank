#!/usr/bin/env python3
"""Assert that `itembank serve` scores in the process, writes answers to disk,
and that the served page is a client of the canonical `/api/*` JSON session
API (SURF-02) -- no key, no scoring implementation, and no full bank item
array in the served source.

Two regressions guarded here, both of which fail silently in the worst way.

First, persistence: the static `build` page cannot save anything, so a sitting
used to vanish with the tab. If the write half breaks, the person believes their
work was recorded when it was not.

Second, answer leakage: the served page must never carry the key or a
client-side scorer. If that breaks nothing looks wrong, because the quiz still
works. It just becomes a page that hands over the answers to anyone who opens
the source, which disqualifies every surface an agent or a second person
touches.

Since plan 01-10, the attempt file itself is `evidence.render_attempt_md()`'s
output, a view over `_evidence/evidence.jsonl` rather than a second store, and
its "MARK:" / "[auto: ...]" text reflects that render's own vocabulary.

Standard library only, no test framework, runnable as
`python tests/serve_roundtrip.py`.
"""
import json, os, re, shutil, subprocess, sys, tempfile, threading, time
import urllib.error, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import evidence                                            # noqa: E402
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


def post(url, payload):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=5) as res:
        return json.loads(res.read().decode("utf-8"))


# ---- served-page contract helpers ------------------------------------------

def served_boot(page):
    """The served page's bootstrap metadata object (`const BOOT = {...};`)."""
    m = re.search(r"(?m)^const BOOT = (\{.*?\});$", page)
    if not m:
        fail("served page carries no BOOT bootstrap metadata")
    return json.loads(m.group(1))


def served_items(page):
    """The item payload the page was actually given -- empty for served mode,
    which receives items one at a time from the API.
    """
    m = re.search(r"(?m)^const Q = (\[.*\]);$", page)
    return json.loads(m.group(1)) if m else []


def check_served_boot(page, qs, stem, mode):
    """Test 1: the served shell's boot data carries the allowlisted bank stem,
    the item count, and the configured session mode -- nothing else.
    """
    boot = served_boot(page)
    if boot.get("bank") != stem:
        fail("served boot bank is %r, expected %r" % (boot.get("bank"), stem))
    if boot.get("count") != len(qs):
        fail("served boot count is %r, expected %d" % (boot.get("count"), len(qs)))
    if boot.get("mode") != mode:
        fail("served boot mode is %r, expected %r" % (boot.get("mode"), mode))


def check_no_key(page, qs):
    """Test 1 + 5: the served page has no full item array and no
    canonicalization/scoring implementation; the static page has both.
    """
    items = served_items(page)
    if items:
        fail("served page carries %d full items; boot metadata only is allowed"
             % len(items))
    for banned in ("function canon(", "function grade(", "q.correct.includes",
                   "same(picked", "q.key", "q.explain"):
        if banned in page:
            fail("served page references %r; the process is the only scorer" % banned)
    # Nothing from the answer half of the bank may appear anywhere in the
    # source, not only inside the payload.
    for q in qs:
        if q["type"] == "short" and q.get("model") and q["model"] in page:
            fail("served page contains the model answer for %s" % q["id"])
        if q.get("why") and q["why"] in page:
            fail("served page contains the WHY BEST text for %s" % q["id"])
    if "function installDraft(" not in page:
        fail("the served page does not ship the draft installer")


def check_served_page_js(page, stem):
    """Test 2 + 6: the new browser flow starts and submits through the
    canonical API, renders a loading/checking status, keeps a Retry path for
    API failure, and never references the legacy bank-scoped answer route.
    """
    for needle in ('"/api/start"', '"/api/submit"',
                   "Loading", "Checking answer", "Try again"):
        if needle not in page:
            fail("served page is missing %r" % needle)
    if 'fetch("/quiz/%s/answer"' % stem in page:
        fail("the new browser flow still references the legacy bank-scoped "
             "answer route")


def check_static_offline(page, qs):
    """Test 5: the static `build` compatibility path still carries the full
    Python-produced key/explanation array and its offline canonical-key
    comparison -- that implementation belongs only to the static page.
    """
    items = served_items(page)
    if len(items) != len(qs):
        fail("static page carries %d items, bank has %d" % (len(items), len(qs)))
    for item in items:
        if "key" not in item or "explain" not in item:
            fail("static item %s is missing the offline key/explanation"
                 % item.get("id"))
    for needle in ("function canon(", "q.key"):
        if needle not in page:
            fail("static page lost its offline canonical-key comparison (%r)"
                 % needle)


# ---- canonical API flow helpers ---------------------------------------------

def api_start(base, bank, count, mode, focus=None):
    payload = {"bank": bank, "count": count, "mode": mode}
    if focus:
        payload["focus"] = focus
    return post(base + "api/start", payload)


def api_submit(base, session_id, answer):
    return post(base + "api/submit",
                {"session_id": session_id, "answer": answer})


def form_fields_for(q, answer):
    """The urlencoded field list `_form_controls` renders for this item type,
    carrying `answer` -- the browser's own vocabulary, not the JSON API's."""
    if q["type"] == "mc":
        return [("option", answer)]
    if q["type"] == "multi":
        return [("option", k) for k in answer]
    if q["type"] in ("table", "dnd"):
        return [("row_%s" % n, v) for n, v in sorted(answer.items(), key=lambda kv: int(kv[0]))]
    if q["type"] == "build":
        return [("step_%d" % n, v) for n, v in enumerate(answer)]
    return [("answer", answer)]


def check_form_submit_writes_the_attempt_file():
    """A script-free `serve` sitting writes the attempt markdown the banner
    promises.

    It never did. `_refresh_attempt_view` was reachable only from the JSON
    `/api/submit` route, so the browser form branch recorded evidence and
    returned its redirect with the configured `--out` file untouched. The
    banner printed a path that stayed absent for the whole sitting, and
    13.9-03's verify step asked for a file the served path could not produce.
    Found 2026-08-24 after the 13.9 sitting; the typed prose was safe in
    `evidence.jsonl`, so this was a missing second copy rather than data loss.

    Driven through the real served bytes (GET the page, read its own token and
    item id, POST the form) because a suite of green tests agreed with a broken
    served page all night on 2026-08-24.
    """
    qs = itembank.parse_bank(open(BANK, encoding="utf-8").read())
    by_id = dict((q["id"], q) for q in qs)
    work_root = tempfile.mkdtemp(prefix="serve-form-")
    bank = os.path.join(work_root, "sample_bank.md")
    shutil.copyfile(BANK, bank)
    out = os.path.join(tempfile.mkdtemp(), "attempt.md")
    proc = subprocess.Popen(
        [sys.executable, "-u", os.path.join(ROOT, "itembank.py"), "serve", bank,
         "--no-open", "--port", "0", "--out", out],
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
        fail("serve never printed a URL. Output was:\n" + "".join(lines))
    quiz_url = base + "quiz/sample_bank"
    try:
        page = urllib.request.urlopen(quiz_url, timeout=5).read().decode("utf-8")
        item_id = re.search(r'data-item-id="([^"]+)"', page)
        token = re.search(r'name="form_token" value="([^"]+)">'
                          r'<input type="hidden" name="action" value="submit"', page)
        if not item_id or not token:
            fail("the served baseline carried no item id or no submit token")
        q = by_id[item_id.group(1)]
        if os.path.exists(out):
            fail("the attempt file existed before any answer was given")
        fields = form_fields_for(q, correct_answer(q))
        fields.append(("form_token", token.group(1)))
        fields.append(("action", "submit"))
        req = urllib.request.Request(
            quiz_url + "/answer", data=urllib.parse.urlencode(fields).encode(),
            method="POST",
            headers={"Content-Type": "application/x-www-form-urlencoded"})
        with urllib.request.urlopen(req, timeout=5) as res:
            res.read()
    finally:
        proc.terminate()
    if not os.path.exists(out):
        fail("a form submit wrote no attempt file at %s" % out)
    text = open(out, encoding="utf-8").read()
    if q["stem"].split("\n")[0][:40] not in text:
        fail("the attempt file does not carry the item that was answered")
    print("  a script-free form submit refreshed the attempt view at %s" % out)


def check_banner_id_is_the_evidence_id():
    """The id `itembank serve` prints in its banner must be the id every
    evidence row of that sitting carries, and the id inside the session file
    the daemon creates under the hood.

    Found 2026-08-24: the banner minted one id in `cmd_serve`, but
    `_ensure_quiz_session` minted a second, independent id for the actual
    session file the first API request created. A marker who copied the
    printed banner id into `itembank mark` would find no matching evidence.
    """
    qs = itembank.parse_bank(open(BANK, encoding="utf-8").read())
    by_id = dict((q["id"], q) for q in qs)
    work_root = tempfile.mkdtemp(prefix="serve-banner-")
    bank = os.path.join(work_root, "sample_bank.md")
    shutil.copyfile(BANK, bank)
    out = os.path.join(tempfile.mkdtemp(), "attempt.md")
    proc = subprocess.Popen(
        [sys.executable, "-u", os.path.join(ROOT, "itembank.py"), "serve", bank,
         "--no-open", "--port", "0", "--out", out],
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
        fail("serve never printed a URL. Output was:\n" + "".join(lines))
    banner_m = re.search(r"session ([0-9a-f]{32})", "".join(lines))
    if not banner_m:
        fail("serve never printed a banner session id. Output was:\n" +
             "".join(lines))
    banner_id = banner_m.group(1)
    quiz_url = base + "quiz/sample_bank"
    try:
        page = urllib.request.urlopen(quiz_url, timeout=5).read().decode("utf-8")
        item_id = re.search(r'data-item-id="([^"]+)"', page)
        token = re.search(r'name="form_token" value="([^"]+)">'
                          r'<input type="hidden" name="action" value="submit"', page)
        if not item_id or not token:
            fail("the served baseline carried no item id or no submit token")
        q = by_id[item_id.group(1)]
        fields = form_fields_for(q, correct_answer(q))
        fields.append(("form_token", token.group(1)))
        fields.append(("action", "submit"))
        req = urllib.request.Request(
            quiz_url + "/answer", data=urllib.parse.urlencode(fields).encode(),
            method="POST",
            headers={"Content-Type": "application/x-www-form-urlencoded"})
        with urllib.request.urlopen(req, timeout=5) as res:
            res.read()
    finally:
        proc.terminate()
    log = evidence.log_path(work_root)
    if not os.path.exists(log):
        fail("no evidence log was written at %s" % log)
    ev_ids = set()
    for line in open(log, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        row = json.loads(line)
        if row.get("item_ref") == q["id"]:
            ev_ids.add(row.get("session_id"))
    for ev_id in ev_ids:
        if ev_id != banner_id:
            fail("the banner id %s is not the evidence id %s; the daemon "
                 "must honor the CLI-minted session id" % (banner_id, ev_id))
    if not ev_ids:
        fail("no evidence row carried the submitted item %s" % q["id"])
    session_files = [f for f in os.listdir(os.path.join(work_root, "_attempts"))
                     if f.startswith("session_") and f.endswith(".json")]
    if not session_files:
        fail("no session_*.json file was created under %s/_attempts" % work_root)
    for fname in session_files:
        sdata = json.load(open(os.path.join(work_root, "_attempts", fname),
                               encoding="utf-8"))
        if sdata.get("session_id") != banner_id:
            fail("the banner id %s is not the evidence id %s; the daemon "
                 "must honor the CLI-minted session id" %
                 (banner_id, sdata.get("session_id")))
    print("  the served banner id %s matches the evidence and session file"
         % banner_id)


def seed_serving_first(qs, want_type):
    """The lowest seed whose scoped-serve session opens on a `want_type` item.

    Built with the same `_ensure_quiz_session` the served page uses, so the
    order this returns is the order the browser will actually see.
    """
    from surfaces import daemon as daemon_mod

    class _Handler(object):
        pass

    with tempfile.TemporaryDirectory() as tmp:
        bank = os.path.join(tmp, "sample_bank.md")
        shutil.copyfile(BANK, bank)
        for seed in range(40):
            handler = _Handler()
            handler.root = tmp
            handler.sessions = {"sample_bank": {"mode": "practice",
                                                "progress": True, "seed": seed}}
            path = daemon_mod._ensure_quiz_session(handler, "sample_bank", bank, qs)
            with open(path, encoding="utf-8") as fh:
                first = json.load(fh)["items"][0]
            if qs[first]["type"] == want_type:
                return seed
    return None


def start_serve(bank, out, extra=()):
    """Boot `itembank serve` on an OS-assigned port; returns (proc, base_url)."""
    proc = subprocess.Popen(
        [sys.executable, "-u", os.path.join(ROOT, "itembank.py"), "serve", bank,
         "--no-open", "--port", "0", "--out", out] + list(extra),
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    lines = []
    threading.Thread(target=lambda: [lines.append(l) for l in proc.stdout],
                     daemon=True).start()
    for _ in range(60):
        time.sleep(0.1)
        m = re.search(r"http://127\.0\.0\.1:\d+/", "".join(lines))
        if m:
            return proc, m.group(0)
    proc.terminate()
    fail("serve never printed a URL. Output was:\n" + "".join(lines))


def submit_token(page):
    m = re.search(r'name="form_token" value="([^"]+)">'
                  r'<input type="hidden" name="action" value="submit"', page)
    return m.group(1) if m else None


def check_a_failed_submit_keeps_the_answer():
    """A submit that does not go through comes back carrying what was typed.

    On 2026-08-24 the 13.9 sitting wrote a constructed response, submitted it,
    and got `403 invalid or expired quiz form token` as a bare error document:
    no link, no retry, no echo. The prose was gone. The expired-token trigger
    is fixed separately (`QUIZ_TOKEN_TTL`), but a network blip, a server
    restart or a stray reload does exactly the same thing, so the class is
    what is pinned here.

    Two guarantees: the failing response still carries the failure status and
    the learner's own text, and the token is not spent by a failure, so the
    resubmit the page invites actually works.
    """
    qs = itembank.parse_bank(open(BANK, encoding="utf-8").read())
    seed = seed_serving_first(qs, "short")
    if seed is None:
        fail("no seed in 0..39 serves a constructed response first")
    work_root = tempfile.mkdtemp(prefix="serve-echo-")
    bank = os.path.join(work_root, "sample_bank.md")
    shutil.copyfile(BANK, bank)
    out = os.path.join(tempfile.mkdtemp(), "attempt.md")
    prose = "Scene safety first, then BSI, then a general impression of the patient."
    proc, base = start_serve(bank, out, ["--seed", str(seed)])
    quiz_url = base + "quiz/sample_bank"
    try:
        page = urllib.request.urlopen(quiz_url, timeout=5).read().decode("utf-8")
        if "<textarea" not in page:
            fail("seed %d did not serve a constructed response first" % seed)
        good = submit_token(page)
        if not good:
            fail("the served baseline minted no submit token")

        # A token that was never minted stands in for every way a submit can
        # fail after the answer is typed.
        body = urllib.parse.urlencode(
            {"form_token": "not-a-token", "action": "submit", "answer": prose}).encode()
        req = urllib.request.Request(
            quiz_url + "/answer", data=body, method="POST",
            headers={"Content-Type": "application/x-www-form-urlencoded"})
        try:
            urllib.request.urlopen(req, timeout=5)
            fail("an unminted quiz form token was accepted")
        except urllib.error.HTTPError as exc:
            if exc.code != 403:
                fail("a bad quiz token returned HTTP %d, expected 403" % exc.code)
            refused = exc.read().decode("utf-8")
        if prose not in refused:
            fail("the refused submit did not echo the learner's answer back")
        if "<textarea" not in refused:
            fail("the refused submit returned no usable page, only an error document")
        retry = submit_token(refused)
        if not retry:
            fail("the refused page offered no fresh token to resubmit with")

        # The failure must not have burned the token minted for this item.
        body = urllib.parse.urlencode(
            {"form_token": good, "action": "submit", "answer": prose}).encode()
        req = urllib.request.Request(
            quiz_url + "/answer", data=body, method="POST",
            headers={"Content-Type": "application/x-www-form-urlencoded"})
        with urllib.request.urlopen(req, timeout=5) as res:
            res.read()
    finally:
        proc.terminate()
    if not os.path.exists(out):
        fail("the resubmitted answer wrote no attempt file")
    if prose not in open(out, encoding="utf-8").read():
        fail("the resubmitted answer is not in the attempt record")
    print("  a refused submit returns 403 with the answer intact, and the "
          "token it did not spend still works")


def check_multi_hold_shows_which_of_my_picks_were_right():
    """The served page shows a held multiple-response attempt which of the
    learner's OWN picks were right, and nothing about the ones he did not pick.

    Weibao, USER-VISION 2026-08-24: "its just to rule out wrong answers and
    also show what I got right so I can keep on going rather than gambling."
    The runtime decides the disclosure (`FEEDBACK_POLICIES`); this pins that it
    reaches the script-free page a learner actually sits, and that the card
    stops where the policy stops.
    """
    qs = itembank.parse_bank(open(BANK, encoding="utf-8").read())
    by_id = dict((q["id"], q) for q in qs)
    seed = seed_serving_first(qs, "multi")
    if seed is None:
        fail("no seed in 0..39 serves a multiple-response item first")
    work_root = tempfile.mkdtemp(prefix="serve-multi-")
    bank = os.path.join(work_root, "sample_bank.md")
    shutil.copyfile(BANK, bank)
    out = os.path.join(tempfile.mkdtemp(), "attempt.md")
    proc, base = start_serve(bank, out, ["--seed", str(seed)])
    quiz_url = base + "quiz/sample_bank"
    try:
        page = urllib.request.urlopen(quiz_url, timeout=5).read().decode("utf-8")
        item_id = re.search(r'data-item-id="([^"]+)"', page).group(1)
        q = by_id[item_id]
        if q["type"] != "multi":
            fail("seed %d did not serve a multiple-response item first" % seed)
        keyed = list(q["correct"])
        unpicked = keyed[-1]
        decoy = next(k for k in sorted(q["opts"]) if k not in keyed)
        fields = [("option", keyed[0]), ("option", decoy),
                  ("form_token", submit_token(page)), ("action", "submit")]
        req = urllib.request.Request(
            quiz_url + "/answer", data=urllib.parse.urlencode(fields).encode(),
            method="POST",
            headers={"Content-Type": "application/x-www-form-urlencoded"})
        with urllib.request.urlopen(req, timeout=5) as res:
            held = res.read().decode("utf-8")
    finally:
        proc.terminate()
    card = re.search(r'<div class="picks" data-selection-feedback>(.*?)</div>\s*</div>',
                     held, re.S)
    if not card:
        fail("a held multi attempt showed no own-selection card")
    card = card.group(1)
    if ("%s)" % keyed[0]) not in card or ("%s)" % decoy) not in card:
        fail("the card did not name both of the learner's own picks: %r" % card)
    if "right" not in card or "not right" not in card:
        fail("the card marks its verdicts by colour alone, with no words")
    if ("%s)" % unpicked) in card or q["opts"][unpicked] in card:
        fail("the card named a keyed option the learner did not pick")
    if "Not correct" not in held:
        fail("a partially correct multi stopped being marked wrong as a whole")
    print("  a held multi attempt rules out the learner's own wrong pick "
          "without touching an option he did not choose")


def check_serve_seed_reaches_the_session():
    """`itembank serve --seed N` chooses the item order the sitting runs in.

    The daemon hardcoded `seed: 0` until 2026-08-24, so a scoped serve could
    not influence order at all. That is not cosmetic. A sitting parks on a
    constructed response until a marker rules on it, so a bank whose `short`
    item lands first under seed 0 ends at item one, which is exactly how the
    13.9 walking-skeleton sitting produced one response out of ten.

    Asserted through `_ensure_quiz_session`, the function that builds the
    selection spec, rather than by booting a server: the plumbing is the part
    that regressed, and it is the part worth pinning.
    """
    from surfaces import daemon as daemon_mod
    from surfaces import session as session_mod
    from model import load as load_bank

    class _Handler(object):
        pass

    with tempfile.TemporaryDirectory() as tmp:
        bank = os.path.join(tmp, "sample_bank.md")
        shutil.copyfile(BANK, bank)
        qs = load_bank(bank)

        def order_for(cfg):
            handler = _Handler()
            handler.root = tmp
            handler.sessions = {"sample_bank": dict(cfg)}
            path = daemon_mod._ensure_quiz_session(handler, "sample_bank", bank, qs)
            with open(path, encoding="utf-8") as fh:
                return json.load(fh)["items"]

        default = order_for({"mode": "practice", "progress": True})
        expect = order_for({"mode": "practice", "progress": True, "seed": 0})
        if default != expect:
            fail("serve without --seed must keep the seed-0 order it always "
                 "had: %r vs %r" % (default, expect))

        # A seed that reorders proves the value is consumed rather than
        # accepted and dropped. Scanning avoids pinning a specific shuffle,
        # which is selection's business and not this test's.
        moved = next((s for s in range(1, 40)
                      if order_for({"mode": "practice", "progress": True,
                                    "seed": s}) != default), None)
        if moved is None:
            fail("no seed in 1..39 changed the item order, so --seed is not "
                 "reaching the selection spec")
    print("  serve --seed reaches the session spec; default order unchanged")


def main():
    check_serve_seed_reaches_the_session()
    check_form_submit_writes_the_attempt_file()
    check_banner_id_is_the_evidence_id()
    check_a_failed_submit_keeps_the_answer()
    check_multi_hold_shows_which_of_my_picks_were_right()
    qs = itembank.parse_bank(open(BANK, encoding="utf-8").read())
    stem = os.path.splitext(os.path.basename(BANK))[0]
    # Isolate this test's bank (and its evidence log) from the shared
    # fixtures directory: other tests that drive the real fixtures bank
    # pollute `fixtures/_evidence/evidence.jsonl`, which used to make this
    # sitting's recorded-event count order-dependent.
    work_root = tempfile.mkdtemp()
    isolated_bank = os.path.join(work_root, "sample_bank.md")
    shutil.copyfile(BANK, isolated_bank)
    out = os.path.join(tempfile.mkdtemp(), "attempt.md")
    proc = subprocess.Popen(
        [sys.executable, "-u", os.path.join(ROOT, "itembank.py"), "serve", isolated_bank,
         "--no-open", "--port", "0", "--out", out],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    lines = []
    threading.Thread(target=lambda: [lines.append(l) for l in proc.stdout],
                     daemon=True).start()

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
        check_served_boot(page, qs, stem, "practice")
        check_no_key(page, qs)
        check_served_page_js(page, stem)

        # Test 2: the whole sitting runs over /api/start -> /api/submit.
        started = api_start(base, stem, len(qs), "practice")
        if started["status"] != "active":
            fail("POST /api/start did not return an active session")
        if "correct" in started["item"] or "explain" in started["item"]:
            fail("POST /api/start's item carries answer material")
        session_id = started["session_id"]
        by_id = dict((q["id"], q) for q in qs)

        view = started
        seen = 0
        wrong_done = False
        while True:
            q = by_id[view["item"]["id"]]
            if q["type"] == "short":
                # Phase 6: a constructed response stays pending for a human
                # marker and never advances the cursor -- record it and stop.
                got = api_submit(base, session_id, correct_answer(q))
                if got.get("action") != "defer_feedback" or got["score"] is not None:
                    fail("a pending short response must defer feedback with "
                         "score None: %r" % got)
                if got["evidence"]["status"] != "recorded":
                    fail("the short response was not recorded: %r" % got["evidence"])
                seen += 1
                break
            elif not wrong_done:
                # One deliberate wrong auto answer so the attempt view proves
                # it renders both verdicts (mirrors the legacy test).
                answer = wrong_answer(q)
                wrong_done = True
                got = api_submit(base, session_id, answer)
                if got["score"] is not False:
                    fail("item %s wrong submit scored %r, expected False"
                         % (q["id"], got["score"]))
                if got.get("action") != "hold":
                    fail("practice wrong submit must hold, got %r" % got.get("action"))
                if got["evidence"]["status"] != "recorded":
                    fail("the wrong response was not recorded: %r" % got["evidence"])
                seen += 1
                # The card holds; resubmit the same item correctly to advance.
                answer, want = correct_answer(q), True
            else:
                answer, want = correct_answer(q), True
            got = api_submit(base, session_id, answer)
            if got["score"] is not want:
                fail("item %s (%s) scored %r, expected %r"
                     % (q["id"], q["type"], got["score"], want))
            if got["action"] in ("advance", "complete") and "explain" not in got:
                fail("an advancing submit response carries no server-issued "
                     "explanation")
            if got["action"] not in ("advance", "complete") and "explain" in got:
                fail("a non-advancing submit response must not leak an "
                     "explanation")
            if got["evidence"]["status"] != "recorded":
                fail("submit response was not recorded exactly once: %r"
                     % got["evidence"])
            seen += 1
            if got["action"] == "complete":
                if "summary" not in got["next"]:
                    fail("final submit returned no completion summary")
                break
            if seen > len(qs) * 2:
                fail("the sitting did not complete within the expected submits")
            if "item" not in got["next"]:
                fail("submit %d returned no next item" % seen)
            view = got["next"]
        if not wrong_done:
            fail("the sitting never submitted a wrong auto answer")

        # Test 2: evidence recorded exactly once, under the API session id.
        log = evidence.log_path(work_root)
        recorded = [ev for ev in evidence.live_events(log)
                    if ev.get("event_type") == "response"
                    and ev.get("session_id") == session_id]
        # The sitting answers every item up to and including the pending
        # short one (which stalls the cursor): 5 auto answers, the deliberate
        # wrong answer held and retried on the first item, and the short
        # answer -- one event per genuine submit, 6 total.
        if len(recorded) != len(qs):
            fail("API sitting recorded %d response events, expected %d"
                 % (len(recorded), len(qs)))

        # Test 3: forged authority/path/verdict fields are rejected.
        for field in ("item_id", "score", "key", "explanation",
                      "bank_path", "out"):
            try:
                post(base + "api/submit", {"session_id": session_id,
                                           "answer": "A", field: "forged"})
                fail("api/submit accepted a forged %r field" % field)
            except urllib.error.HTTPError as exc:
                if exc.code != 400:
                    fail("forged %r returned HTTP %d, expected 400"
                         % (field, exc.code))

        # D-09 pin: /api/start accepts focus=<item id> and starts the sitting
        # there (the served analogue of the file client's #<id> fragment).
        # Run after the main sitting so it cannot disturb the tracked
        # api_session_id the attempt-file regeneration reads.
        last_id = qs[-1]["id"]
        pinned = api_start(base, stem, len(qs), "practice", focus=last_id)
        if pinned["item"]["id"] != last_id:
            fail("focus=%r did not pin that item first; got %r"
                 % (last_id, pinned["item"]["id"]))
    finally:
        proc.terminate()

    # Test 4: the configured attempt view refreshed atomically after API
    # submissions -- the response text and marker vocabulary are present.
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

    # Test 5: the static offline build keeps its keys and canonical comparison.
    build_out = os.path.join(tempfile.mkdtemp(), "quiz.html")
    result = subprocess.run(
        [sys.executable, os.path.join(ROOT, "itembank.py"), "build", BANK,
         build_out], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if result.returncode != 0:
        fail("itembank build failed: %s" % result.stdout)
    check_static_offline(open(build_out, encoding="utf-8").read(), qs)

    print("ok: serve scored %d items in-process via /api/start + /api/submit, "
          "recorded %d evidence events once, refreshed the attempt view at %s, "
          "and kept the static offline build green"
          % (len(qs), len(qs), out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
