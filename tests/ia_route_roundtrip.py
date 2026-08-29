#!/usr/bin/env python3
"""Assert that Phase 16B's information-architecture routes are one row in the
shipped route tables and one read model in `surfaces/ia.py`, and never a
second router, a second dispatch mechanism, or a write path over the journal.

The failure this guards against is a new page that looks right in a browser
while having been added outside the four parallel route structures: such a
route has no CLI twin, no parity row, and no place in the token gate's
inventory, and it fails nowhere until something else needs the inventory to be
true. Every check below asserts on bytes that crossed a socket, or on the
route tables themselves, rather than on an in-process render.

The Activity area asserted here means durable agent and maintenance jobs. It
is a different object from `REQUIREMENTS.md`'s `ACTIVITY-01/02/03` family of
purpose-first learner questions; they share a word and not a schema
(Decision D6).

Standard library only, no test framework, runnable as
`python tests/ia_route_roundtrip.py`.
"""
import hashlib, html, inspect, io, json, os, random, re, shutil
import subprocess, sys, tempfile
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import itembank                                             # noqa: E402
from surfaces import daemon, ia                             # noqa: E402
sys.path.insert(0, os.path.join(ROOT, "fixtures"))          # noqa: E402
import course_storyboard_corpus as corpus                   # noqa: E402
import graph                                                # noqa: E402
import sample_course                                        # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from daemon_roundtrip import start_daemon, get, json_request  # noqa: E402,F401

BANK = os.path.join(ROOT, "fixtures", "sample_bank.md")


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def suppress_sample_course(workdir):
    """Record the bundled sample course as already removed.

    Plan 16B-09 makes `GET /` materialize the sample course on first launch,
    which would add a third card to fixtures that are asserting on two. The
    checks that exist to prove first launch do not call this; every check that
    predates it does, so each keeps asserting the thing it was written for.
    """
    ia.write_ia_state(workdir, "sample_course", {"removed": True})
    return workdir


def temp_dir_with_bank():
    workdir = tempfile.mkdtemp(prefix="ia_route_")
    shutil.copy(BANK, os.path.join(workdir, "sample_bank.md"))
    return suppress_sample_course(workdir)


def check_activity_route_end_to_end():
    """The phase tracer: a real daemon on a real port answers GET /activity
    with a page built by `surfaces/ia.py`'s read model."""
    workdir = temp_dir_with_bank()
    proc, url, lines = start_daemon(workdir)
    try:
        status, body = get(url + "activity")
        if status != 200:
            fail("GET /activity returned %d, expected 200" % status)
        if "<h1>Activity</h1>" not in body:
            fail("GET /activity did not render the Activity heading")
        if "Back to courses" not in body:
            fail("GET /activity did not render the back link")
        marker = 'data-ia-state="'
        pos = 0
        while True:
            start = body.find(marker, pos)
            if start < 0:
                break
            start += len(marker)
            end = body.find('"', start)
            found = body[start:end]
            if found not in ia.ACTIVITY_JOB_STATES:
                fail("data-ia-state carried %r, which is not an "
                     "ACTIVITY_JOB_STATES member" % found)
            pos = end
        pos = 0
        while True:
            start = body.find("<h3>", pos)
            if start < 0:
                break
            end = body.find("</h3>", start)
            if "%" in body[start:end]:
                fail("an Activity job heading carried a percent character")
            pos = end
    finally:
        proc.terminate()
        proc.wait(timeout=5)
        shutil.rmtree(workdir, ignore_errors=True)


class _FakeJournal(object):
    """An explicit synthetic stand-in for `journal.py`, named as a stand-in so
    no reader mistakes it for the real module. It exists so every Activity job
    state can be driven deterministically; the real `journal.py` is exercised
    by `check_activity_route_end_to_end`, which serves a live daemon.
    """

    ENTRY_STATES = ("prepared", "applied", "refused")

    def __init__(self, entries, object_states=None):
        self._entries = entries
        self._object_states = object_states or {}

    def entries(self, root):
        return list(self._entries)

    def object_state(self, root, object_id):
        return self._object_states.get(object_id, "clean")


def _fake_journal(entries, object_states=None):
    return _FakeJournal(entries, object_states)


class _CapturingHandler(object):
    """The smallest object `daemon.handle_activity_get` needs. Capturing the
    bytes the shipped handler sends is the point: this drives the real
    renderer rather than a second copy of it."""

    def __init__(self, root):
        self.root = root
        self.sent = b""

    def send_html(self, payload, status=200):
        self.sent = payload


def _render_activity(state, root):
    """Render `state` through the shipped `handle_activity_get`."""
    original = ia.activity_view_state
    ia.activity_view_state = lambda _root, journal=None: state
    try:
        handler = _CapturingHandler(root)
        daemon.handle_activity_get(handler)
        return handler.sent.decode("utf-8")
    finally:
        ia.activity_view_state = original


def _prepared(entry_id, **extra):
    entry = {"entry_id": entry_id, "timestamp": "2026-08-28T00:00:00Z",
             "state": "prepared", "operation": "import",
             "object_id": "obj-" + entry_id, "kind": "lesson",
             "path": "/private/roots/course/chapter one.md"}
    entry.update(extra)
    return entry


def _resolver(entry_id, resolves, state, **extra):
    entry = {"entry_id": entry_id, "timestamp": "2026-08-28T00:00:01Z",
             "state": state, "resolves_entry": resolves,
             "object_id": "obj-" + resolves, "kind": "lesson"}
    entry.update(extra)
    return entry


def _one(entries, object_states=None):
    state = ia.activity_view_state(".", journal=_fake_journal(entries,
                                                              object_states))
    if len(state["jobs"]) != 1:
        fail("expected exactly one job, got %d" % len(state["jobs"]))
    return state["jobs"][0]


def check_activity_unavailable_state():
    """The not-yet-available branch, proven both in-process and served."""
    state = ia.activity_view_state(".", journal=None)
    if state["available"] is not False:
        fail("activity_view_state(journal=None) reported available")
    if state["code"] != "ia.activity_unavailable":
        fail("the unavailable branch carried code %r" % state["code"])
    expected = ("Activity isn't available yet in this build. Check back "
                "after your next update.")
    if state["notice"] != expected:
        fail("the unavailable notice was %r" % state["notice"])
    if state["needs_input"] != [] or state["jobs"] != []:
        fail("the unavailable branch carried jobs")

    workdir = temp_dir_with_bank()
    os.environ["ITEMBANK_IA_NO_JOURNAL"] = "1"
    try:
        proc, url, lines = start_daemon(workdir)
        try:
            status, body = get(url + "activity")
            if status != 200:
                fail("the unavailable Activity page returned %d" % status)
            # The page escapes the notice's apostrophe, which is correct;
            # the comparison unescapes rather than weakening the escaping.
            if expected not in html.unescape(body):
                fail("the served unavailable page did not carry the notice")
            if 'href="/help/ia.activity_unavailable"' not in body:
                fail("the served unavailable page did not link its help code")
        finally:
            proc.terminate()
            proc.wait(timeout=5)
    finally:
        os.environ.pop("ITEMBANK_IA_NO_JOURNAL", None)
        shutil.rmtree(workdir, ignore_errors=True)


