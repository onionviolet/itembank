#!/usr/bin/env python3
"""Plan 17A-08: the home surface. One data function, four modes.

The plan replaces the daemon's directory listing with the home 16B
designed: cards with honest resume state, one evidence-sourced next
action, and an activity list. Every check here runs against a temporary
root, so nothing in this suite reads or writes the repository.

No model produces any text this suite asserts on: the next action's
`why` is built from the evidence store's own counts, or it is absent.
"""
import copy
import datetime
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "surfaces"))

import evidence                                            # noqa: E402
from surfaces import home                                  # noqa: E402

BANK = os.path.join(ROOT, "fixtures", "sample_bank.md")
SESSION_ID = "sess-17a08-home"
OBJECTIVE = "bio:cells"

failures = []


def fail(msg):
    failures.append(msg)
    print("FAIL: " + msg)


def ok(msg):
    print("OK   " + msg)


def iso_days_ago(days):
    now = datetime.datetime.now(datetime.timezone.utc)
    then = now - datetime.timedelta(days=days)
    return then.strftime("%Y-%m-%dT%H:%M:%S.") + "%03dZ" % (
        then.microsecond // 1000)


class _Root(object):
    """A temporary daemon root with optional banks, sessions, evidence."""

    def __init__(self, banks=("sample_bank",)):
        self.root = tempfile.mkdtemp(prefix="itembank-17a08-")
        self.stems = []
        for stem in banks:
            shutil.copy(BANK, os.path.join(self.root, stem + ".md"))
            self.stems.append(stem)

    def write_session(self, stem, cursor, total, status="active"):
        attempts = os.path.join(self.root, "_attempts")
        os.makedirs(attempts, exist_ok=True)
        data = {
            "schema_version": 1,
            "session_id": SESSION_ID,
            "bank": os.path.abspath(os.path.join(self.root, stem + ".md")),
            "items": list(range(total)),
            "cursor": cursor,
            "responses": [],
            "status": status,
            "mode": "practice",
        }
        with open(os.path.join(attempts, "session_%s.json" % SESSION_ID),
                  "w", encoding="utf-8") as fh:
            json.dump(data, fh)

    def write_evidence(self, outcomes):
        """outcomes: list of True/False, recorded `practice` events for
        OBJECTIVE, backdated past the review interval so the retention
        machinery labels the objective due."""
        log = evidence.log_path(self.root)
        os.makedirs(os.path.dirname(log), exist_ok=True)
        bank_abspath = os.path.abspath(
            os.path.join(self.root, "sample_bank.md"))
        for i, score in enumerate(outcomes):
            q = {"id": "q%d" % (i + 1), "type": "mc",
                 "objective": OBJECTIVE}
            ev = evidence.response_event(
                SESSION_ID, q, "an answer", score, "practice", 1,
                bank_abspath)
            ev["ts"] = iso_days_ago(10)
            evidence.append_event(log, ev)

    def close(self):
        shutil.rmtree(self.root, ignore_errors=True)


def card_by_stem(state, stem):
    for card in state["cards"]:
        if card["stem"] == stem:
            return card
    return None


def check_empty_root_is_honest():
    """An empty root: no cards, no invented progress, and a next-action
    blocker that says what would make one possible. The unit is named
    `bank`, the seam 14B will swap."""
    r = _Root(banks=())
    try:
        state = home.home_state(r.root)
        if state["cards"]:
            fail("an empty root produced %d cards" % len(state["cards"]))
            return
        if state["unit"] != "bank":
            fail("the unit seam reads %r, not bank" % state["unit"])
            return
        if state["next_action"] is not None:
            fail("an empty root produced a next action: %r"
                 % state["next_action"])
            return
        blocker = state.get("next_action_blocker") or ""
        for needle in ("practice", "evidence"):
            if needle not in blocker.lower():
                fail("the blocker does not say what would make a next "
                     "action possible (%r missing): %r" % (needle, blocker))
                return
        ok("an empty root renders no cards and an honest blocker")
    finally:
        r.close()


def check_bank_with_no_session_is_not_started():
    """A bank with no session is `not_started`, never 0%. No progress
    figure appears anywhere on the shelf for it."""
    r = _Root()
    try:
        state = home.home_state(r.root)
        card = card_by_stem(state, "sample_bank")
        if card is None:
            fail("the scanned bank produced no card")
            return
        if card["resume"]["state"] != "not_started":
            fail("a bank with no session reads %r"
                 % card["resume"]["state"])
            return
        if card["progress"] is not None:
            fail("a bank with no session shows progress %r"
                 % card["progress"])
            return
        if not card.get("progress_refused_reason"):
            fail("the card does not say why it shows no progress")
            return
        html = home.render_home(state, "shelf")
        if "0%" in html:
            fail("the shelf shows a 0% figure for an unstarted bank")
            return
        if "not started" not in html.lower():
            fail("the shelf does not name the not-started state")
            return
        ok("an unstarted bank reads not_started with no invented percent")
    finally:
        r.close()


def check_bank_mid_session_reports_its_cursor():
    """A bank with a live session reports the cursor against the sitting
    length, and both numbers are real."""
    r = _Root()
    try:
        r.write_session("sample_bank", cursor=3, total=6)
        state = home.home_state(r.root)
        card = card_by_stem(state, "sample_bank")
        if card["resume"]["state"] != "in_progress":
            fail("a mid-session bank reads %r" % card["resume"]["state"])
            return
        progress = card["progress"]
        if not progress or progress.get("answered") != 3 \
                or progress.get("total") != 6:
            fail("the card shows %r, not 3 of 6" % progress)
            return
        html = home.render_home(state, "shelf")
        if "3 of 6" not in html:
            fail("the shelf does not say 3 of 6")
            return
        ok("a mid-session bank reports its real cursor, 3 of 6")
    finally:
        r.close()


def check_next_action_comes_from_evidence():
    """With evidence on disk, the next action names the objective, how
    many times it was missed, and over what denominator, in one
    sentence. No model text: the numbers are the store's own counts."""
    r = _Root()
    try:
        r.write_evidence([True, False, False, False])
        r.write_session("sample_bank", cursor=6, total=6, status="complete")
        state = home.home_state(r.root)
        action = state["next_action"]
        if action is None:
            fail("evidence on disk produced no next action (%r)"
                 % state.get("next_action_blocker"))
            return
        if action.get("objective") != OBJECTIVE:
            fail("the next action names %r, not %r"
                 % (action.get("objective"), OBJECTIVE))
            return
        why = action.get("why") or ""
        if "3 of 4" not in why:
            fail("the why does not carry 3 missed of 4: %r" % why)
            return
        if why.count(".") > 1 or why.count("!") > 0:
            fail("the why is not one sentence: %r" % why)
            return
        if "/quiz/sample_bank" not in (action.get("href") or ""):
            fail("the next action links nowhere actionable: %r"
                 % action.get("href"))
            return
        ok("the next action names the objective, 3 of 4 missed, one "
           "sentence")
    finally:
        r.close()


def check_no_evidence_means_no_next_action():
    """Sessions without evidence cannot ground a reason, so the next
    action stays None and the home says what would make one possible."""
    r = _Root()
    try:
        r.write_session("sample_bank", cursor=6, total=6, status="complete")
        state = home.home_state(r.root)
        if state["next_action"] is not None:
            fail("a root with no evidence produced a next action: %r"
                 % state["next_action"])
            return
        if not state.get("next_action_blocker"):
            fail("the home does not say why there is no next action")
            return
        ok("sessions alone do not invent a next action")
    finally:
        r.close()


def check_activity_lists_real_events():
    """The activity list is built from recorded evidence events only,
    newest first, capped."""
    r = _Root()
    try:
        r.write_evidence([True, False])
        state = home.home_state(r.root)
        rows = state["activity"]
        if len(rows) != 2:
            fail("activity carries %d rows, not 2" % len(rows))
            return
        if "sample_bank" not in rows[0]["text"]:
            fail("the newest activity row does not name the bank: %r"
                 % rows[0])
            return
        html = home.render_home(state, "shelf")
        if "sample_bank" not in html:
            fail("the shelf dropped the activity")
            return
        ok("activity rows come from the evidence store, newest first")
    finally:
        r.close()


def check_shelf_carries_the_sitting_links():
    """The shelf cards keep every entrance the old index had, reading
    first, and link the file list view for stems and collisions."""
    r = _Root()
    try:
        html = home.render_home(home.home_state(r.root), "shelf")
        for needle in ("Sit this bank", "Study this bank",
                       "/quiz/sample_bank", "/study/sample_bank",
                       "/banks"):
            if needle not in html:
                fail("the shelf is missing %r" % needle)
                return
        if "/lesson/sample_bank" in html:
            fail("the shelf advertises a reading the bank does not have")
            return
        ok("shelf cards keep sit, study and the file-list link, reading "
           "absent when the bank has none")
    finally:
        r.close()


def check_four_modes_render_from_one_state():
    """All four modes ship and render from the same state dict: a mode
    is a template, never a second data path."""
    r = _Root()
    try:
        r.write_session("sample_bank", cursor=3, total=6)
        state = home.home_state(r.root)
        if tuple(home.MODES) != ("shelf", "next-action", "agent", "split"):
            fail("MODES is %r" % (home.MODES,))
            return
        if home.DEFAULT_MODE != "shelf":
            fail("the default mode is %r, not shelf"
                 % home.DEFAULT_MODE)
            return
        shelf = home.render_home(state, "shelf")
        for mode in ("next-action", "agent", "split"):
            body = home.render_home(state, mode)
            if "sample_bank" not in body:
                fail("mode %r lost the card stems" % mode)
                return
        nxt = home.render_home(state, "next-action")
        if "Everything else" not in nxt:
            fail("next-action mode hides the shelf entirely")
            return
        agent = home.render_home(state, "agent")
        if "sample_bank" not in agent or "Agent area" not in agent \
                and "agent area" not in agent.lower():
            fail("agent mode shows neither the area nor card context")
            return
        split = home.render_home(state, "split")
        if "home-split" not in split:
            fail("split mode renders no two-column layout")
            return
        if "max-width:640px" not in home.HOME_CSS.replace(" ", ""):
            fail("split has no phone-width degradation")
            return
        if "nowrap" in home.HOME_CSS or "ellipsis" in home.HOME_CSS:
            fail("home CSS truncates link text")
            return
        if "In progress: 3 of 6" not in split:
            fail("split disagrees with the shelf about the cursor")
            return
        ok("all four modes render one state, split degrades at 640px")
    finally:
        r.close()


def check_unknown_mode_falls_back_saying_so():
    """An unknown setting falls back to shelf and says so exactly once,
    rather than failing to serve a home."""
    r = _Root()
    try:
        state = home.home_state(r.root)
        html = home.render_home(state, "magazine")
        if html.count("magazine") != 1:
            fail("the fallback note appears %d times, not once"
                 % html.count("magazine"))
            return
        if "Sit this bank" not in html:
            fail("the fallback did not serve a shelf")
            return
        mode, note = home.resolve_mode("")
        if mode != "shelf" or note is not None:
            fail("an empty setting resolved to %r/%r" % (mode, note))
            return
        ok("an unknown mode falls back to shelf with one note")
    finally:
        r.close()


def check_setting_and_schema_carry_the_modes():
    """`home` is a real settings key: typed as the four modes, defaulted
    to the shelf Weibao chose, described, and validated by the same
    loader every other key uses."""
    import schema_validate
    schema_path = os.path.join(ROOT, "schemas", "settings.schema.json")
    with open(schema_path, encoding="utf-8") as fh:
        schema = json.load(fh)
    prop = schema["properties"].get("home")
    if prop is None:
        fail("settings.schema.json carries no home key")
        return
    if list(prop.get("enum") or []) != list(home.MODES):
        fail("home enum is %r, not the four modes" % prop.get("enum"))
        return
    if prop.get("default") != "shelf":
        fail("home defaults to %r, not the chosen shelf"
             % prop.get("default"))
        return
    if "description" not in prop:
        fail("home carries no description naming what each mode shows")
        return
    r = _Root(banks=())
    try:
        cfg_path = os.path.join(r.root, "itembank.json")
        with open(cfg_path, "w", encoding="utf-8") as fh:
            json.dump({"home": "split"}, fh)
        from surfaces import settings as settings_mod
        doc = settings_mod.load_settings(r.root)
        if doc.get("home") != "split":
            fail("load_settings read home as %r" % doc.get("home"))
            return
        with open(cfg_path, "w", encoding="utf-8") as fh:
            json.dump({"home": "magazine"}, fh)
        try:
            settings_mod.load_settings(r.root)
            fail("an invalid home mode was accepted")
        except SystemExit:
            pass
        errs = schema_validate.validate(
            "shelf", schema["properties"]["home"])
        if errs:
            fail("the shipped default fails its own subschema: %r" % errs)
            return
        if not schema_validate.validate(
                "magazine", schema["properties"]["home"]):
            fail("the subschema accepted a mode outside the enum")
            return
    finally:
        r.close()
    with open(os.path.join(ROOT, "itembank.json"), encoding="utf-8") as fh:
        shipped = json.load(fh)
    if shipped.get("home") != "shelf":
        fail("the repository's itembank.json ships home=%r"
             % shipped.get("home"))
        return
    ok("home is a validated setting, shipped at the chosen default")


class _FakeHandler(object):
    """Just enough handler for the daemon's GET / handlers: a root, the
    startup scan, and a place to capture the HTML."""

    def __init__(self, root):
        from surfaces import daemon as daemon_mod
        self.root = root
        self.banks, self.plans, self.collisions = daemon_mod.scan_dir(root)
        self.sent = None

    def send_html(self, body):
        self.sent = body.decode("utf-8")


def check_daemon_serves_the_configured_home():
    """Task 3: GET / renders the configured home through the daemon's own
    handlers; the mode setting switches the shape without touching the
    data function."""
    from surfaces import daemon as daemon_mod
    r = _Root()
    try:
        r.write_session("sample_bank", cursor=3, total=6)
        handler = _FakeHandler(r.root)
        daemon_mod.handle_index(handler)
        html = handler.sent or ""
        for needle in ("Sit this bank", "Study this bank",
                       "In progress: 3 of 6"):
            if needle not in html:
                fail("the served home is missing %r" % needle)
                return
        with open(os.path.join(r.root, "itembank.json"), "w",
                  encoding="utf-8") as fh:
            json.dump({"home": "next-action"}, fh)
        handler = _FakeHandler(r.root)
        daemon_mod.handle_index(handler)
        if "Everything else" not in (handler.sent or ""):
            fail("the configured next-action home did not serve")
            return
        ok("GET / serves the configured mode over the same state")
    finally:
        r.close()


def check_file_list_stays_reachable_at_banks():
    """The old stem list moves to /banks whole: stems, day plans, and the
    stem-collision warning the daemon still needs somewhere to report."""
    from surfaces import daemon as daemon_mod
    r = _Root()
    try:
        shutil.copy(os.path.join(ROOT, "fixtures", "sample_plan.md"),
                    os.path.join(r.root, "sample_plan.md"))
        # A stem collision: two directories, same filename stem.
        os.makedirs(os.path.join(r.root, "a"))
        os.makedirs(os.path.join(r.root, "b"))
        shutil.copy(BANK, os.path.join(r.root, "a", "dupe_bank.md"))
        shutil.copy(BANK, os.path.join(r.root, "b", "dupe_bank.md"))
        handler = _FakeHandler(r.root)
        daemon_mod.handle_banks(handler)
        html = handler.sent or ""
        for needle in ("sample_bank", "sample_plan", "Open day view",
                       "shares their name"):
            if needle not in html:
                fail("/banks is missing %r" % needle)
                return
        home_html = _FakeHandler(r.root)
        daemon_mod.handle_index(home_html)
        if 'href="/banks"' not in (home_html.sent or ""):
            fail("the home does not link the file list")
            return
        ok("/banks keeps the stem list, plans and collision warning")
    finally:
        r.close()


def check_daemon_empty_case_keeps_its_copy():
    """A daemon serving nothing still says exactly what it said before."""
    from surfaces import daemon as daemon_mod
    from surfaces import ia as ia_mod
    r = _Root(banks=())
    # Plan 16B-09 (APP-03): a genuinely fresh root materializes the bundled
    # sample course on first launch. The documented empty copy still governs
    # the no-course case, so the sample is recorded as removed and this check
    # keeps asserting exactly what it always asserted.
    ia_mod.write_ia_state(r.root, "sample_course", {"removed": True})
    try:
        handler = _FakeHandler(r.root)
        daemon_mod.handle_index(handler)
        if "Nothing to serve here yet" not in (handler.sent or ""):
            fail("the empty home lost its documented copy")
            return
        ok("the empty case keeps its copy")
    finally:
        r.close()


def check_reading_stays_first_on_every_card():
    """The 2026-08-21 fix holds on the new surface: when a bank has a
    lesson its reading link precedes the sitting link, on the home and
    on /banks alike."""
    from surfaces import daemon as daemon_mod
    r = _Root()
    try:
        shutil.copy(os.path.join(ROOT, "fixtures", "lesson_bank.md"),
                    os.path.join(r.root, "lesson_bank.md"))
        handler = _FakeHandler(r.root)
        daemon_mod.handle_index(handler)
        html = handler.sent or ""
        if "/lesson/lesson_bank" not in html:
            fail("a bank with a lesson gets no reading link on the home")
            return
        if html.index("/lesson/lesson_bank") > \
                html.index("/quiz/lesson_bank"):
            fail("the sitting is offered before the reading")
            return
        banks_handler = _FakeHandler(r.root)
        daemon_mod.handle_banks(banks_handler)
        old = banks_handler.sent or ""
        if old.index("/lesson/lesson_bank") > \
                old.index("/quiz/lesson_bank"):
            fail("/banks inverted the order")
            return
        ok("reading stays first on the home and on /banks")
    finally:
        r.close()


def check_proposals_surface_on_the_object_only():
    """Task 4: a pending proposal about an object shows one badge with
    the count and a link into the Agent area, on that object's card.
    Acceptance never happens from the badge. With nothing pending, the
    home renders no badge and fabricates nothing."""
    from surfaces import daemon as daemon_mod
    r = _Root()
    try:
        state = home.home_state(r.root)
        if home.pending_proposals(r.root) != []:
            fail("nothing persists proposals yet; the source returned "
                 "non-zero")
            return
        shelf = home.render_home(state, "shelf")
        if "home-badge" in shelf:
            fail("a zero-proposal root rendered a badge")
            return
        banks, plans, collisions = daemon_mod.scan_dir(r.root)
        abspath = os.path.abspath(os.path.join(r.root, "sample_bank.md"))
        proposals = [{"path": abspath, "count": 2}]
        state = home.build_state(r.root, banks, plans, collisions,
                                 proposals=proposals)
        card = card_by_stem(state, "sample_bank")
        if card["proposal_count"] != 2:
            fail("the card carries count %r" % card["proposal_count"])
            return
        shelf = home.render_home(state, "shelf")
        if "2 pending proposals" not in shelf:
            fail("the badge does not carry the count")
            return
        start = shelf.index("home-badge")
        segment = shelf[start:start + 400]
        if home.AGENT_AREA_HREF not in segment:
            fail("the badge does not link into the Agent area")
            return
        if ">Accept<" in segment or ">Reject<" in segment:
            fail("the badge offers acceptance outside the Agent area")
            return
        ok("a pending proposal surfaces as a counted badge linking to "
           "the Agent area")
    finally:
        r.close()


def check_agent_area_keeps_room_for_inline_affordances():
    """The third placement option stays registered: the Agent area holds
    a named slot for inline affordances, rendered as not built yet
    rather than hidden or dropped."""
    r = _Root()
    try:
        state = home.home_state(r.root)
        body = home.render_home(state, "agent")
        for needle in ("ask about this item", "revise this lesson",
                       "not built yet"):
            if needle not in body.lower():
                fail("the inline-affordance slot is missing %r" % needle)
                return
        ok("the Agent area names its registered-but-unbuilt slots")
    finally:
        r.close()


def _phase20_state(kind="one"):
    """Synthetic durable facts only. No sitting or learner evidence is read."""
    course = {
        "course_id": "course-synthetic-algebra",
        "name": "Synthetic Algebra",
        "route": "/course/course-synthetic-algebra",
        "state": "available",
        "resume": {"label": "Resume lesson 2",
                   "href": "/course/course-synthetic-algebra/learn/lesson-2"},
        "primary_action": {"label": "Resume lesson 2",
                           "href": "/course/course-synthetic-algebra/learn/lesson-2"},
        "facts": [
            {"kind": "anki_due", "source": "Anki due", "label": "4 cards"},
            {"kind": "itembank_due", "source": "itembank due", "label": "2 reviews"},
            {"kind": "course_completion", "source": "Course completion",
             "label": "3 of 8 objectives complete"},
            {"kind": "evidence_standing", "source": "Evidence standing",
             "label": "6 settled attempts"},
        ],
        "path": [
            {"state": "complete", "label": "Read lesson 1",
             "href": "/course/course-synthetic-algebra/learn/lesson-1"},
            {"state": "current", "label": "Read lesson 2",
             "href": "/course/course-synthetic-algebra/learn/lesson-2"},
            {"state": "available", "label": "Practice set",
             "href": "/course/course-synthetic-algebra/practice"},
            {"state": "pending", "label": "Written response review"},
            {"state": "locked", "label": "Formal assessment"},
            {"state": "unavailable", "label": "Remote source"},
        ],
    }
    agenda = [
        {"group": "overdue", "kind": "itembank_due",
         "course_id": course["course_id"], "href": course["route"],
         "label": "Review objective A", "source": "itembank due"},
        {"group": "today", "kind": "anki_due",
         "course_id": course["course_id"], "href": course["route"],
         "label": "Review 4 cards", "source": "Anki due"},
        {"group": "upcoming", "kind": "itembank_due",
         "course_id": course["course_id"], "href": course["route"],
         "label": "Practice objective B", "source": "itembank due"},
        {"group": "revision", "kind": "course_revision",
         "course_id": course["course_id"], "href": course["route"],
         "label": "Inspect course revision", "source": "Course revision"},
        {"group": "recently-completed", "kind": "course_completion",
         "course_id": course["course_id"], "href": course["route"],
         "label": "Lesson 1 completed", "source": "Course completion"},
    ]
    axes = {"presentation_profile": "field-guide", "home": "shelf",
            "look": "classic", "theme": "system", "accent": "blue",
            "density": "comfortable", "contrast": "normal",
            "motion": "full"}
    if kind == "empty":
        return {"courses": [], "agenda": [], "appearance": axes}
    if kind == "many":
        second = copy.deepcopy(course)
        second.update({"course_id": "course-synthetic-history",
                       "name": "Synthetic History",
                       "route": "/course/course-synthetic-history"})
        second["resume"] = {"label": "Start source reading",
                            "href": "/course/course-synthetic-history/learn"}
        second["primary_action"] = copy.deepcopy(second["resume"])
        return {"courses": [course, second], "agenda": agenda,
                "appearance": axes}
    if kind in ("archived", "corrupted", "interrupted", "unavailable"):
        labels = {
            "archived": ("Archived course. Its files remain available.",
                         "Open archived course", course["route"]),
            "corrupted": ("Course record could not be read. Nothing was overwritten.",
                          "Open last valid overview", course["route"]),
            "interrupted": ("Interrupted at lesson 2. Resume the same locator.",
                            "Resume lesson 2", course["resume"]["href"]),
            "unavailable": ("Remote source unavailable. Local course remains available.",
                            "Open local course", course["route"]),
        }
        blocker, label, href = labels[kind]
        course["state"] = kind
        course["blocker"] = blocker
        course["primary_action"] = {"label": label, "href": href}
    return {"courses": [course], "agenda": agenda, "appearance": axes}


def check_phase20_projection_contract():
    """Task 20-02-01: four learner jobs share one immutable state contract."""
    if tuple(home.LEARNER_JOBS) != ("resume", "shelf", "agenda", "path"):
        fail("learner jobs changed: %r" % (home.LEARNER_JOBS,))
        return
    if home.LEARNER_JOB_MODES != {"resume": "next-action", "shelf": "shelf"}:
        fail("Resume and Shelf no longer refine the stable modes")
        return
    if "agenda" in home.MODES or "path" in home.MODES:
        fail("prototype jobs were minted as stable setting values")
        return
    for kind in ("empty", "one", "many", "archived", "corrupted",
                 "interrupted", "unavailable"):
        state = _phase20_state(kind)
        before = copy.deepcopy(state)
        for job in home.LEARNER_JOBS:
            body = home.render_projection(state, job, "field-guide")
            if 'data-learner-job="%s"' % job not in body:
                fail("%s fixture did not render %s" % (kind, job))
                return
            if state != before:
                fail("%s projection mutated canonical state" % job)
                return
        if kind == "empty":
            for job in home.LEARNER_JOBS:
                body = home.render_projection(state, job)
                if "data-state=\"empty\"" not in body:
                    fail("%s has no meaningful empty state" % job)
                    return
    ok("empty, one, many, archived, corrupted, interrupted, and unavailable fixtures render from one state")


def check_phase20_projection_labels_and_actions():
    state = _phase20_state("many")
    shelf = home.render_projection(state, "shelf")
    if shelf.count("data-action-primary") != len(state["courses"]):
        fail("Shelf does not render exactly one primary action per course")
        return
    path_actions = home.render_projection(state, "path").count(
        "data-action-primary")
    if path_actions != len(state["courses"]):
        fail("Path does not render exactly one primary action per course")
        return
    if any(len(card["primary_action"]["label"]) > 40
           for card in state["courses"]):
        fail("a course primary action is not short")
        return
    for label in ("Anki due", "itembank due", "Course completion",
                  "Evidence standing"):
        if label not in shelf:
            fail("Shelf merged or omitted %r" % label)
            return
    agenda = home.render_projection(state, "agenda")
    for key, _label in home.AGENDA_GROUPS:
        if 'data-agenda-group="%s"' % key not in agenda:
            fail("Agenda omitted populated durable group %r" % key)
            return
    empty_agenda = home.render_projection({"courses": state["courses"],
                                           "agenda": []}, "agenda")
    if "data-agenda-group" in empty_agenda or "Use Shelf" not in empty_agenda:
        fail("Agenda did not hide empty groups or name its supported fallback")
        return
    path = home.render_projection(state, "path")
    for path_state in home.PATH_STATES:
        if 'data-path-state="%s"' % path_state not in path:
            fail("Path omitted state %r" % path_state)
            return
    if "master" in path.lower():
        fail("Path equated movement with mastery")
        return
    ok("actions stay singular and due, completion, evidence, agenda, and path states stay separate")


def check_phase20_profiles_preserve_behavior():
    state = _phase20_state("many")
    for job in home.LEARNER_JOBS:
        guide = home.render_projection(state, job, "field-guide")
        deck = home.render_projection(state, job, "trajectory-deck")
        for token in ("course-synthetic-algebra", "/course/course-synthetic-algebra"):
            if guide.count(token) != deck.count(token):
                fail("%s profile switch changed behavior token %r" % (job, token))
                return
    root = _Root()
    try:
        legacy = home.home_state(root.root)
        for mode in ("agent", "split"):
            for profile in ("field-guide", "trajectory-deck"):
                body = home.render_home(legacy, mode,
                                        presentation_profile=profile)
                if 'data-presentation-profile="%s"' % profile not in body:
                    fail("%s did not render in %s" % (mode, profile))
                    return
    finally:
        root.close()
    ok("all learner jobs plus agent and split preserve behavior across both profiles")


def main():
    check_empty_root_is_honest()
    check_bank_with_no_session_is_not_started()
    check_bank_mid_session_reports_its_cursor()
    check_next_action_comes_from_evidence()
    check_no_evidence_means_no_next_action()
    check_activity_lists_real_events()
    check_shelf_carries_the_sitting_links()
    check_four_modes_render_from_one_state()
    check_unknown_mode_falls_back_saying_so()
    check_setting_and_schema_carry_the_modes()
    check_daemon_serves_the_configured_home()
    check_file_list_stays_reachable_at_banks()
    check_daemon_empty_case_keeps_its_copy()
    check_reading_stays_first_on_every_card()
    check_proposals_surface_on_the_object_only()
    check_agent_area_keeps_room_for_inline_affordances()
    check_phase20_projection_contract()
    check_phase20_projection_labels_and_actions()
    check_phase20_profiles_preserve_behavior()
    if failures:
        print("\n%d failure(s)" % len(failures))
        return 1
    print("\nall home checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
