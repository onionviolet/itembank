#!/usr/bin/env python3
"""The home surface (plan 17A-08): one data function, four modes.

`home_state(root)` builds everything the home shows from sources that
already exist: the daemon's own startup scan (banks, day plans, stem
collisions), the newest session per bank under `_attempts/`, the evidence
store, and `retention`'s recommendation for what is next. No model
produces any of it. The runtime chooses what is next, the same as
everywhere else in itembank.

Honesty rules this module enforces:

- A card never displays progress it could not compute. A bank with no
  session is `not_started`, never 0%.
- The next action carries one sentence of `why`, built from the
  evidence store's own counts (which objective, how many misses, over
  what denominator). If evidence cannot ground a reason, there is no
  next action and the home says what would make one possible.
- This is a shelf of BANKS until phase 14B lands a course object. The
  word "course" on a screen that cannot parse a course is the kind of
  lie this project has rules against. `HOME_UNIT` names that seam: 14B
  swaps the noun and the grouping without touching the modes.
"""
import html
import json
import os

import evidence
import retention

# The named seam for 14B: today every card is a bank file on disk.
HOME_UNIT = "bank"

MODES = ("shelf", "next-action", "agent", "split")
DEFAULT_MODE = "shelf"

ACTIVITY_MAX = 5


def resolve_mode(value):
    """(mode, note). An unknown or missing setting falls back to the
    shelf default and says so once, rather than failing to serve a home."""
    if not value:
        return DEFAULT_MODE, None
    if value in MODES:
        return value, None
    return DEFAULT_MODE, (
        "'%s' is not one of the four home modes (%s); showing %s."
        % (value, ", ".join(MODES), DEFAULT_MODE))


def pending_proposals(root):
    """Agent proposals waiting about objects in this root, as
    `{path, count}` rows.

    Zero is the honest answer today and the home must render it without
    fabricating one. Plan 17A-07's run-propose-accept machine holds a
    proposal inside one run; nothing persists a pending proposal yet, so
    there is genuinely nothing to count. When persistence lands, this
    function is the single source the badge reads; acceptance still
    happens only in the Agent area.
    """
    return []


def _load_session(path):
    """The raw session dict, or None. Tolerant on purpose: a half-written
    or future-versioned file must not take the whole home down."""
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def _resume(root, banks, sessions, stem):
    """(resume dict, progress dict or None). Progress exists only when a
    real sitting reports a real cursor; otherwise it is refused with a
    reason instead of being invented."""
    session_id = sessions.get(stem)
    if session_id is None:
        return ({"state": "not_started", "session_id": None},
                None, "no sitting has been started here")
    from surfaces import daemon as daemon_mod
    path = daemon_mod.session_index(root).get(session_id)
    data = _load_session(path) if path else None
    if data is None:
        return ({"state": "not_started", "session_id": session_id},
                None, "its last sitting could not be read")
    items = data.get("items") or []
    cursor = data.get("cursor") or 0
    total = len(items)
    done = data.get("status") == "complete" or \
        (total and cursor >= total)
    state = "complete" if done else "in_progress"
    progress = {"answered": min(cursor, total), "total": total}
    return ({"state": state, "session_id": session_id}, progress, None)