def check_activity_job_states():
    """Every ACTIVITY_JOB_STATES member except unavailable, each asserting its
    exact locked label and its exact token name."""
    produced = []

    job = _one([_prepared("e1")])
    produced.append(job)
    if job["state"] != "needs_input" or job["label"] != "Needs your input" \
            or job["token"] != "pending":
        fail("the needs_input case produced %r" % job)

    job = _one([_prepared("e2", step=2)])
    produced.append(job)
    if job["label"] != "In progress: no estimate.":
        fail("the in_progress_no_estimate case produced %r" % job["label"])
    if "%" in job["label"]:
        fail("in_progress_no_estimate carried a percent character")

    job = _one([_prepared("e3", step=2, steps_total=5,
                          stage="Binding sources")])
    produced.append(job)
    if job["label"] != "Step 2 of 5: Binding sources":
        fail("the in_progress_known case produced %r" % job["label"])

    job = _one([_prepared("e4"), _resolver("r4", "e4", "applied")])
    produced.append(job)
    if job["label"] != "Completed" or job["token"] != "ok":
        fail("the completed case produced %r" % job)

    job = _one([_prepared("e5"),
                _resolver("r5", "e5", "refused", reason="rights not granted")])
    produced.append(job)
    if job["label"] != "Failed: rights not granted" or job["token"] != "bad":
        fail("the failed case produced %r" % job)

    job = _one([_prepared("e6"),
                _resolver("r6", "e6", "refused", cancelled=True)])
    produced.append(job)
    if job["label"] != ("Cancelled. Partial results are marked below and were "
                        "not saved as final.") or job["token"] != "warn":
        fail("the cancelled case produced %r" % job)

    job = _one([_prepared("e7")], {"obj-e7": "interrupted"})
    produced.append(job)
    if job["label"] != "Interrupted: resume available." \
            or job["token"] != "warn":
        fail("the interrupted case produced %r" % job)

    for job in produced:
        if "%" in job["label"]:
            fail("a job label carried a percent character: %r" % job["label"])

    empty = ia.activity_view_state(".", journal=_fake_journal([]))
    if empty["jobs"] != [] or empty["needs_input"] != []:
        fail("zero entries did not produce an empty Activity state")
    page = _render_activity(empty, ".")
    if "Needs your input" in page:
        fail("the zero-jobs page rendered a Needs your input section header")

    one = ia.activity_view_state(".", journal=_fake_journal([_prepared("z1")]))
    three = ia.activity_view_state(
        ".", journal=_fake_journal([_prepared("z1"), _prepared("z2"),
                                    _prepared("z3")]))
    if _render_activity(one, ".").count('<article class="job"') != 1:
        fail("one job did not render through one job article")
    if _render_activity(three, ".").count('<article class="job"') != 3:
        fail("three jobs did not render through three job articles")

    tied = ia.activity_view_state(".", journal=_fake_journal(
        [_prepared("c1"), _prepared("a1"), _prepared("b1")]))
    order = [job["entry_id"] for job in tied["jobs"]]
    if order != ["a1", "b1", "c1"]:
        fail("tied timestamps were not broken by entry_id ascending: %r"
             % order)

    newest = ia.activity_view_state(".", journal=_fake_journal(
        [_prepared("old", timestamp="2026-08-01T00:00:00Z"),
         _prepared("new", timestamp="2026-08-27T00:00:00Z")]))
    if [job["entry_id"] for job in newest["jobs"]] != ["new", "old"]:
        fail("jobs were not ordered newest timestamp first")


def check_activity_no_write_path():
    """The read model mutates nothing it is given, survives a malformed entry,
    and never carries a journal payload out to a page."""
    entries = [_prepared("m1", before_image="SECRET-BEFORE-IMAGE"),
               "not a dict"]
    before = json.dumps(entries, sort_keys=True)
    state = ia.activity_view_state(".", journal=_fake_journal(entries))
    if json.dumps(entries, sort_keys=True) != before:
        fail("activity_view_state mutated the entries it was given")

    malformed = [job for job in state["jobs"]
                 if job["label"] == "Failed: unreadable journal entry"]
    if len(malformed) != 1:
        fail("a malformed entry did not produce one unreadable-entry job")
    if malformed[0]["state"] != "failed":
        fail("the unreadable-entry job was not in the failed state")

    for job in state["jobs"]:
        if "SECRET-BEFORE-IMAGE" in json.dumps(job):
            fail("a journal before-image reached a job dict")
    if "SECRET-BEFORE-IMAGE" in _render_activity(state, "."):
        fail("a journal before-image reached a rendered page")

    for job in state["jobs"]:
        if set(job) != set(ia.JOB_KEYS):
            fail("a job carried keys outside the metadata allowlist: %r"
                 % sorted(job))

    intents = [job["intent"] for job in state["jobs"]]
    if any("/" in intent or "\\" in intent for intent in intents):
        fail("a resolved path reached a job intent: %r" % intents)


def check_route_order_is_load_bearing():
    """The fixed-literal-before-stem-parameterised ordering rule, asserted."""
    literals = [i for i, e in enumerate(daemon.ROUTES)
                if isinstance(e[1], str)]
    patterns = [i for i, e in enumerate(daemon.ROUTES)
                if not isinstance(e[1], str)]
    activity = daemon.ROUTES.index(("GET", "/activity", "handle_activity_get"))
    if patterns and activity > min(patterns):
        fail("a new fixed-literal route was appended after the "
             "stem-parameterised block")
    if literals and patterns and max(literals) > min(patterns):
        fail("the fixed-literal-before-stem-parameterised ordering rule was "
             "broken")
    if set(daemon.ROUTE_CLI) != set(e[:2] for e in daemon.ROUTES):
        fail("ROUTE_CLI's key set does not match ROUTES")


def check_one_dispatcher():
    """One dispatcher, never a second router beside it."""
    src = inspect.getsource(daemon)
    if src.count("def _dispatch") != 1:
        fail("a second dispatch mechanism appeared beside "
             "DaemonHandler._dispatch")


NETWORK_MARKERS = ("import urllib", "import http.client", "import socket",
                   "import requests", "from urllib", "urlopen",
                   "model_adapter")


def _scan_for_network(text):
    """Every networking or model-module marker present in `text`, with whole
    comment lines stripped first so a comment naming a module cannot
    invalidate the scan."""
    body = re.sub(r"^\s*#.*$", "", text, flags=re.M)
    return [marker for marker in NETWORK_MARKERS if marker in body]


