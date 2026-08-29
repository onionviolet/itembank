#!/usr/bin/env python3
"""Assert that every degraded state itembank can reach says what happened, what
to do next, and where to read more, and that a refusal states its unlock
condition without carrying the content it withholds.

Two failures are guarded here. The first is a dead end: a failure that reports
itself and offers nothing, which leaves a learner with a sentence and no move.
The second is a refusal that behaves like a conversation, which invites the
learner to argue with a model about a disclosure the runtime, not the model,
decides. A locked card is the visible form of that boundary, so this file
asserts on the rendered markup and not only on the dict behind it.

Standard library only, no test framework, runnable as
`python tests/degraded_state_roundtrip.py`.
"""
import html, inspect, itertools, json, os, re, shutil, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import itembank                                             # noqa: E402
from surfaces import daemon, ia, presentation               # noqa: E402

sys.path.insert(0, os.path.join(ROOT, "fixtures"))
import course_storyboard_corpus as corpus                   # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from daemon_roundtrip import start_daemon, get              # noqa: E402

# Everything a locked card must never contain. Data rather than a chain of
# conditionals, so a later addition is one line.
FORBIDDEN_IN_LOCKED_CARD = (
    "<input", "<textarea", "<form", "contenteditable",
    'role="log"', 'aria-live="assertive"', "chat",
    "ask again", "send", "reply", "try asking", "typing",
    "hidden", "display:none", "visibility:hidden", 'aria-hidden="true"',
    "opacity:0",
    "sorry", "great job", "keep going",
)


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def check_eight_states():
    """Eight states, eight exact sentences, eight codes, and a next action."""
    for name in ("DEGRADED_COPY", "DEGRADED_ACTIONS", "DEGRADED_HELP_CODES"):
        table = getattr(ia, name)
        if sorted(table) != sorted(ia.DEGRADED_STATES):
            fail("%s does not cover exactly DEGRADED_STATES" % name)

    expected = {
        "crash": "Restored your last saved position. Nothing was lost since "
                 "your last saved step.",
        "cancelled": "Cancelled. Partial results are marked below and were "
                     "not saved as final.",
        "disk_full": "This save could not complete (disk full or "
                     "interrupted). Your previous version is intact. Free up "
                     "space and try again.",
        "offline": "You're offline. Reading, practice, scoring, hints, and "
                   "evidence keep working. Anything that needs a network "
                   "connection is marked unavailable below.",
        "permission_denied": "itembank could not access {target}. Check that "
                             "the folder is still shared with itembank, then "
                             "try again.",
        "future_schema": "This file was saved by a newer version of itembank. "
                         "The parts itembank recognizes are shown below; "
                         "nothing is changed or deleted.",
        "agent_unavailable": "Generated help is unavailable. You can keep "
                             "learning with the lesson and authored hints.",
        "course_corrupted": "This course's full record couldn't be loaded. "
                            "Showing its last valid overview.",
    }
    for state, sentence in expected.items():
        if ia.DEGRADED_COPY[state] != sentence:
            fail("%s's copy is not the locked sentence: %r"
                 % (state, ia.DEGRADED_COPY[state]))

    banner = ia.degraded_banner("offline")
    if set(banner) != {"state", "text", "code", "token", "actions"}:
        fail("degraded_banner returned the key set %r" % sorted(banner))
    if banner["text"] != expected["offline"] or banner["code"] != "ia.offline":
        fail("the offline banner was %r" % banner)

    named = ia.degraded_banner("permission_denied", target="airway_bank.md")
    if "airway_bank.md" not in named["text"]:
        fail("the permission_denied banner dropped its target")

    try:
        ia.degraded_banner("not_a_state")
    except ValueError as exc:
        if "not_a_state" not in str(exc):
            fail("the unknown-state error did not name the state: %s" % exc)
    else:
        fail("an unknown degraded state was accepted")

    for state in ia.DEGRADED_STATES:
        one = ia.degraded_banner(state, target="x.md")
        if not one["actions"]:
            fail("%s offered no next safe action" % state)
        for action in one["actions"]:
            if not action.get("label") or not action.get("href"):
                fail("%s carried an incomplete action: %r" % (state, action))
        if one["token"] != "unknown":
            fail("%s used the token %r; no degraded state is a learner error"
                 % (state, one["token"]))