def _next_action(root, banks):
    """(action dict or None, blocker sentence or None).

    The objective comes from retention's recommendation over ONE captured
    snapshot; the sentence comes from that snapshot's own counts. When
    retention cannot ground a reason, there is no next action.
    """
    log = evidence.log_path(root)
    events = evidence.capture_events(log) \
        if os.path.exists(log) else ()
    cfg = None
    try:
        from surfaces import settings as settings_mod
        cfg = settings_mod.load_settings(root)
    except SystemExit:
        cfg = None
    snapshot = retention.capture(events, cfg=cfg)
    summaries = retention.objective_summaries(snapshot)
    rec = retention.recommendation(summaries, snapshot)

    by_abspath = dict((os.path.abspath(path), stem)
                      for stem, path in banks.items())

    def stem_for(objective):
        for ev in reversed(events):
            if ev.get("objective") == objective \
                    and ev.get("bank") in by_abspath:
                return by_abspath[ev.get("bank")]
        return None

    if rec.get("objectives"):
        objective = rec["objectives"][0]
        row = next((r for r in summaries
                    if r["objective"] == objective), None)
        missed = denominator = None
        if row is not None:
            missed = row["settled"] - row["correct"]
            denominator = row["settled"]
        why = ("You have missed '%s' %s times, so practice it now."
               % (objective,
                  ("%d of %d settled" % (missed, denominator))
                  if missed is not None else "recently"))
        stem = stem_for(objective)
        href = "/quiz/%s" % html.escape(stem) if stem else "/banks"
        return {"verb": "practice", "objective": objective, "why": why,
                "href": href}, None

    if not events:
        return None, ("No evidence yet: nothing has been answered under "
                      "this root. Sit a practice set and this slot will "
                      "name what to review.")
    return None, ("%s. Sit a practice set; once more responses are "
                  "recorded, this slot names what to review."
                  % rec.get("reason", "Nothing is due right now"))


def _activity(root, banks=None):
    """Recent recorded responses, newest first, capped. Built from the
    evidence log only; an empty log is an empty list."""
    log = evidence.log_path(root)
    if not os.path.exists(log):
        return []
    by_abspath = dict((os.path.abspath(path), stem)
                      for stem, path in (banks or {}).items())

    def stem_of(ev):
        bank = ev.get("bank") or ""
        return by_abspath.get(os.path.abspath(bank)) if bank else None

    rows = []
    for ev in evidence.events(log):
        if ev.get("event_type") != evidence.RESPONSE_EVENT_TYPE:
            continue
        outcome = {True: "correct", False: "wrong",
                   None: "pending review"}.get(ev.get("score"), "scored")
        stem = stem_of(ev)
        where = " of %s" % stem if stem else ""
        rows.append({"when": ev.get("ts") or "",
                     "text": "Answered %s%s (%s)"
                             % (ev.get("item_ref") or ev.get("item_id")
                                or "an item", where, outcome)})
    rows.reverse()
    return rows[:ACTIVITY_MAX]


def build_state(root, banks, plans, collisions):
    """Assemble the one state dict every mode renders from. Callers that
    already hold the startup scan (the daemon) pass it in; `home_state`
    scans first for everyone else."""
    from surfaces import daemon as daemon_mod
    from model import load, parse_bank, parse_lesson

    sessions = daemon_mod.sessions_by_bank(root, banks)
    proposals = pending_proposals(root)
    proposal_counts = {}
    for row in proposals:
        proposal_counts[row.get("path")] = row.get("count", 0)

    cards = []
    for stem in sorted(banks, key=str.lower):
        path = banks[stem]
        abspath = os.path.abspath(path)
        objectives = set()
        items = None
        try:
            with open(path, encoding="utf-8") as fh:
                qs = parse_bank(fh.read())
            items = len(qs)
            objectives = set(q.get("objective", "") for q in qs
                             if q.get("objective"))
        except (OSError, UnicodeDecodeError):
            items = None
        resume, progress, refusal = _resume(root, banks, sessions, stem)
        try:
            has_lesson = bool(parse_lesson(path))
        except Exception:
            has_lesson = False
        cards.append({
            "stem": stem,
            "kind": HOME_UNIT,
            "path": abspath,
            "items": items,
            "objectives": len(objectives) if objectives else None,
            "objectives_note": "" if objectives else
            "no objectives are tagged on its items",
            "has_lesson": has_lesson,
            "resume": resume,
            "progress": progress,
            "progress_refused_reason": refusal,
            "proposal_count": proposal_counts.get(abspath, 0),
        })

    action, blocker = _next_action(root, banks)
    return {
        "root": os.path.abspath(root),
        "unit": HOME_UNIT,
        "cards": cards,
        "plans": [{"stem": stem, "href": "/day/%s" % html.escape(stem)}
                  for stem in sorted(plans, key=str.lower)],
        "collisions": collisions or [],
        "next_action": action,
        "next_action_blocker": blocker,
        "activity": _activity(root, banks),
        "load": load,
    }