def check_help_table_shape():
    """Twelve codes, each with a cause and a next safe action, plus a sentence
    for the codes nobody wrote an entry for."""
    entry = ia.help_entry("ia.activity_unavailable")
    if set(entry) != {"code", "title", "cause", "next_action", "known"}:
        fail("help_entry returned the key set %r" % sorted(entry))
    if entry["known"] is not True:
        fail("a known code was reported unknown")

    unknown = ia.help_entry("ia.not_a_real_code")
    if set(unknown) != set(entry):
        fail("the unknown shape carried a different key set")
    if unknown["known"] is not False:
        fail("an unknown code was reported known")
    if unknown["cause"] != ia.HELP_FALLBACK_COPY or unknown["next_action"] != "":
        fail("the unknown entry carried %r" % unknown)

    for bad in ("", None, 0):
        try:
            shape = ia.help_entry(bad)
        except Exception as exc:
            fail("help_entry(%r) raised %s" % (bad, exc))
        if shape["known"] is not False:
            fail("help_entry(%r) reported known" % bad)

    if sorted(ia.HELP_TABLE) != list(ia.IA_HELP_CODES):
        fail("HELP_TABLE is not exactly IA_HELP_CODES, sorted and unique")
    for code, row in ia.HELP_TABLE.items():
        if set(row) != {"title", "cause", "next_action"}:
            fail("%s carried the key set %r" % (code, sorted(row)))
        if not row["cause"].strip() or not row["next_action"].strip():
            fail("%s carried an empty cause or next_action" % code)

    if ia.HELP_FALLBACK_COPY != "No additional help is available for this yet.":
        fail("HELP_FALLBACK_COPY was %r" % ia.HELP_FALLBACK_COPY)

    if ia.HELP_TABLE["ia.offline"]["cause"] != (
            "You're offline. Reading, practice, scoring, hints, and evidence "
            "keep working. Anything that needs a network connection is marked "
            "unavailable below."):
        fail("the ia.offline cause is not the Degraded-State Matrix copy")
    if ia.HELP_TABLE["ia.disk_full"]["cause"] != (
            "This save could not complete (disk full or interrupted). Your "
            "previous version is intact. Free up space and try again."):
        fail("the ia.disk_full cause is not the Degraded-State Matrix copy")

    for state in ia.DEGRADED_STATES:
        code = "ia.crash_recovered" if state == "crash" else "ia." + state
        if code not in ia.IA_HELP_CODES:
            fail("degraded state %r has no help code %r" % (state, code))


def check_help_route_bijection():
    """Each of the twelve codes routes to exactly one page, and each page names
    exactly one code."""
    workdir = temp_dir_with_bank()
    proc, url, lines = start_daemon(workdir)
    try:
        reached = set()
        for code in ia.IA_HELP_CODES:
            status, body = get(url + "help/" + code)
            if status != 200:
                fail("GET /help/%s returned %d" % (code, status))
            plain = html.unescape(body)
            if ia.HELP_TABLE[code]["cause"] not in plain:
                fail("GET /help/%s did not carry its cause sentence" % code)
            marker = "Error code: "
            named = [line for line in plain.split("<")
                     if marker in line]
            codes_named = set()
            for chunk in named:
                tail = chunk.split(marker, 1)[1]
                codes_named.add(tail.split("<")[0].strip())
            if codes_named != {code}:
                fail("GET /help/%s named the codes %r" % (code, codes_named))
            reached.add(code)
        if reached != set(ia.IA_HELP_CODES):
            fail("the route reached %r, not every IA_HELP_CODES member"
                 % sorted(reached))
    finally:
        proc.terminate()
        proc.wait(timeout=5)
        shutil.rmtree(workdir, ignore_errors=True)


def check_help_unknown_code():
    """An unknown code is a sentence; a malformed one is a path-free 404."""
    workdir = temp_dir_with_bank()
    proc, url, lines = start_daemon(workdir)
    try:
        status, body = get(url + "help/ia.no_such_code")
        if status != 200:
            fail("an unknown help code returned %d, expected 200" % status)
        if ia.HELP_FALLBACK_COPY not in html.unescape(body):
            fail("an unknown help code did not carry the fallback sentence")

        for path in ("help/UPPERCASE", "help/..%2fetc%2fpasswd", "help/a/b"):
            status, body = json_request(url + path, method="GET")
            if status != 404:
                fail("GET /%s returned %d, expected 404" % (path, status))
            text = body if isinstance(body, str) else json.dumps(body)
            if "Traceback" in text:
                fail("a 404 body carried a traceback")
            if (os.sep * 2) in text or "/etc/" in text:
                fail("a 404 body carried a filesystem path")
    finally:
        proc.terminate()
        proc.wait(timeout=5)
        shutil.rmtree(workdir, ignore_errors=True)


def check_help_is_offline():
    """Help resolves with no network, no proxy, and no configured backend,
    proven structurally and behaviourally, because neither way is enough."""
    if _scan_for_network("import socket") == []:
        fail("the network scan cannot fail, so it proves nothing")

    source = io.open(os.path.join(ROOT, "surfaces", "ia.py"),
                     encoding="utf-8").read()
    found = _scan_for_network(source)
    if found:
        fail("surfaces/ia.py reached for a networking or model module: %s"
             % ", ".join(found))

    workdir = temp_dir_with_bank()
    # The schema has no `model_backend` key with a "none" member. Its own way
    # of saying no backend is configured is an empty `model.active`, which is
    # also the shipped default, so it is written explicitly rather than left
    # implicit.
    with io.open(os.path.join(workdir, "itembank.json"), "w",
                 encoding="utf-8") as fh:
        fh.write(json.dumps({"model": {"active": "", "profiles": []}}))
    env = dict(os.environ)
    env["ITEMBANK_NO_NETWORK"] = "1"
    for name in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY",
                 "http_proxy", "https_proxy", "all_proxy"):
        env.pop(name, None)
    saved = dict(os.environ)
    os.environ.clear()
    os.environ.update(env)
    try:
        proc, url, lines = start_daemon(workdir)
        try:
            status, body = get(url + "help/ia.offline")
            if status != 200:
                fail("offline help returned %d with no backend configured"
                     % status)
            if ia.HELP_TABLE["ia.offline"]["cause"] not in html.unescape(body):
                fail("offline help did not carry its exact cause sentence")
        finally:
            proc.terminate()
            proc.wait(timeout=5)
    finally:
        os.environ.clear()
        os.environ.update(saved)
        shutil.rmtree(workdir, ignore_errors=True)


def _no_percent(cards, where):
    for card in cards:
        for field in ("chip", "resume_cue", "cta_label"):
            if "%" in card[field]:
                fail("%s: card %s carried a percent in %s: %r"
                     % (where, card["course_id"], field, card[field]))