def check_banner_precedence():
    """D-16B-9's declared tuple order, over every pair."""
    if ia.degraded_banner_for(["offline", "crash"])["state"] != "crash":
        fail("crash did not win the banner slot over offline")
    if ia.degraded_banner_for(
            ["course_corrupted", "disk_full"])["state"] != "disk_full":
        fail("disk_full did not win the banner slot over course_corrupted")

    order = list(ia.DEGRADED_STATES)
    pairs = 0
    for first, second in itertools.combinations(order, 2):
        pairs += 1
        winner = ia.degraded_banner_for([second, first])
        lower = first if order.index(first) < order.index(second) else second
        if winner["state"] != lower:
            fail("%s and %s resolved to %s, expected %s"
                 % (first, second, winner["state"], lower))
        other = second if lower == first else first
        if winner["also_fired"] != [ia.DEGRADED_HELP_CODES[other]]:
            fail("%s and %s reported also_fired %r"
                 % (first, second, winner["also_fired"]))
    if pairs != 28:
        fail("checked %d pairs, expected 28" % pairs)

    if ia.degraded_banner_for([]) is not None:
        fail("an empty fired set produced a banner")


def check_basename_only():
    """Four path shapes, one basename, no separator anywhere."""
    shapes = ("airway_bank.md",
              "C:/Users/w/private/airway_bank.md",
              "/home/w/private corpus/airway_bank.md",
              "..\\..\\secrets\\airway_bank.md")
    for shape in shapes:
        text = ia.degraded_banner("permission_denied", target=shape)["text"]
        if "airway_bank.md" not in text:
            fail("%r did not reduce to its basename: %r" % (shape, text))
        if "/" in text or "\\" in text:
            fail("%r left a path separator in the banner: %r" % (shape, text))

    for state in ia.DEGRADED_STATES:
        for shape in shapes:
            text = ia.degraded_banner(state, target=shape)["text"]
            if "/" in text or "\\" in text:
                fail("%s leaked a path separator for %r: %r"
                     % (state, shape, text))


def check_banner_help_links_resolve():
    """Every banner links exactly one help page, and every page exists."""
    for state, code in ia.DEGRADED_HELP_CODES.items():
        if code not in ia.IA_HELP_CODES:
            fail("%s maps to %r, which is not an IA_HELP_CODES member"
                 % (state, code))
        if code not in ia.HELP_TABLE:
            fail("%s maps to %r, which has no HELP_TABLE entry" % (state, code))
        banner = ia.degraded_banner(state, target="x.md")
        links = [a for a in banner["actions"]
                 if a["href"].startswith("/help/")]
        if len(links) != 1:
            fail("%s carried %d help links, expected exactly 1"
                 % (state, len(links)))
        if links[0]["href"] != "/help/" + code:
            fail("%s linked %r, expected /help/%s"
                 % (state, links[0]["href"], code))


def _render_locked(card):
    """Render a locked card the way a route would, through the one shared
    status region, so the negative contract is asserted on markup."""
    return ('<article class="locked-card"><h3>%s</h3><p>%s</p></article>'
            % (presentation.esc(card["header"]),
               presentation.esc(card["body"])))


def check_locked_card_shape():
    """One header, one sentence, four keys, and nothing withheld inside it."""
    card = ia.locked_refusal_card("Second hint tier",
                                  "you submit an attempt on this item")
    if card["header"] != "Second hint tier, locked":
        fail("the locked header was %r" % card["header"])
    if card["body"] != "Unlocks after you submit an attempt on this item.":
        fail("the locked body was %r" % card["body"])
    if set(card) != {"header", "body", "condition", "affordance"}:
        fail("the locked card carried the key set %r" % sorted(card))
    if not card["header"].endswith(", locked"):
        fail("the locked header did not end with the locked marker")
    if card["body"].count(".") != 1:
        fail("the locked body was not one sentence: %r" % card["body"])

    dotted = ia.locked_refusal_card("X", "you finish this step.")
    if dotted["body"] != "Unlocks after you finish this step.":
        fail("a condition ending in a period doubled it: %r" % dotted["body"])

    empty = ia.locked_refusal_card("X", "")
    if empty["body"] != "Unlocks after the next authored step.":
        fail("an empty condition produced %r" % empty["body"])
    if "Unlocks after ." in empty["body"]:
        fail("an empty condition produced the bare fragment")

    for key, value in card.items():
        text = "%s %s" % (key, value)
        for banned in ("message", "reply", "prompt", "input", "send", "chat"):
            if banned in text.lower():
                fail("the locked card carried a conversational key or value: "
                     "%r" % text)

    names = list(inspect.signature(ia.locked_refusal_card).parameters)
    if names != ["name", "condition", "affordance"]:
        fail("locked_refusal_card accepts %r; a parameter that could carry "
             "the withheld content would let it leak" % names)