def home_state(root):
    """Scan `root` the way the daemon does, then build the home state."""
    from surfaces import daemon as daemon_mod
    banks, plans, collisions = daemon_mod.scan_dir(root)
    return build_state(root, banks, plans, collisions)


# ---- templates. A mode is a template over one state dict, never a
# second data path, so the four cannot disagree about what is true. ----

def _esc(value):
    return html.escape(str(value), quote=True)


def _resume_line(card):
    resume = card["resume"]
    if resume["state"] == "not_started":
        return "Not started"
    if resume["state"] == "complete":
        return "Sitting complete"
    p = card["progress"] or {}
    return "In progress: %d of %d answered" % (p.get("answered", 0),
                                               p.get("total", 0))


def _card_links(card):
    stem = _esc(card["stem"])
    parts = []
    # Reading first, always: the reading comes before the sitting.
    if card["has_lesson"]:
        parts.append('<a class="go primary" data-action-primary '
                     'href="/lesson/%s">Read the lesson</a>' % stem)
    parts.append('<a href="/quiz/%s">Sit this bank</a>' % stem)
    parts.append('<a href="/study/%s">Study this bank</a>' % stem)
    if card["resume"]["session_id"]:
        parts.append('<a href="/report?session=%s">View report</a>'
                     % _esc(card["resume"]["session_id"]))
    return "\n    ".join(parts)


def _cards_html(state):
    rows = []
    for card in state["cards"]:
        meta = []
        if card["items"] is not None:
            meta.append("%d items" % card["items"])
        if card["objectives"]:
            meta.append("%d objectives" % card["objectives"])
        elif card["objectives_note"]:
            meta.append(card["objectives_note"])
        badge = ""
        if card["proposal_count"]:
            badge = ('<span class="home-badge">%d pending proposal%s, '
                     'review it in the Agent area</span>'
                     % (card["proposal_count"],
                        "" if card["proposal_count"] == 1 else "s"))
        rows.append(
            '<li class="home-card"><h3>%s</h3>'
            '<p class="vf-status">%s</p>'
            '<p class="vf-status">%s%s</p>'
            '<div class="links">%s</div></li>'
            % (_esc(card["stem"]), _esc("; ".join(meta)),
               _esc(_resume_line(card)), badge, _card_links(card)))
    if rows:
        return ('<ul class="home-cards">%s</ul>'
                "<p class=\"vf-status\">These are %ss: files on disk. A "
                "course object that groups them arrives in phase 14B.</p>"
                % ("\n".join(rows), _esc(state["unit"])))
    return ("<p class=\"vf-status\">No %s files are being served here "
            "yet.</p>" % _esc(state["unit"]))


def _plans_html(state):
    if not state["plans"]:
        return ""
    links = "".join('<li><a href="%s">Open day view</a></li>'
                    % plan["href"] for plan in state["plans"])
    return ('<h3>Day plans</h3><ul class="home-plans">%s</ul>'
            % links)


def _next_html(state):
    action = state["next_action"]
    if action is None:
        return ('<section class="home-next" data-state="unknown">'
                "<p class=\"vf-status\">%s</p></section>"
                % _esc(state["next_action_blocker"]
                       or "Nothing is queued."))
    return (
        '<section class="home-next" data-state="ok">'
        "<h3>Next: practice %s</h3><p>%s</p>"
        '<p><a class="go primary" data-action-primary href="%s">'
        "Start it</a></p></section>"
        % (_esc(action["objective"]), _esc(action["why"]),
           action["href"]))


def _activity_html(state):
    if not state["activity"]:
        return ""
    rows = "".join("<li><span class=\"vf-status\">%s</span> %s</li>"
                   % (_esc(row["when"]), _esc(row["text"]))
                   for row in state["activity"])
    return '<h3>Recent activity</h3><ul class="home-activity">%s</ul>' % rows