def check_shelf_state_shape():
    """The module-absent branch, the empty state, the two healthy cards, and
    the corrupted card's two ways forward."""
    absent = ia.course_shelf_state(".", course=None)
    if absent["available"] is not False or absent["cards"] != []:
        fail("the module-absent shelf branch returned %r" % absent)
    if absent["empty_heading"] != "No courses yet":
        fail("the empty heading was %r" % absent["empty_heading"])
    if absent["empty_body"] != ("Start with the sample course, or bind a "
                                "source to create your first course."):
        fail("the empty body was %r" % absent["empty_body"])

    workdir = suppress_sample_course(tempfile.mkdtemp(prefix="ia_shelf_"))
    try:
        empty_mod = corpus.FakeCourseModule({})
        state = ia.course_shelf_state(workdir, course=empty_mod)
        if state["available"] is not True or state["cards"] != []:
            fail("a zero-record shelf returned %r" % state)

        module, dirs = corpus.build_two_course_shelf(workdir)
        state = ia.course_shelf_state(workdir, course=module)
        if len(state["cards"]) != 2:
            fail("the two-course shelf rendered %d cards"
                 % len(state["cards"]))
        labels = [card["cta_label"] for card in state["cards"]]
        if labels != ["Resume Kestrel County Field Basics",
                      "Start Mirefield Numeracy"]:
            fail("the two-course CTAs were %r" % labels)
        _no_percent(state["cards"], "two-course shelf")
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def check_shelf_ordering_is_total():
    """Ten rebuilds over a shuffled input produce one identical sequence, and
    two equal cards are ordered by course id."""
    workdir = suppress_sample_course(tempfile.mkdtemp(prefix="ia_order_"))
    try:
        records = {r["course_id"]: dict(r) for r in corpus.FICTIONAL_COURSES}
        sequences = set()
        for _ in range(10):
            order = list(records)
            random.Random(20260815).shuffle(order)
            shuffled = {key: records[key] for key in order}
            module = corpus.FakeCourseModule(shuffled)
            for course_id in shuffled:
                path = os.path.join(workdir, course_id)
                os.makedirs(path, exist_ok=True)
                open(os.path.join(path, module.COURSE_SIDECAR_FILENAME),
                     "w").close()
            state = ia.course_shelf_state(workdir, course=module)
            sequences.add(tuple(c["course_id"] for c in state["cards"]))
        if len(sequences) != 1:
            fail("ten rebuilds produced %d different orders: %r"
                 % (len(sequences), sequences))
        _no_percent(state["cards"], "ordering")
    finally:
        shutil.rmtree(workdir, ignore_errors=True)

    twins = suppress_sample_course(tempfile.mkdtemp(prefix="ia_twins_"))
    try:
        module, dirs = corpus.build_same_name_pair(twins)
        state = ia.course_shelf_state(twins, course=module)
        ids = [card["course_id"] for card in state["cards"]]
        names = {card["name"] for card in state["cards"]}
        if ids != ["crs-twin-a", "crs-twin-b"]:
            fail("the course-id tiebreak produced %r" % ids)
        if len(ids) != 2 or len(names) != 1:
            fail("two same-named courses were merged: %r %r" % (ids, names))
        _no_percent(state["cards"], "same-name pair")
    finally:
        shutil.rmtree(twins, ignore_errors=True)


def check_shelf_corrupted_course():
    """APP-01's fixture in process: one healthy card beside one degraded one,
    the degraded one built from the basename and offering two ways forward."""
    workdir = suppress_sample_course(tempfile.mkdtemp(prefix="ia_corrupt_"))
    try:
        module, dirs = corpus.build_corrupted_course(workdir)
        state = ia.course_shelf_state(workdir, course=module)
        if len(state["cards"]) != 2:
            fail("the corrupted fixture rendered %d cards"
                 % len(state["cards"]))
        degraded = [c for c in state["cards"] if c["degraded"]]
        healthy = [c for c in state["cards"] if not c["degraded"]]
        if len(degraded) != 1 or len(healthy) != 1:
            fail("expected one healthy and one degraded card, got %d and %d"
                 % (len(healthy), len(degraded)))
        card = degraded[0]
        if card["chip"] != "Showing last valid overview":
            fail("the degraded chip was %r" % card["chip"])
        if [a["label"] for a in card["actions"]] != [
                "Open last valid overview", "View files"]:
            fail("the degraded actions were %r" % list(card["actions"]))
        if card["name"] != "crs-mirefield-02":
            fail("the degraded card name was %r" % card["name"])
        if os.sep in card["name"] or "/" in card["name"]:
            fail("a resolved path reached the degraded card name")
        if card["help_code"] != "ia.course_corrupted":
            fail("the degraded card help code was %r" % card["help_code"])
        _no_percent(state["cards"], "corrupted fixture")
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def check_shelf_end_to_end():
    """APP-01's fixture served by a real daemon against the real course.py."""
    workdir = suppress_sample_course(tempfile.mkdtemp(prefix="ia_shelf_e2e_"))
    proc = None
    try:
        corpus.build_corrupted_course(workdir)
        proc, url, lines = start_daemon(workdir)
        status, body = get(url)
        if status != 200:
            fail("GET / returned %d with courses present" % status)
        if body.count('class="course-card"') != 2:
            fail("GET / rendered %d course cards, expected 2"
                 % body.count('class="course-card"'))
        plain = html.unescape(body)
        # The landed 14B course record carries no resume cue at all, so the
        # real module yields the Start form rather than the Resume form. The
        # Resume form is proved against the stand-in by
        # check_shelf_state_shape; fabricating it here would assert a cue
        # nothing recorded.
        if "Start Kestrel County Field Basics" not in plain:
            fail("the healthy course's CTA was absent from the served shelf")
        for needle in ("Showing last valid overview",
                       "Open last valid overview", "View files"):
            if needle not in plain:
                fail("the degraded course string %r was absent" % needle)
        # Identity is the pinned course_object_id the sidecar names, never the
        # folder name (FILE-03). The degraded card is the one exception: its
        # record would not read, so it is keyed by basename and says so.
        healthy_id = "crskestrel010000"
        if ('data-course-id="%s"' % healthy_id) not in body:
            fail("the healthy card was not keyed by its pinned object id")
        if 'data-course-id="crs-kestrel-01"' in body:
            fail("the healthy card was keyed by its folder name")
        if 'data-course-id="crs-mirefield-02"' not in body:
            fail("the degraded card was not keyed by its basename")
        for tag, closer in (('<span class="chip">', "</span>"),
                            ('<p class="resume-cue">', "</p>")):
            pos = 0
            while True:
                start = body.find(tag, pos)
                if start < 0:
                    break
                end = body.find(closer, start)
                if "%" in body[start + len(tag):end]:
                    fail("a percent character appeared inside %s" % tag)
                pos = end
        for banned in ("Next page", "Previous page", "page="):
            if banned in body:
                fail("a pagination affordance %r appeared on the shelf"
                     % banned)
    finally:
        if proc is not None:
            proc.terminate()
            proc.wait(timeout=5)
        shutil.rmtree(workdir, ignore_errors=True)