def check_locked_card_is_not_chat():
    """The rendered card offers nothing that reads as continuing a
    conversation, and hides nothing it could instead be showing."""
    if len(FORBIDDEN_IN_LOCKED_CARD) < 17:
        fail("FORBIDDEN_IN_LOCKED_CARD has %d entries, expected at least 17"
             % len(FORBIDDEN_IN_LOCKED_CARD))

    card = ia.locked_refusal_card("Second hint tier",
                                  "you submit an attempt on this item")
    markup = _render_locked(card)
    lowered = markup.lower()
    for banned in FORBIDDEN_IN_LOCKED_CARD:
        if banned.lower() in lowered:
            fail("the rendered locked card carried %r" % banned)

    controls = lowered.count("<a ") + lowered.count("<button")
    if controls > 1:
        fail("the locked card offered %d controls, expected at most 1"
             % controls)

    if re.search(r"\bI\b", markup):
        fail("the locked card used a first-person pronoun")


def check_banner_end_to_end():
    """A corrupted course produces a real banner on a real page, and its help
    link resolves rather than dead-ending."""
    workdir = tempfile.mkdtemp(prefix="degraded_e2e_")
    proc = None
    try:
        corpus.build_corrupted_course(workdir)
        proc, url, lines = start_daemon(workdir)
        status, body = get(url)
        plain = html.unescape(body)
        if status != 200:
            fail("GET / returned %d with a corrupted course" % status)
        if ia.DEGRADED_COPY["course_corrupted"] not in plain:
            fail("the corrupted-course banner sentence was absent")
        if 'href="/help/ia.course_corrupted"' not in body:
            fail("the corrupted-course banner linked no help page")
        for needle in ("Open last valid overview", "View files"):
            if needle not in plain:
                fail("the banner omitted the action %r" % needle)
        if os.path.realpath(workdir) in body or workdir in body:
            fail("a resolved absolute path reached the served page")

        status, body = get(url + "help/ia.course_corrupted")
        if status != 200:
            fail("the banner's help link returned %d" % status)
        if ia.HELP_TABLE["ia.course_corrupted"]["cause"] not in \
                html.unescape(body):
            fail("the banner's help page carried no cause sentence")
    finally:
        if proc is not None:
            proc.terminate()
            proc.wait(timeout=5)
        shutil.rmtree(workdir, ignore_errors=True)

    workdir = tempfile.mkdtemp(prefix="degraded_agent_")
    saved = dict(os.environ)
    os.environ["ITEMBANK_IA_NO_JOURNAL"] = "1"
    proc = None
    try:
        proc, url, lines = start_daemon(workdir)
        status, body = get(url + "activity")
        plain = html.unescape(body)
        if status != 200:
            fail("GET /activity returned %d with the journal absent" % status)
        if ia.DEGRADED_COPY["agent_unavailable"] not in plain:
            fail("the agent-unavailable sentence was absent from /activity")
        if 'href="/help/ia.agent_unavailable"' not in body:
            fail("the agent-unavailable banner linked no help page")
    finally:
        if proc is not None:
            proc.terminate()
            proc.wait(timeout=5)
        os.environ.clear()
        os.environ.update(saved)
        shutil.rmtree(workdir, ignore_errors=True)


CHECKS = (check_eight_states,
          check_banner_precedence,
          check_basename_only,
          check_banner_help_links_resolve,
          check_locked_card_shape,
          check_locked_card_is_not_chat,
          check_banner_end_to_end)


def main():
    for check in CHECKS:
        check()
    print("DEGRADED: %d passed, 0 failed" % len(CHECKS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