def _collision_note(state):
    if not state["collisions"]:
        return ""
    return ('<p class="vf-status">%d file(s) were not served because '
            "another file shares their name; see <a href=\"/banks\">all "
            "files</a>.</p>" % len(state["collisions"]))


def render_shelf(state, note=None):
    head = ""
    if note:
        head = '<p class="vf-status" data-state="warn">%s</p>' % _esc(note)
    return (
        '<section class="home">%s'
        "%s%s%s%s%s%s</section>"
        % (head, _next_html(state), _cards_html(state),
           _plans_html(state), _activity_html(state),
           _collision_note(state),
           '<p class="vf-status"><a href="/banks">All files, including '
           "any the daemon could not serve</a></p>"))


def render_next_action(state, note=None):
    head = ""
    if note:
        head = '<p class="vf-status" data-state="warn">%s</p>' % _esc(note)
    return (
        '<section class="home home-mode-next">%s%s'
        "<details><summary>Everything else on the shelf</summary>%s%s%s"
        "</details></section>"
        % (head, _next_html(state), _cards_html(state),
           _plans_html(state), _activity_html(state)))


def _agent_html(state):
    try:
        from surfaces import visual_fixture
        data = visual_fixture.load_fixture()
        return visual_fixture.render_stage(data, "agent_harness",
                                           base=state["root"])
    except Exception:
        return ('<section class="vf-stage"><h2>Agent area</h2>'
                '<p class="vf-status">The agent area could not be '
                "rendered here; it stays available on its own screen."
                "</p></section>")


def render_agent(state, note=None):
    head = ""
    if note:
        head = '<p class="vf-status" data-state="warn">%s</p>' % _esc(note)
    context = "".join(
        '<li class="home-card"><h3>%s</h3><p class="vf-status">%s</p></li>'
        % (_esc(card["stem"]), _esc(_resume_line(card)))
        for card in state["cards"])
    return (
        '<section class="home home-mode-agent">%s'
        "<h3>Agent area</h3>%s"
        "<h3>Your %ss, as context</h3><ul class=\"home-cards\">%s</ul>"
        "</section>"
        % (head, _agent_html(state), _esc(state["unit"]), context))


def render_split(state, note=None):
    return (
        '<section class="home home-split">%s'
        '<div class="home-col"><h3>The shelf</h3>%s%s%s</div>'
        '<div class="home-col"><h3>The agent</h3>%s</div>'
        "</section>"
        % ('<p class="vf-status" data-state="warn">%s</p>' % _esc(note)
           if note else "",
           _next_html(state), _cards_html(state), _activity_html(state),
           _agent_html(state)))


RENDERERS = {
    "shelf": render_shelf,
    "next-action": render_next_action,
    "agent": render_agent,
    "split": render_split,
}


def render_home(state, mode=None, note=None):
    """Render one mode over one state dict. An unknown mode falls back to
    the shelf and says so once."""
    mode, fallback_note = resolve_mode(mode or DEFAULT_MODE)
    if fallback_note:
        note = fallback_note
    return RENDERERS[mode](state, note=note)


# Styles for the four modes, appended to the theme block the shell
# already carries. Split degrades to one column at phone width instead
# of crushing two columns together.
HOME_CSS = """
.home-cards{list-style:none;padding:0;display:flex;flex-wrap:wrap;
gap:1rem;}
.home-card{border:1px solid var(--accent,#888);border-radius:8px;
padding:.75rem 1rem;max-width:34rem;}
.home-card .links{display:flex;flex-wrap:wrap;gap:.75rem;margin-top:.5rem;}
.home-next{border:2px solid var(--accent,#888);border-radius:8px;
padding:.75rem 1rem;margin-bottom:1rem;max-width:40rem;}
.home-badge{display:inline-block;margin-left:.5rem;padding:0 .5rem;
border-radius:999px;border:1px solid var(--accent,#888);}
.home-split{display:grid;grid-template-columns:1fr 1fr;gap:1.25rem;
align-items:start;}
@media (max-width:640px){.home-split{grid-template-columns:1fr;}}
"""