def check_shelf_falls_back_to_bank_index():
    """No course means the shipped listing, and no course and no bank means the
    shelf's own empty state."""
    workdir = temp_dir_with_bank()
    saved = dict(os.environ)
    os.environ["ITEMBANK_IA_NO_COURSE"] = "1"
    try:
        proc, url, lines = start_daemon(workdir)
        try:
            status, body = get(url)
            if status != 200:
                fail("the bank-index fallback returned %d" % status)
            if 'class="course-card"' in body:
                fail("a course card rendered with the course module absent")
            if "sample_bank" not in body:
                fail("the shipped bank listing did not render")
        finally:
            proc.terminate()
            proc.wait(timeout=5)
    finally:
        os.environ.clear()
        os.environ.update(saved)
        shutil.rmtree(workdir, ignore_errors=True)

    # With no course and no bank, D1 keeps the shipped empty-state page rather
    # than substituting the shelf's own empty copy. Four shipped tests assert
    # that heading, and D1's own key link forbids replacing a shipped surface
    # to add a new one. The shelf's empty copy is therefore asserted on the
    # read model, which is where it is actually reachable.
    bare = suppress_sample_course(tempfile.mkdtemp(prefix="ia_bare_"))
    try:
        state = ia.course_shelf_state(bare)
        if state["cards"]:
            fail("a bare directory produced course cards")
        if state["empty_heading"] != "No courses yet":
            fail("the empty shelf heading was %r" % state["empty_heading"])
        if state["empty_body"] != ("Start with the sample course, or bind a "
                                   "source to create your first course."):
            fail("the empty shelf body was %r" % state["empty_body"])
        proc, url, lines = start_daemon(bare)
        try:
            status, body = get(url)
            if status != 200:
                fail("the empty index returned %d" % status)
            if "Nothing to serve here yet" not in body:
                fail("D1's shipped empty-state heading was replaced")
            if 'class="course-card"' in body:
                fail("a course card rendered on an empty index")
        finally:
            proc.terminate()
            proc.wait(timeout=5)
    finally:
        shutil.rmtree(bare, ignore_errors=True)


PAGINATION_MARKERS = ("Next page", "Previous page", "page=", 'rel="next"',
                      'rel="prev"')

NAMED_AREAS = ("learn", "practice", "test", "map", "sources", "build",
               "evidence")


def _shelf_course_ids(workdir):
    """The pinned course ids the real module reports for a fixture directory.

    Identity is the sidecar's own `course_object_id`, not the folder name, so
    a test that hard-coded the folder name would be asserting the name-based
    identity FILE-03 forbids.
    """
    state = ia.course_shelf_state(workdir)
    return [card["course_id"] for card in state["cards"]]


def check_course_areas_all_render():
    """All eight areas addressable, Notes and Search deliberately not, and an
    unresolvable course a path-free 404."""
    workdir = suppress_sample_course(tempfile.mkdtemp(prefix="ia_areas_"))
    proc = None
    try:
        corpus.build_two_course_shelf(workdir)
        course_id = _shelf_course_ids(workdir)[0]
        proc, url, lines = start_daemon(workdir)

        labels = [ia.COURSE_AREA_LABELS[a] for a in ia.COURSE_AREAS]

        status, body = get(url + "course/" + course_id)
        if status != 200:
            fail("GET /course/<id> returned %d" % status)
        if "Back to courses" not in html.unescape(body):
            fail("the Overview frame lost its back control")
        for label in labels:
            if label not in html.unescape(body):
                fail("Overview's nav omitted %r" % label)

        for area in NAMED_AREAS:
            status, body = get(url + "course/%s/%s" % (course_id, area))
            plain = html.unescape(body)
            if status != 200:
                fail("GET /course/<id>/%s returned %d" % (area, status))
            if ia.COURSE_AREA_LABELS[area] not in plain:
                fail("the %s area did not carry its own label" % area)
            if "Back to " not in plain:
                fail("the %s area lost its back control" % area)
            for label in labels:
                if label not in plain:
                    fail("the %s area's nav omitted %r" % (area, label))

        for banned, why in (("notes", "D4"), ("search", "D5")):
            status, body = json_request(
                url + "course/%s/%s" % (course_id, banned), method="GET")
            if status != 404:
                fail("/%s returned %d, expected 404 per %s"
                     % (banned, status, why))

        status, body = json_request(url + "course/no-such-course",
                                    method="GET")
        text = body if isinstance(body, str) else json.dumps(body)
        if status != 404:
            fail("an unknown course returned %d, expected 404" % status)
        if "Traceback" in text or (os.sep * 2) in text:
            fail("the unknown-course 404 carried a traceback or a path")
    finally:
        if proc is not None:
            proc.terminate()
            proc.wait(timeout=5)
        shutil.rmtree(workdir, ignore_errors=True)


def check_same_routes_both_widths():
    """One route per object at every width, and one back control."""
    workdir = suppress_sample_course(tempfile.mkdtemp(prefix="ia_widths_"))
    proc = None
    try:
        corpus.build_two_course_shelf(workdir)
        course_id = _shelf_course_ids(workdir)[0]
        proc, url, lines = start_daemon(workdir)

        paths = ["/course/" + course_id]
        paths += ["/course/%s/%s" % (course_id, a) for a in NAMED_AREAS]

        for path in paths:
            matches = [e for e in daemon.ROUTES
                       if e[0] == "GET" and (
                           path == e[1] if isinstance(e[1], str)
                           else e[1].match(path))]
            if len(matches) != 1:
                fail("%s matched %d ROUTES entries, expected exactly 1"
                     % (path, len(matches)))

            wide_status, wide = json_request(url + path.lstrip("/"),
                                             method="GET")
            narrow_status, narrow = json_request(
                url + path.lstrip("/"), method="GET",
                headers={"Sec-CH-Viewport-Width": "360",
                         "Viewport-Width": "360"})
            if wide_status != 200 or narrow_status != 200:
                fail("%s returned %d and %d at the two widths"
                     % (path, wide_status, narrow_status))

            def back_href(text):
                marker = '<p class="back"><a href="'
                start = text.find(marker)
                if start < 0:
                    fail("%s rendered no back control" % path)
                start += len(marker)
                return text[start:text.find('"', start)]

            if back_href(wide) != back_href(narrow):
                fail("%s served two different back hrefs by width" % path)
    finally:
        if proc is not None:
            proc.terminate()
            proc.wait(timeout=5)
        shutil.rmtree(workdir, ignore_errors=True)


def check_no_pagination_on_reading():
    """Nothing a reader reads paginates."""
    for banned in ("history.back", "fetch(", "XMLHttpRequest",
                   "document.write", "innerHTML ="):
        if banned in daemon.RESTORE_SCRIPT:
            fail("RESTORE_SCRIPT carried the banned construct %r" % banned)

    workdir = suppress_sample_course(tempfile.mkdtemp(prefix="ia_nopage_"))
    proc = None
    try:
        corpus.build_two_course_shelf(workdir)
        course_id = _shelf_course_ids(workdir)[0]
        proc, url, lines = start_daemon(workdir)
        paths = ["", "course/" + course_id]
        paths += ["course/%s/%s" % (course_id, a) for a in NAMED_AREAS]
        for path in paths:
            request = urllib.request.Request(url + path)
            with urllib.request.urlopen(request, timeout=5) as res:
                body = res.read().decode("utf-8")
                link = res.headers.get("Link") or ""
            for banned in PAGINATION_MARKERS:
                if banned in body:
                    fail("/%s carried the pagination marker %r"
                         % (path, banned))
            if "rel=next" in link.replace('"', "").replace(" ", ""):
                fail("/%s carried a Link header with rel=next" % path)

            if path.startswith("course/"):
                plain = html.unescape(body)
                if "data-anchor-missing" not in body:
                    fail("/%s rendered no anchor-missing region" % path)
                if "hidden" not in body:
                    fail("/%s did not hide the anchor-missing region" % path)
                if ia.ANCHOR_NOT_FOUND_NOTICE not in plain:
                    fail("/%s did not carry the anchor-missing notice" % path)
                if daemon.COURSE_NOSCRIPT not in plain:
                    fail("/%s did not carry the noscript sentence" % path)
    finally:
        if proc is not None:
            proc.terminate()
            proc.wait(timeout=5)
        shutil.rmtree(workdir, ignore_errors=True)


def check_deep_link_scenarios():
    """The three APP-02 scenarios the edge-coverage probe left unresolved."""
    # Scenario a: deep-link stability under rename or move.
    workdir = suppress_sample_course(tempfile.mkdtemp(prefix="ia_deeplink_a_"))
    try:
        module, dirs = corpus.build_two_course_shelf(workdir)
        record = module.records["crs-kestrel-01"]
        before = ia.deep_link_target("crs-kestrel-01", "learn",
                                     course_name=record["name"])
        moved_parent = os.path.join(workdir, "moved")
        os.makedirs(moved_parent, exist_ok=True)
        shutil.move(dirs[0], os.path.join(moved_parent, "crs-kestrel-01"))
        record["name"] = "Kestrel Field Skills"
        after = ia.deep_link_target("crs-kestrel-01", "learn",
                                    course_name=record["name"])
        if after["path"] != before["path"]:
            fail("a rename and a move changed the deep link path: %r to %r"
                 % (before["path"], after["path"]))
        if after["back_label"] != "Back to Kestrel Field Skills":
            fail("the back label did not follow the rename: %r"
                 % after["back_label"])
        for key, value in after.items():
            if isinstance(value, str) and "Kestrel County Field Basics" in value:
                fail("the old name survived in %s: %r" % (key, value))
    finally:
        shutil.rmtree(workdir, ignore_errors=True)

    # Scenario b: an anchor into deleted content keeps its page; only an
    # unknown area is a route failure.
    workdir = suppress_sample_course(tempfile.mkdtemp(prefix="ia_deeplink_b_"))
    proc = None
    try:
        corpus.build_two_course_shelf(workdir)
        course_id = _shelf_course_ids(workdir)[0]
        proc, url, lines = start_daemon(workdir)

        # A fragment is never sent to the server, so the same path is
        # requested and the client-side branch is what the region serves.
        status, body = get(url + "course/%s/learn" % course_id)
        plain = html.unescape(body)
        if status != 200:
            fail("an area with a dead anchor returned %d" % status)
        for label in ia.COURSE_AREA_LABELS.values():
            if label not in plain:
                fail("the dead-anchor page lost the nav label %r" % label)
        if "Back to " not in plain:
            fail("the dead-anchor page lost its back control")
        if ia.ANCHOR_NOT_FOUND_NOTICE not in plain:
            fail("the dead-anchor page carried no anchor-missing region")
        if body.count('href="/help/ia.route_not_found"') != 0:
            fail("a resolved route linked the route-not-found help page")

        # An unrecognized area segment never reaches a handler: D-16B-1's
        # closed alternation refuses it at dispatch, which is the stronger
        # property. It is a 404 with no handler run and so no help link.
        status, body = json_request(url + "course/%s/nosucharea" % course_id,
                                    method="GET")
        text = body if isinstance(body, str) else json.dumps(body)
        if status != 404:
            fail("an unknown area returned %d, expected 404" % status)
        if "Traceback" in text:
            fail("the unknown-area 404 carried a traceback")

        # The route-failure half of the distinction is the case that does
        # reach a handler: a well-formed path naming a course that does not
        # exist. That 404 links the one page explaining the state.
        status, body = json_request(url + "course/no-such-course/learn",
                                    method="GET")
        text = body if isinstance(body, str) else json.dumps(body)
        if status != 404:
            fail("an unknown course area returned %d, expected 404" % status)
        if 'href="/help/ia.route_not_found"' not in text:
            fail("the unknown-course 404 did not link its help page")
    finally:
        if proc is not None:
            proc.terminate()
            proc.wait(timeout=5)
        shutil.rmtree(workdir, ignore_errors=True)

    # Scenario c: a real fallback focus target when the anchor is gone. The
    # server-side half is what a Python suite can prove; the browser half is
    # recorded as a backstop in 16B-05-SUMMARY.md rather than claimed here.
    workdir = suppress_sample_course(tempfile.mkdtemp(prefix="ia_deeplink_c_"))
    proc = None
    try:
        corpus.build_two_course_shelf(workdir)
        course_id = _shelf_course_ids(workdir)[0]
        proc, url, lines = start_daemon(workdir)
        status, body = get(url + "course/%s/learn" % course_id)
        expected_id = ia.anchor_slug(ia.COURSE_AREA_LABELS["learn"])
        if ('id="%s"' % expected_id) not in body:
            fail("the area heading carried no anchor_slug id")
        for needle in ("document.getElementById", "querySelector(\"h1\")",
                       "[data-anchor-missing]"):
            if needle not in daemon.RESTORE_SCRIPT:
                fail("RESTORE_SCRIPT lacks the fallback branch %r" % needle)

        state = ia.course_area_state(workdir, course_id, "learn")
        if state["found"] is not True:
            fail("an existing course area reported not found")
        target = ia.deep_link_target(course_id, "learn", anchor="gone")
        if target["anchor"] != ia.anchor_slug("gone"):
            fail("a stale anchor was passed through raw: %r"
                 % target["anchor"])
    finally:
        if proc is not None:
            proc.terminate()
            proc.wait(timeout=5)
        shutil.rmtree(workdir, ignore_errors=True)


def _post_shelf(url, payload, headers=None):
    return json_request(url + "api/shelf", payload, headers=headers)


def check_sample_course_suffix():
    """The bundled course is obviously synthetic, is made of fixed bytes, and
    lints clean."""
    if not sample_course.SAMPLE_COURSE_NAME.endswith("(Sample)"):
        fail("the sample course name lost its suffix: %r"
             % sample_course.SAMPLE_COURSE_NAME)

    workdir = tempfile.mkdtemp(prefix="ia_sample_")
    try:
        dest = os.path.join(workdir, sample_course.SAMPLE_COURSE_DIRNAME)
        first = sample_course.write_sample_course(dest)
        if len(first) != 3:
            fail("write_sample_course wrote %d files, expected 3" % len(first))
        if first != sorted(first):
            fail("write_sample_course did not return sorted paths")
        for path in first:
            if not os.path.abspath(path).startswith(os.path.abspath(dest)):
                fail("write_sample_course wrote outside its destination: %r"
                     % path)

        before = {path: hashlib.sha256(open(path, "rb").read()).hexdigest()
                  for path in first}
        second = sample_course.write_sample_course(dest)
        if second != first:
            fail("a second materialization wrote a different file set")
        for path in second:
            digest = hashlib.sha256(open(path, "rb").read()).hexdigest()
            if digest != before[path]:
                fail("re-materializing %s produced different bytes"
                     % os.path.basename(path))

        bank = [p for p in first if p.endswith("study_skills_sample.md")][0]
        result = subprocess.run(
            [sys.executable, os.path.join(ROOT, "itembank.py"), "lint", bank],
            capture_output=True, text=True)
        if result.returncode != 0:
            fail("the materialized sample bank does not lint clean: %s"
                 % (result.stdout + result.stderr))

        state = ia.course_shelf_state(workdir)
        cards = [c for c in state["cards"]
                 if c["course_id"] == sample_course.SAMPLE_COURSE_ID]
        if len(cards) != 1:
            fail("the sample course did not render exactly one card")
        card = cards[0]
        if not card["name"].endswith("(Sample)"):
            fail("the shelf card dropped the suffix: %r" % card["name"])
        if "(Sample)" not in card["cta_label"]:
            fail("the CTA dropped the suffix: %r" % card["cta_label"])

        # APP-03 adjacency: a real course with the same base name stays a
        # separate card with a different name string.
        real = os.path.join(workdir, "real-study-skills")
        os.makedirs(real)
        with io.open(os.path.join(real, "course-graph.md"), "w",
                     encoding="utf-8") as fh:
            fh.write(graph.serialize_course(
                graph.new_course("Study Skills Basics", "realstudyskill01")))
        state = ia.course_shelf_state(workdir)
        names = [c["name"] for c in state["cards"]]
        if len(state["cards"]) != 2:
            fail("the adjacent real course did not render its own card")
        if len(set(names)) != 2:
            fail("the sample and the real course collapsed to one name: %r"
                 % names)
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def check_ia_state_is_atomic():
    """First-run state survives a fault mid-write and a corrupted record."""
    workdir = tempfile.mkdtemp(prefix="ia_state_")
    try:
        fresh = ia.read_ia_state(workdir, "walkthrough")
        if fresh != {"status": "unseen", "step": 0}:
            fail("a fresh root did not read the walkthrough default: %r"
                 % fresh)
        if os.path.exists(os.path.join(workdir, ia.IA_STATE_DIR)):
            fail("reading state created a file")

        ia.write_ia_state(workdir, "walkthrough",
                          {"status": "in_progress", "step": 2})
        if ia.read_ia_state(workdir, "walkthrough") != {
                "status": "in_progress", "step": 2}:
            fail("a written state did not read back")

        directory = os.path.join(workdir, ia.IA_STATE_DIR)
        leftovers = [f for f in os.listdir(directory) if f.endswith(".tmp")]
        if leftovers:
            fail("a temporary file survived a successful write: %r"
                 % leftovers)

        with io.open(os.path.join(directory, "walkthrough.json"), "w",
                     encoding="utf-8") as fh:
            fh.write('{"status":')
        truncated = ia.read_ia_state(workdir, "walkthrough")
        if truncated != {"status": "unseen", "step": 0}:
            fail("a truncated record did not read as the default: %r"
                 % truncated)

        try:
            ia.apply_shelf_action(workdir, "not_an_action")
        except ValueError as exc:
            if "not_an_action" not in str(exc):
                fail("the unknown-action error did not name it: %s" % exc)
        else:
            fail("an unknown shelf action was accepted")

        dest = os.path.join(workdir, sample_course.SAMPLE_COURSE_DIRNAME)
        sample_course.write_sample_course(dest)
        first = ia.apply_shelf_action(workdir, "remove_sample_course")
        if first["ok"] is not True or os.path.isdir(dest):
            fail("remove_sample_course did not remove the directory")
        second = ia.apply_shelf_action(workdir, "remove_sample_course")
        if second["ok"] is not True:
            fail("a repeated removal reported failure")
        if second["message"] != ("The sample course was already removed. "
                                 "Nothing to do."):
            fail("a repeated removal said %r" % second["message"])

        # Scan the code, not the docstring: the docstring legitimately uses
        # the word "request" to explain the guarantee being asserted.
        source = inspect.getsource(ia.apply_shelf_action)
        body = re.sub(r'"""[\s\S]*?"""', "", source, count=1)
        body = re.sub(r"^\s*#.*$", "", body, flags=re.M)
        if "SAMPLE_COURSE_DIRNAME" not in body:
            fail("apply_shelf_action does not derive its deletion path from "
                 "the fixed sample-course directory name")
        joins = re.findall(r"os\.path\.join\(([^)]*)\)", body)
        for call in joins:
            args = [a.strip() for a in call.split(",")]
            if args[0] != "root":
                fail("apply_shelf_action joined a path onto %r, not root"
                     % args[0])
            for arg in args[1:]:
                if arg not in ("sample_course.SAMPLE_COURSE_DIRNAME",
                               "IA_STATE_DIR"):
                    fail("apply_shelf_action joined the non-constant segment "
                         "%r into a path it may delete" % arg)
        for banned in ("data.get", "handler", "shutil.rmtree"):
            if banned in body:
                fail("apply_shelf_action reads a request-supplied value or "
                     "deletes a tree: %r" % banned)
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def check_shelf_action_allowed_fields():
    """One route, one allowed field, four allowed actions, loopback only."""
    workdir = tempfile.mkdtemp(prefix="ia_shelf_route_")
    proc = None
    try:
        proc, url, lines = start_daemon(workdir)

        status, body = _post_shelf(url, {"action": "skip_walkthrough"})
        if status != 200:
            fail("a valid shelf action returned %d" % status)
        if ia.read_ia_state(workdir, "walkthrough")["status"] != "skipped":
            fail("skip_walkthrough did not record the skipped status")

        status, body = _post_shelf(
            url, {"action": "skip_walkthrough", "path": "/etc"})
        text = body if isinstance(body, str) else json.dumps(body)
        if status != 400:
            fail("an unlisted field returned %d, expected 400" % status)
        if "body may carry only: action" not in text:
            fail("the unlisted-field refusal did not name the allowed field")

        status, body = _post_shelf(url, {"action": "rm -rf"})
        text = body if isinstance(body, str) else json.dumps(body)
        if status != 400:
            fail("an unknown action returned %d, expected 400" % status)
        for action in ia.SHELF_ACTIONS:
            if action not in text:
                fail("the unknown-action refusal did not name %r" % action)

        status, body = _post_shelf(url, {"action": "skip_walkthrough"},
                                   headers={"Origin": "http://evil.example"})
        if status != 403:
            fail("a cross-origin shelf write returned %d, expected 403"
                 % status)

        status, body = json_request(url + "api/shelf", method="GET")
        if status != 404:
            fail("GET /api/shelf returned %d, expected 404" % status)
    finally:
        if proc is not None:
            proc.terminate()
            proc.wait(timeout=5)
        shutil.rmtree(workdir, ignore_errors=True)


def check_first_launch_offline():
    """A fresh install with nothing configured and no network reaches a real
    course page."""
    workdir = tempfile.mkdtemp(prefix="ia_first_launch_")
    saved = dict(os.environ)
    os.environ["ITEMBANK_NO_NETWORK"] = "1"
    for name in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY",
                 "http_proxy", "https_proxy", "all_proxy"):
        os.environ.pop(name, None)
    proc = None
    try:
        proc, url, lines = start_daemon(workdir)
        status, body = get(url)
        plain = html.unescape(body)
        if status != 200:
            fail("first launch returned %d" % status)
        for needle in ("Study Skills Basics (Sample)",
                       "For exploring itembank. Remove it anytime.",
                       "New here? A short walkthrough shows how a course "
                       "works.",
                       "Start walkthrough", "Skip for now",
                       "Replay walkthrough"):
            if needle not in plain:
                fail("first launch omitted %r" % needle)
        if 'class="course-card"' not in body:
            fail("the walkthrough offer replaced or blocked the shelf")

        status, _ = get(url + "course/" + sample_course.SAMPLE_COURSE_ID)
        if status != 200:
            fail("the sample course page returned %d with nothing configured"
                 % status)

        status, body = get(url + "help/ia.offline")
        if status != 200:
            fail("offline help returned %d on a fresh install" % status)
        if ia.HELP_TABLE["ia.offline"]["cause"] not in html.unescape(body):
            fail("offline help carried no cause sentence on a fresh install")
    finally:
        if proc is not None:
            proc.terminate()
            proc.wait(timeout=5)
        os.environ.clear()
        os.environ.update(saved)
        shutil.rmtree(workdir, ignore_errors=True)

    result = subprocess.run(
        [sys.executable, os.path.join(ROOT, "itembank.py"), "guard", ROOT],
        capture_output=True, text=True)
    if result.returncode != 0 or "0 offending files" not in result.stdout:
        fail("guard is no longer clean after a temp materialization: %s"
             % (result.stdout + result.stderr))


def check_walkthrough_interruption():
    """Walkthrough position survives a process death, skip and replay both
    work, and removal is idempotent."""
    workdir = tempfile.mkdtemp(prefix="ia_interrupt_")
    proc = None
    try:
        proc, url, lines = start_daemon(workdir)
        # First launch is what materializes the sample course, so the shelf is
        # requested before any course-level path is.
        status, _ = get(url)
        if status != 200:
            fail("first launch returned %d" % status)
        for _ in range(2):
            status, _ = _post_shelf(url, {"action": "advance_walkthrough"})
            if status != 200:
                fail("advance_walkthrough returned %d" % status)

        stored = json.load(io.open(
            os.path.join(workdir, ia.IA_STATE_DIR, "walkthrough.json"),
            encoding="utf-8"))
        if stored != {"status": "in_progress", "step": 2}:
            fail("the walkthrough record on disk is %r" % stored)

        # Every other area stayed reachable while the walkthrough was open.
        for path in ("course/%s/learn" % sample_course.SAMPLE_COURSE_ID,
                     "activity"):
            status, _ = get(url + path)
            if status != 200:
                fail("/%s returned %d during the walkthrough" % (path, status))

        # Kill the process without a clean shutdown.
        proc.kill()
        proc.wait(timeout=5)
        proc = None

        proc, url, lines = start_daemon(workdir)
        status, body = get(url)
        plain = html.unescape(body)
        if ia.WALKTHROUGH_STEPS[2]["title"] not in plain:
            fail("the walkthrough did not resume at step 2 after a process "
                 "death; position was not written atomically to disk")

        status, _ = _post_shelf(url, {"action": "skip_walkthrough"})
        status, body = get(url)
        plain = html.unescape(body)
        if ia.WALKTHROUGH_COPY["offer"] in plain:
            fail("the offer survived a skip")
        if ia.WALKTHROUGH_COPY["replay"] not in plain:
            fail("the replay control disappeared after a skip")

        status, _ = _post_shelf(url, {"action": "replay_walkthrough"})
        if ia.read_ia_state(workdir, "walkthrough") != {
                "status": "in_progress", "step": 0}:
            fail("replay_walkthrough did not return to step 0")

        status, body = _post_shelf(url, {"action": "remove_sample_course"})
        if status != 200:
            fail("remove_sample_course returned %d" % status)
        if os.path.isdir(os.path.join(
                workdir, sample_course.SAMPLE_COURSE_DIRNAME)):
            fail("the sample course directory survived its removal")
        status, body = get(url)
        if sample_course.SAMPLE_COURSE_NAME in html.unescape(body):
            fail("the removed sample course still renders a card")

        status, body = _post_shelf(url, {"action": "remove_sample_course"})
        text = body if isinstance(body, str) else json.dumps(body)
        if status != 200:
            fail("a repeated removal returned %d, expected 200" % status)
        if ("The sample course was already removed. Nothing to do."
                not in text):
            fail("a repeated removal did not state the no-op: %s" % text)
    finally:
        if proc is not None:
            proc.terminate()
            proc.wait(timeout=5)
        shutil.rmtree(workdir, ignore_errors=True)


CHECKS = (check_activity_route_end_to_end,
          check_activity_unavailable_state,
          check_activity_job_states,
          check_activity_no_write_path,
          check_route_order_is_load_bearing,
          check_one_dispatcher,
          check_help_table_shape,
          check_help_route_bijection,
          check_help_unknown_code,
          check_help_is_offline,
          check_shelf_state_shape,
          check_shelf_ordering_is_total,
          check_shelf_corrupted_course,
          check_shelf_end_to_end,
          check_shelf_falls_back_to_bank_index,
          check_course_areas_all_render,
          check_same_routes_both_widths,
          check_no_pagination_on_reading,
          check_deep_link_scenarios,
          check_sample_course_suffix,
          check_ia_state_is_atomic,
          check_shelf_action_allowed_fields,
          check_first_launch_offline,
          check_walkthrough_interruption)


def main():
    for check in CHECKS:
        check()
    print("IA ROUTES: %d passed, 0 failed" % len(CHECKS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
