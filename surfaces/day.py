"""The day cockpit: today's work across every subject, ticked and logged.

Every other surface tests one subject. This one shows the whole day across all of
them and records whether it happened.

It exists because of an observed failure rather than a feature idea. A plan split
across several documents and tools is a plan that does not get opened, and two
consecutive days were lost exactly that way while the plan itself sat there,
correct and concrete. One screen, one tick per lane, one streak.

The plan stays wherever the learner keeps it and this reads it in place, so the
tool still holds no content of its own.
"""
import resources
import html, json, os, re, sys

import evidence
import retention
from model import lesson_slug, parse_lesson
from surfaces import presentation, retention_view, settings
from surfaces.session import OVERRIDE_CONFIRMATION
from surfaces.theme import theme_css

esc = html.escape


# ---- the day surface --------------------------------------------------------
# Every other command here tests one subject. This one shows the whole day
# across all of them and records whether it happened.
#
# It exists because of an observed failure rather than a feature idea. A plan
# split across several documents and tools is a plan that does not get opened,
# and two consecutive days were lost exactly that way while the plan itself sat
# there, correct and concrete. One screen, one tick per lane, one streak.
#
# The plan stays wherever the learner keeps it and this reads it in place, so
# the tool still holds no content of its own.

DAY_LANES = ("EMT", "Math", "CS", "Linux", "Mandarin", "Anki")


# The floor: the smallest day that still counts. A plan with no smaller version
# offers only all-or-nothing once a day starts badly, and nothing wins.
FLOOR_LANES = ("Anki", "EMT", "Math")


# A plan cell that names no work. "Slip budget; no required EMT task" is a
# planned zero, not a debt, so it must never count toward `behind` or `load`.
NONE_CELL = re.compile(r"^\s*(none\b|slip budget\b)", re.I)


MONTHS = dict((m, i + 1) for i, m in enumerate(
    "jan feb mar apr may jun jul aug sep oct nov dec".split()))


DONE_MARKS = ("x", "X", "yes", "done", "✓", "✔")


def parse_day_date(cell, year):
    """Read a date out of a plan table's first column.

    Accepts `2026-07-29` and the shape people actually write by hand,
    `**Mon Jul 27**`. Returns an ISO string, or "" when the cell is not a date,
    which is how a plan table is told apart from every other table in a
    document without the document having to declare itself.
    """
    t = re.sub(r"[*_`]", "", cell).strip()
    if re.match(r"^\d{4}-\d{2}-\d{2}$", t):
        return t
    for m in re.finditer(r"([A-Za-z]{3,9})\.?\s+(\d{1,2})\b", t):
        if m.group(1)[:3].lower() in MONTHS:
            return "%04d-%02d-%02d" % (year, MONTHS[m.group(1)[:3].lower()], int(m.group(2)))
    for m in re.finditer(r"\b(\d{1,2})\s+([A-Za-z]{3,9})", t):
        if m.group(2)[:3].lower() in MONTHS:
            return "%04d-%02d-%02d" % (year, MONTHS[m.group(2)[:3].lower()], int(m.group(1)))
    return ""


def lane_for_header(cell):
    t = re.sub(r"[*_`]", "", cell).lower()
    for lane in DAY_LANES:
        if re.search(r"\b%s\b" % re.escape(lane.lower()), t):
            return lane
    return ""


def split_row(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def is_rule_row(cells):
    return bool(cells) and all(re.match(r"^:?-{2,}:?$", c) for c in cells if c)


def parse_plan(path, year):
    """Pull every dated row out of a markdown plan document.

    Any table whose first column parses as a date is a plan table. That is the
    whole detection rule, so the plan can live inside a dashboard, a syllabus,
    or a file of its own and this does not need to be told which.
    """
    rows, header = {}, []
    for raw in open(path, encoding="utf-8"):
        if not raw.lstrip().startswith("|"):
            continue
        cells = split_row(raw)
        if is_rule_row(cells):
            continue
        iso = parse_day_date(cells[0], year)
        if not iso:
            header = cells                     # newest non-dated row wins as the header
            continue
        day = {}
        for i, text in enumerate(cells[1:], start=1):
            lane = lane_for_header(header[i]) if i < len(header) else ""
            if lane and text:
                day[lane] = text
        if day:
            rows[iso] = day
    return rows


# ---- the wiring file (lanes.md) ---------------------------------------------
# Which deck, notes file and fuse each lane carries, plus the global dated
# fuses. Data, never code: the current window's fuses expire the week classes
# start, and a tool with them baked in dies the same week. Two kinds of table,
# told apart by their headers: a `Lane` column wires lanes; a two-column table
# whose second header is a date carries global fuses.

def parse_lanes(path, known_lanes=DAY_LANES):
    """Returns (wiring, fuses, errors).

    wiring maps lane -> {deck, notes, fuse, fuse_date}; fuses is a list of
    (name, iso) pairs. errors is the lint, each entry carrying the line
    number and the problem, because a wiring mistake that fails silently is
    a lane that silently stops being watched.
    """
    wiring, fuses, errors = {}, [], []
    table, start = [], 0
    tables = []
    for n, raw in enumerate(open(path, encoding="utf-8"), start=1):
        if raw.lstrip().startswith("|"):
            if not table:
                start = n
            table.append((n, split_row(raw)))
        elif table:
            tables.append(table)
            table = []
    if table:
        tables.append(table)

    for table in tables:
        rows = [(n, c) for n, c in table if not is_rule_row(c)]
        if not rows:
            continue
        hn, header = rows[0]
        low = [h.lower() for h in header]
        if low and "lane" in low[0]:
            cols = {}
            for i, h in enumerate(low[1:], start=1):
                if "deck" in h:
                    cols["deck"] = i
                elif "glob" in h:
                    cols["glob"] = i
                elif "note" in h:
                    cols["notes"] = i
                elif "assignment" in h or "ledger" in h:
                    cols["assignments"] = i
                elif "fuse" in h and "date" in h:
                    cols["fuse_date"] = i
                elif "fuse" in h:
                    cols["fuse"] = i
            for n, cells in rows[1:]:
                lane = cells[0]
                if lane not in known_lanes:
                    errors.append("line %d: unknown lane %r (known: %s)"
                                  % (n, lane, ", ".join(known_lanes)))
                    continue
                w = {}
                for key, i in cols.items():
                    w[key] = cells[i] if i < len(cells) else ""
                if w.get("fuse_date") and not re.match(r"^\d{4}-\d{2}-\d{2}$",
                                                       w["fuse_date"]):
                    errors.append("line %d: lane %s has a malformed fuse date %r "
                                  "(want YYYY-MM-DD)" % (n, lane, w["fuse_date"]))
                    w["fuse_date"] = ""
                wiring[lane] = w
        elif len(header) == 2 and "date" in low[1]:
            for n, cells in rows[1:]:
                if len(cells) < 2 or not cells[0]:
                    continue
                if not re.match(r"^\d{4}-\d{2}-\d{2}$", cells[1]):
                    errors.append("line %d: fuse %r has a malformed date %r "
                                  "(want YYYY-MM-DD)" % (n, cells[0], cells[1]))
                    continue
                fuses.append((cells[0], cells[1]))
    return wiring, fuses, errors


def lint_lane_paths(wiring, lanes_path):
    """One resolver, so the linter cannot agree with a resolution bug.

    It used to repeat the two-base lookup inline, which meant a path the
    resolver could not find was also a path the linter reported as fine.
    """
    errors = []
    for lane, w in wiring.items():
        p = w.get("notes")
        if p and not resolve_notes(p, lanes_path):
            errors.append("lane %s: notes file %r does not exist" % (lane, p))
    return errors


def wiring_bases(lanes_path):
    """Candidate roots for a relative wiring path, nearest first.

    This used to be exactly two entries, the wiring file's folder and its
    parent, which worked only because `lanes.md` happens to sit one level below
    the vault root. Walk up to the repository root instead, so moving the
    wiring file deeper does not silently render every lane empty. The walk
    stops at a `.git` (a file in a worktree, a directory otherwise), at the
    filesystem root, or after eight levels, whichever comes first.
    """
    here = os.path.dirname(os.path.abspath(lanes_path))
    out, cur = [], here
    while True:
        out.append(cur)
        if os.path.exists(os.path.join(cur, ".git")):
            break
        parent = os.path.dirname(cur)
        if parent == cur or len(out) >= 8:
            break
        cur = parent
    return out


def resolve_notes(path, lanes_path):
    """Resolve a wiring path to an existing file, or "" if there is none.

    `~` and absolute paths are handled deliberately. Absolute paths did work
    before, but only by the accident that os.path.join returns its right-hand
    side when that side is absolute, which is behaviour nothing tested and
    nothing documented.
    """
    p = os.path.expanduser(path)
    if os.path.isabs(p):
        return os.path.abspath(p) if os.path.exists(p) else ""
    for base in wiring_bases(lanes_path):
        full = os.path.join(base, p)
        if os.path.exists(full):
            return os.path.abspath(full)
    return ""


def lane_files(w, lanes_path):
    """The lane's reachable files: the notes file first, then every match of
    the optional glob, so a lane whose course spans several documents (notes,
    lessons, cadence) is one selector away instead of a folder hunt.

    Returns a list of (label, fullpath). The server only ever opens paths
    from this list, never a path a client named.
    """
    import glob as globmod
    out, seen = [], set()

    def add(full):
        full = os.path.abspath(full)
        if full.lower() in seen or not os.path.isfile(full):
            return
        seen.add(full.lower())
        out.append((os.path.splitext(os.path.basename(full))[0], full))

    if w.get("notes"):
        primary = resolve_notes(w["notes"], lanes_path)
        if primary:
            add(primary)
    g = os.path.expanduser(w.get("glob") or "")
    if g and os.path.isabs(g):
        for m in sorted(globmod.glob(g, recursive=True)):
            add(m)
    elif g:
        # Nearest base that matches anything wins, and the search stops there.
        # A bare `*.md` would otherwise sweep every level up to the repo root.
        for base in wiring_bases(lanes_path):
            hits = sorted(globmod.glob(os.path.join(base, g), recursive=True))
            if hits:
                for m in hits:
                    add(m)
                break
    return out


def lint_lane_decks(wiring, deck_names):
    """The fourth wiring lint, runnable only while Anki is up."""
    errors = []
    for lane, w in wiring.items():
        d = w.get("deck")
        if not d or d == "*":
            continue
        if d not in deck_names and not any(n.startswith(d + "::") for n in deck_names):
            errors.append("lane %s: deck %r is not in Anki" % (lane, d))
    return errors


# ---- behind and load ----------------------------------------------------------
# The two computed numbers that are the point of the surface. `behind` = past
# plan rows that asked for this lane and were never ticked. `load` = what is
# still owed divided by the days left to the lane's fuse; above 1.0 the lane no
# longer fits in the days it has left. "A missed day is never made up" governs
# the day, not the fuse: the fuse is about coverage, so misses roll into load
# as the signal that the plan needs re-cutting.

def cell_counts(text):
    return bool(text) and not NONE_CELL.match(text)


def lane_behind(plan, log, lane, today_iso):
    return sum(1 for iso, row in plan.items()
               if iso < today_iso and cell_counts(row.get(lane, ""))
               and lane not in log.get(iso, set()))


def lane_load(plan, log, lane, today_iso, fuse_iso):
    from datetime import date
    days = (date.fromisoformat(fuse_iso) - date.fromisoformat(today_iso)).days + 1
    if days <= 0:
        return None
    owed = lane_behind(plan, log, lane, today_iso)
    owed += sum(1 for iso, row in plan.items()
                if today_iso <= iso <= fuse_iso and cell_counts(row.get(lane, ""))
                and lane not in log.get(iso, set()))
    return owed / days


# ---- Anki, read-only ----------------------------------------------------------
# Due and new counts per deck over AnkiConnect. Anki only answers while it is
# open, so a closed Anki degrades to an omitted badge rather than an error: a
# morning view that fails because one of four sources is shut is a view nobody
# opens. Port discovery mirrors ankictl: the 8765 default sits inside a range
# Windows commonly reserves, so a working install often listens elsewhere, and
# the addon's own meta.json says where.

ANKI_ADDON_ID = "2055492159"


def _anki_addon_port():
    home = os.path.expanduser("~")
    if sys.platform == "win32":
        base = os.environ.get("APPDATA", os.path.join(home, "AppData", "Roaming"))
    elif sys.platform == "darwin":
        base = os.path.join(home, "Library", "Application Support")
    else:
        base = os.environ.get("XDG_DATA_HOME", os.path.join(home, ".local", "share"))
    for name in ("meta.json", "config.json"):
        try:
            with open(os.path.join(base, "Anki2", "addons21", ANKI_ADDON_ID, name),
                      encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, json.JSONDecodeError):
            continue
        port = data.get("config", data).get("webBindPort")
        if port:
            return int(port)
    return None


def _anki_post(url, action, **params):
    import urllib.request
    payload = json.dumps({"action": action, "version": 6,
                          "params": params}).encode("utf-8")
    req = urllib.request.Request(url, data=payload,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=2) as r:
        body = json.load(r)
    if body.get("error"):
        raise RuntimeError(body["error"])
    return body["result"]


def anki_read(decks):
    """Returns (counts, deck_names) or (None, None) when Anki is closed.

    counts maps deck -> (due, new). A deck of `*` means the whole collection.
    """
    env = os.environ.get("ANKI_CONNECT_URL")
    urls = [env] if env else ["http://127.0.0.1:8765"]
    if not env:
        port = _anki_addon_port()
        if port and port != 8765:
            urls.append("http://127.0.0.1:%d" % port)
    for url in urls:
        try:
            names = _anki_post(url, "deckNames")
            counts = {}
            for d in decks:
                scope = "" if d == "*" else '"deck:%s" ' % d
                counts[d] = (
                    len(_anki_post(url, "findCards",
                                   query=scope + "is:due -is:suspended")),
                    len(_anki_post(url, "findCards",
                                   query=scope + "is:new -is:suspended")))
            return counts, names
        except Exception:
            continue
    return None, None


# ---- Anki, read-only and owner-labelled (10-04, D-05/SCHED-03) -------------
# Anki is an OPTIONAL read-only external card signal. It can never change an
# itembank pacing claim (that would require writing to it, and there are
# deliberately NO Anki write methods in this module -- only deckNames and
# findCards reads), never supplies evidence, and never blocks local report,
# day, or session behavior. When it is unavailable the exact locked copy is
# shown and all local evidence functions remain usable offline.

ANKI_UNAVAILABLE_COPY = "Anki is unavailable; card counts are not shown."


def anki_line(counts):
    """The owner-labelled Anki line, or None. Due/new are summed across the
    requested decks into ONE external signal and never summed with the
    itembank objective counts -- the two owners are never added (D-05)."""
    if not counts:
        return None
    due = sum(v[0] for v in counts.values())
    new = sum(v[1] for v in counts.values())
    return "Anki: %d due · %d new" % (due, new)


def pacing_lines(pacing):
    """One line per subject from a `retention.subject_pacing` dict: the
    ordinary count/cap on the snapshot's local day and the due objective
    count, exactly the numbers the cap gate enforces (D-07)."""
    out = []
    for subj in sorted(pacing["subjects"]):
        s = pacing["subjects"][subj]
        cap = "unlimited" if s["cap"] is None else str(s["cap"])
        out.append("%s: %d of %s ordinary attempts today · %d due objective(s)"
                   % (subj, s["count"], cap, s["due"]))
    return out


def day_pacing(state, cfg=None):
    """The ONE capture per `day` render/--check call (T-10-17): the evidence
    snapshot and every itembank pacing claim (count/cap/due per subject)
    come from this single immutable capture -- never from a tick row, a
    session cursor, an Anki count, or the render cache. The returned pacing
    dict carries the shared claim marker, so no rendered number lacks its
    evidence provenance (D-01/D-13)."""
    if cfg is None:
        from surfaces import settings as _settings
        cfg = _settings.load_settings(
            os.path.dirname(os.path.abspath(state["plan_path"])) or ".")
    events = evidence.capture_events(state["evidence_log"]) \
        if os.path.exists(state["evidence_log"]) else ()
    snapshot = retention.capture(events, cfg=cfg)
    return retention.subject_pacing(snapshot, cap=cfg.get("daily_cap"))


def day_recommendation(state, cfg=None):
    """The Today recommendation payload (10-05 Task 1, D-01/D-05/D-07): the
    due objectives with state/reason/raw counts, the pending-review total,
    and each recommended subject's runtime cap decision -- all from the SAME
    one capture as `day_pacing`, so the card, the disclosure, the cap gate
    and the focused-start request share one snapshot id. Derivation only:
    `retention_view` renders this dict and performs no arithmetic."""
    if cfg is None:
        cfg = settings.load_settings(
            os.path.dirname(os.path.abspath(state["plan_path"])) or ".")
    events = evidence.capture_events(state["evidence_log"]) \
        if os.path.exists(state["evidence_log"]) else ()
    snapshot = retention.capture(events, cfg=cfg)
    summaries = retention.objective_summaries(snapshot)
    recs = []
    for row in summaries:
        st = retention.objective_state(row, snapshot)
        if not st["due"]:
            continue
        recs.append({
            "objective": row["objective"],
            "subject": row["subject"] or "",
            "state": st["state"],
            "reason": retention.risk_reason(row, st, snapshot),
            "attempts": row["attempts"],
            "settled": row["settled"],
            "correct": row["correct"],
            "pending": row["pending"],
            "recent_accuracy": row["recent_accuracy"],
            "highest_hint": row["highest_hint"],
            "average_hint": row["average_hint"],
            "last_evidence": (row["last_evidence"].isoformat()
                              if row["last_evidence"] else None),
            "snapshot_id": snapshot["claim"]["snapshot_id"],
        })
    cap = cfg.get("daily_cap")
    decisions = {}
    # The cap gate covers every subject with activity today -- whether or
    # not it currently has a due recommendation -- so an at-cap subject is
    # always called out (D-07).
    for subj in sorted({row["subject"] for row in summaries
                        if row["subject"]}):
        decisions[subj] = retention.cap_decision(
            snapshot, subject=subj, cap=cap)
    return {
        "objectives": recs,
        "claim": snapshot["claim"],
        "cap": decisions,
        "pending": sum(r["pending"] for r in recs),
    }


def _slugify(text):
    """A DOM-safe id suffix from a subject namespace."""
    return re.sub(r"[^A-Za-z0-9_-]", "-", text or "") or "subject"


def objective_card(o, claim, index=0):
    """One due-objective card: state chip, raw counts, the `Why this
    recommendation` evidence disclosure, and a focused-start action that
    carries ONLY the displayed snapshot id and stable objective -- the
    server re-validates and derives every private authority (D-01/D-04)."""
    state = o.get("state") or "unknown"
    counts = "%d attempt(s), %d settled, %d correct" % (
        o.get("attempts", 0), o.get("settled", 0), o.get("correct", 0))
    hint = ""
    if o.get("highest_hint") is not None:
        hint = " \u00b7 highest hint tier %d" % o["highest_hint"]
    return (
        '<article class="objective" data-objective="%s" data-state="%s" '
        'data-snapshot="%s">'
        "<h3>%s</h3>"
        "<p>%s%s</p>"
        "%s"
        '<button type="button" class="go primary start" '
        'data-objective="%s" data-snapshot="%s">'
        "Start focused session</button>"
        "</article>"
        % (esc(o.get("objective") or ""), esc(state),
           esc(claim.get("snapshot_id") or ""),
           esc(o.get("objective") or ""),
           retention_view.objective_state(state), esc(counts + hint),
           retention_view.evidence_drawer(o, claim, o.get("subject")),
           esc(o.get("objective") or ""),
           esc(claim.get("snapshot_id") or "")))


def today_section(today, info):
    """The 10-05 Today panel, rendered server-side from one snapshot: the
    snapshot stamp, owner-labelled itembank/Anki signals (never summed),
    due-objective cards, the pending badge, and each recommended subject's
    CapGate with recovery links and the one-sitting override dialog. The
    browser performs no derivation (D-01/D-05/D-07/D-08)."""
    e = html.escape
    claim = today.get("claim") or {}
    objs = today.get("objectives") or []
    parts = [retention_view.snapshot_stamp(claim)]
    if objs:
        parts.append(retention_view.signal_card(
            "itembank",
            "%d objective(s) recommended" % len(objs)))
    else:
        parts.append('<p class="empty">%s</p>' % e(
            "Not enough evidence yet. This objective has fewer than the "
            "settled attempts needed for a recommendation. Practice is "
            "still available; no mastery or trend is claimed."))
    for i, o in enumerate(objs):
        parts.append(objective_card(o, claim, index=i))
    if today.get("pending"):
        parts.append(retention_view.pending_review_badge(today["pending"]))
    first_objective = {}
    for o in today.get("objectives") or []:
        first_objective.setdefault(o.get("subject") or "", o.get("objective"))
    for subj, decision in sorted((today.get("cap") or {}).items()):
        oid = "override-%s" % _slugify(subj)
        parts.append(retention_view.cap_gate(
            decision, recovery_href="/report", override_id=oid))
        if decision.get("blocked"):
            parts.append(retention_view.override_dialog(
                oid, subj, oid + "-confirm",
                objective=first_objective.get(subj)))
    # Anki: a separate owner-labelled signal; unavailable uses the locked
    # copy and never alters the itembank snapshot/recommendation (D-05).
    if info.get("anki_unavailable"):
        parts.append('<p class="signal"><span class="owner">Anki</span>%s</p>'
                     % e(ANKI_UNAVAILABLE_COPY))
    elif info.get("anki_line"):
        parts.append(retention_view.signal_card("Anki", info["anki_line"]))
    lessons = today.get("lessons") or {}
    for stem in sorted(lessons):
        parts.append(lesson_complete_form(stem, lessons[stem],
                                          today.get("claim") or {}))
    return '<section class="today">%s</section>' % "".join(parts)


def task_section(snapshot, base):
    """Rank owner-backed assignment rows without turning them into evidence."""
    tasks = snapshot.get("tasks") or []
    issues = snapshot.get("issues") or []
    if not tasks and not issues:
        return ""
    parts = [
        '<section class="task-list" aria-labelledby="task-list-heading">',
        '<div class="task-list-head"><div><p class="eyebrow">Owner-backed to-do</p>',
        '<h2 id="task-list-heading">Assignments</h2></div>',
        '<p>Checking a task edits its declared assignment ledger. Lane ticks stay separate.</p></div>',
        '<p id="task-status" class="task-status" role="status" aria-live="polite"></p>',
    ]
    for bucket in ("Now", "Next", "Later"):
        grouped = [task for task in tasks if task["bucket"] == bucket]
        if not grouped:
            continue
        parts.append('<section class="task-group" aria-labelledby="tasks-%s"><h3 id="tasks-%s">%s</h3>' %
                     (bucket.lower(), bucket.lower(), bucket))
        for task in grouped:
            checked = " checked" if task["checked"] else ""
            parts.append(
                '<article class="task-card%s" data-task-id="%s">'
                '<label class="task-check"><input type="checkbox" class="owner-task"%s '
                'data-task-id="%s" data-revision="%s" '
                'aria-describedby="task-meta-%s"><span><strong>%s</strong>'
                '<small>%s</small></span></label>'
                '<div class="task-quick"><span>%s</span><span>%s</span></div>'
                '<details id="task-meta-%s"><summary>Details</summary><dl>'
                '<div><dt>Purpose</dt><dd>%s</dd></div>'
                '<div><dt>Completion gate</dt><dd>%s</dd></div>'
                '<div><dt>Authoritative source</dt><dd>%s</dd></div>'
                '<div><dt>Owner</dt><dd><code>%s</code>, row %d</dd></div>'
                '</dl></details></article>' % (
                    " done" if task["checked"] else "", esc(task["task_id"]), checked,
                    esc(task["task_id"]), esc(task["revision"]), esc(task["task_id"]),
                    esc(task["name"]), esc(task["course"]), esc(task["due_label"]),
                    esc(task["estimate"]), esc(task["task_id"]), esc(task["purpose"]),
                    esc(task["completion_gate"]), esc(task["source"]),
                    esc(task["owner"]), task["line"]))
        parts.append("</section>")
    for issue in issues:
        parts.append('<div class="task-issue" role="alert"><strong>%s owner</strong>: %s '
                     '<code>%s</code></div>' % (esc(issue["state"]), esc(issue["reason"]),
                                                esc(issue["owner"])))
    parts.append("</section>")
    return "".join(parts)


def lesson_complete_form(stem, headings, claim):
    """The explicit `Mark lesson complete` affordance (10-05 Task 2,
    SCHED-04): a native select of server-resolved lesson headings and a
    button that POSTs to `/api/lesson-complete`. Merely opening/rendering
    the page writes nothing; completion is a separate explicit action that
    appends one lesson_complete event through the runtime."""
    opts = "".join('<option value="%s">%s</option>' % (esc(h), esc(h))
                   for h in headings)
    return (
        '<form class="lesson-complete" data-bank="%s" data-snapshot="%s">'
        '<label>Mark lesson complete <select name="ref">%s</select></label>'
        '<button type="submit" class="go">Mark lesson complete</button>'
        "</form>" % (esc(stem), esc(claim.get("snapshot_id") or ""), opts))


# ---- git evidence --------------------------------------------------------------
# Ticks are an opinion; a commit touching the lane's file is evidence, and the
# two disagreeing is the thing worth seeing. Uncommitted edits count too, since
# the vault's auto-backup commits on its own schedule, not the learner's.

def touched_today(repo_dir, iso):
    import subprocess
    out = set()
    try:
        r = subprocess.run(
            ["git", "-C", repo_dir, "log", "--since", iso + " 00:00",
             "--name-only", "--pretty=format:"],
            capture_output=True, text=True, timeout=5)
        out |= {l.strip().replace("\\", "/").lower()
                for l in r.stdout.splitlines() if l.strip()}
        r = subprocess.run(["git", "-C", repo_dir, "status", "--porcelain"],
                           capture_output=True, text=True, timeout=5)
        out |= {l[3:].strip().strip('"').replace("\\", "/").lower()
                for l in r.stdout.splitlines() if len(l) > 3}
    except Exception:
        return set()
    return out


def open_in_editor(path):
    """Hand a file to the OS default handler, so a markdown file lands in
    whatever the learner already edits it with (Obsidian, VS Code)."""
    import subprocess
    if sys.platform == "win32":
        os.startfile(path)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


def load_day_log(path):
    """Read the tick log, mapping columns by the log's own header row.

    The log predates the sixth lane on some machines, so a five-column file
    must read correctly: a lane the header does not name is simply not done
    that day, never an error and never another lane's mark.

    Kept for two callers only, per plan 01-10 (D-11 extended to the day
    surface): the migration reader (plan 01-11) that brings a pre-evidence
    log's history into `_evidence/evidence.jsonl`, and `cmd_day`'s own
    fallback for a machine that has not run that migration yet. `cmd_day`
    no longer treats this as how it learns what was ticked once an
    evidence log exists -- `evidence.day_log_from_events()` is.
    """
    log, header = {}, list(DAY_LANES)
    if not os.path.exists(path):
        return log
    for raw in open(path, encoding="utf-8"):
        if not raw.lstrip().startswith("|"):
            continue
        cells = split_row(raw)
        if is_rule_row(cells):
            continue
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", cells[0]):
            named = [c for c in cells[1:] if c in DAY_LANES]
            if named:
                header = named
            continue
        log[cells[0]] = set(lane for lane, c in zip(header, cells[1:])
                            if c in DONE_MARKS)
    return log


def day_status(done):
    if all(l in done for l in DAY_LANES):
        return "full"
    if all(l in done for l in FLOOR_LANES):
        return "floor"
    return "miss"


def write_day_log(path, log):
    """Write the tick log's markdown table directly.

    Kept as the fallback writer for the pre-migration path only (plan
    01-10, D-11 extended to the day surface): the day POST route now
    writes through `evidence.render_daily_log()` and an atomic
    tmp-then-`os.replace()`, never through this function, once an evidence
    log exists for the plan being served.
    """
    L = ["# Daily log", "",
         "*Written by `itembank day`. One row per day, `x` where the lane was done.*", "",
         "**Floor** = %s, the smallest day that still counts. **Full** = every lane. "
         "A missed day is never made up; the next day runs its own row at normal size."
         % ", ".join(FLOOR_LANES), "",
         "| Date | " + " | ".join(DAY_LANES) + " | Day |",
         "|---" * (len(DAY_LANES) + 2) + "|"]
    for iso in sorted(log):
        marks = ["x" if l in log[iso] else "." for l in DAY_LANES]
        L.append("| %s | %s | %s |" % (iso, " | ".join(marks), day_status(log[iso])))
    L.append("")
    if os.path.dirname(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as source_handle:
        source_handle.write("\n".join(L))


def day_streak(log, today):
    """Consecutive days up to today that met at least the floor.

    An unfinished today is not counted as a break, because a counter that reads
    zero every morning is an argument for not starting.
    """
    from datetime import timedelta
    d, n = today, 0
    if day_status(log.get(today.isoformat(), set())) == "miss":
        d = today - timedelta(days=1)
    while day_status(log.get(d.isoformat(), set())) != "miss":
        n += 1
        d -= timedelta(days=1)
    return n


def day_history(log, today, span=14):
    from datetime import timedelta
    out = []
    for i in range(span - 1, -1, -1):
        d = (today - timedelta(days=i)).isoformat()
        out.append({"date": d, "status": day_status(log.get(d, set()))})
    return out


# What is left of the day sheet after plan 17A-02 moved the document shell to
# `presentation.surface_shell`. The reset, the reading column, the centring and
# the box-sizing rule are the shell's now and were deleted here rather than
# overridden, because two owners of one layout is the duplication the migration
# exists to remove. The three lines below are the parts that are genuinely
# day's: the 15px/1.45 chrome font this route reads at, the iOS text-size
# guard, and day's tighter column padding, which the shell's 24/64 reading
# padding would otherwise loosen. This sheet is emitted after SHARED_CSS, so it
# still wins the cascade it won when it owned the whole document.
DAY_CSS = resources.read_text("surfaces/assets/day/day.css")


DAY_JS = resources.read_text("surfaces/assets/day/day.js")


def task_text(cell):
    """Plan cells are markdown; the card shows their text, not their markup."""
    return re.sub(r"[*`_]", "", cell)


def lane_badges(li):
    """The badge strip under a lane's task text, from that lane's numbers."""
    out = []
    if li.get("anki"):
        due, new = li["anki"]
        out.append(("", "%d due · %d new" % (due, new)))
    if li.get("behind"):
        out.append(("bad", "behind %d" % li["behind"]))
    load = li.get("load")
    if load is not None:
        cls = "bad" if load > 1.0 else ("warn" if load > 0.85 else "")
        out.append((cls, "load %.2f/day" % load))
    return out


def day_page(iso, weekday, plan_row, done, streak, hist, plan_path, info=None,
             base="", theme_css="", snapshot=None):
    e = html.escape
    info = info or {}
    lane_info = info.get("lanes", {})
    snapshot = snapshot or {}
    rev = snapshot.get("revision") or ""
    columns = snapshot.get("columns") or []
    cells = snapshot.get("cells") or {}
    lanes = []
    for lane in DAY_LANES:
        task = task_text(plan_row.get(lane) or "standing daily item")
        req = ' <span class="req">floor</span>' if lane in FLOOR_LANES else ""
        li = lane_info.get(lane, {})
        dot = ""
        if li.get("evidence") is not None:
            dot = ('<i class="dot%s" title="%s"></i>'
                   % (" on" if li["evidence"] else "",
                      "a change touched this lane's file today" if li["evidence"]
                      else "no change to this lane's file yet today"))
        badges = "".join('<b class="badge %s">%s</b>' % (cls, e(txt))
                         for cls, txt in lane_badges(li))
        badges = '<span class="badges">%s</span>' % badges if badges else ""
        files = li.get("files", [])
        if len(files) > 1:
            opts = "".join('<option value="%d">%s</option>' % (i, e(label))
                           for i, (label, _) in enumerate(files))
            btn = ('<select class="open" data-lane="%s" title="open a file">'
                   '<option value="">open…</option>%s</select>' % (e(lane), opts))
        elif files:
            btn = ('<button class="open" data-lane="%s" data-i="0" '
                   'title="open the notes file">notes</button>' % e(lane))
        else:
            btn = ""
        lanes.append(
            '<label class="lane"><input type="checkbox" name="%s"%s>'
            '<span style="flex:1"><span class="name">%s%s%s</span>'
            '<span class="task">%s</span>%s</span>%s</label>'
            % (e(lane), " checked" if lane in done else "",
               e(lane), req, dot, e(task), badges, btn))
    chips = []
    for name, days in info.get("fuses", []):
        cls = "red" if days <= 3 else ("amber" if days <= 10 else "")
        chips.append('<span class="chip %s">%s <b>%dd</b></span>'
                     % (cls, e(name), days))
    chips = '<div class="chips">%s</div>' % "".join(chips) if chips else ""
    # 10-05: the Today panel -- recommendation cards, cap gates, pending
    # badge, override dialogs and the owner-labelled Anki signal -- all
    # rendered server-side from ONE snapshot (day_recommendation). The
    # itembank pacing block and the notes below remain.
    today_html = ""
    if info.get("today"):
        today_html = today_section(info["today"], info)
    tasks_html = task_section(info.get("tasks") or {}, base)
    # 10-04: the itembank pacing block (per-subject count/cap + due
    # objectives from ONE snapshot, owner-labelled) and the separate
    # owner-labelled Anki line -- two owners, never summed (D-05). The
    # pacing block is rendered fresh on every render; a cached Anki line
    # carries its age note in `notes`.
    pacing = ""
    if info.get("pacing") and info["pacing"].get("subjects"):
        p_rows = "".join(
            '<li><span class="owner">itembank</span> %s: <b>%d</b> of %s '
            "ordinary attempts today \u00b7 <b>%d</b> due objective(s)</li>"
            % (e(subj), s["count"],
               "unlimited" if s["cap"] is None else str(s["cap"]), s["due"])
            for subj, s in sorted(info["pacing"]["subjects"].items()))
        pacing = ('<section class="pacing" aria-label="itembank pacing">'
                  "<ul>%s</ul>"
                  '<p class="snap">itembank snapshot <code>%s</code></p>'
                  "</section>"
                  % (p_rows, e(info["pacing"]["claim"]["snapshot_id"])))
    anki = ""
    if info.get("anki_unavailable"):
        anki = ('<div class="anki"><span class="owner">Anki</span> %s</div>'
                % e(ANKI_UNAVAILABLE_COPY))
    elif info.get("anki_line"):
        anki = ('<div class="anki"><span class="owner">Anki</span> %s</div>'
                % e(info["anki_line"]))
    notes = "".join('<div class="note">%s</div>' % e(m)
                    for m in info.get("notes", []))
    # `base` is the plan-scoped POST prefix (T-2-12): one process serving
    # more than one plan needs each page to say which plan's save/open
    # routes it posts back to, the same fix `__POST__` was for the quiz
    # page. An empty base (the default) preserves the pre-daemon behaviour
    # of posting to root-relative `/save` and `/open`.
    # The date column is the row key and is excluded from the snapshot by
    # *index* (day_document._build_snapshot skips column 0), never by label --
    # a plan whose first header is "DAY", "DATE" or "Date " would otherwise
    # render a phantom input that can never be saved (WR-04).
    editable = [(c, cells.get(c, "")) for c in columns[1:]]
    fields = "".join(
        '<div class="field"><label for="edit-%d">%s</label>'
        '<input class="day-edit" type="text" id="edit-%d" name="%s" value="%s" '
        'autocomplete="off" spellcheck="false">'
        '<span class="err">Fix this cell.</span></div>'
        % (i, e(label), i, e(label), e(value))
        for i, (label, value) in enumerate(editable))
    editor = ""
    if snapshot.get("status") == "ready" and editable:
        editor = (
            '<button type="button" id="edit-btn" class="go">Edit plan</button>'
            '<fieldset class="editor" id="editor">'
            "<legend>Edit plan</legend>"
            '<p class="rev">Plan version <code id="revision-code">%s</code> '
            '<button type="button" id="copy-revision" class="open">copy</button></p>'
            '<div class="fields">%s</div>'
            '<div class="acts">'
            '<button type="button" id="save-edits" data-primary disabled>Save changes</button>'
            '<button type="button" id="discard-edits" class="open">Discard edits</button>'
            "</div>"
            '<div class="status" id="edit-status" role="status" aria-live="polite"></div>'
            '<div class="acts" id="edit-recovery">'
            '<button type="button" id="retry-edits">Retry</button>'
            '<button type="button" id="copy-unavailable">Copy current</button>'
            '<button type="button" id="download-unavailable">Download current</button>'
            "</div>"
            '<section class="conflict" id="conflict" aria-labelledby="conflict-heading">'
            '<h3 id="conflict-heading" tabindex="-1">%s</h3>'
            '<div class="panes">'
            '<div class="pane" id="draft-pane">'
            "<h4>Your draft</h4>"
            '<p class="rev" data-draft-rev></p>'
            '<pre data-draft-cells></pre>'
            '<div class="acts">'
            '<button type="button" id="copy-draft">Copy draft</button>'
            '<button type="button" id="download-draft">Download draft</button>'
            "</div></div>"
            '<div class="pane" id="current-pane">'
            "<h4>Current file</h4>"
            '<p class="rev" data-current-rev></p>'
            '<pre data-current-cells></pre>'
            '<pre id="current-doc" hidden></pre>'
            '<div class="acts">'
            '<button type="button" id="copy-current">Copy current</button>'
            '<button type="button" id="download-current">Download current</button>'
            "</div></div></div>"
            '<div class="acts">'
            '<button type="button" id="reload-current">Reload current</button>'
            '<button type="button" id="reapply-draft">Reapply draft</button>'
            "</div>"
            '<div class="force" id="force-panel">'
            '<label><input type="checkbox" id="force-confirm">'
            "<span>I understand this replaces these edited cells using the "
            "latest plan version.</span></label>"
            '<div class="acts"><button type="button" id="force-btn" disabled>'
            "Force overwrite</button></div>"
            "</div></section>"
            "</fieldset>"
            % (e(rev[:12] if rev else ""), fields,
               "Plan changed outside itembank \u2014 nothing was overwritten."))
    boot = {"date": iso, "lanes": list(DAY_LANES), "floor": list(FLOOR_LANES),
            "base": base, "snapshot": snapshot}
    today = info.get("today") or {}
    if today:
        boot["today"] = {
            "claim": today.get("claim") or {},
            "objectives": [{"objective": o.get("objective"),
                            "state": o.get("state"),
                            "subject": o.get("subject")}
                           for o in (today.get("objectives") or [])],
            "banks": today.get("banks") or [],
            "cap": dict((s, {"count": d.get("count"), "cap": d.get("cap"),
                             "blocked": bool(d.get("blocked"))})
                        for s, d in (today.get("cap") or {}).items()),
            "confirm": OVERRIDE_CONFIRMATION,
        }
    empty_row = ""
    if not plan_row:
        empty_row = '<div class="empty">No plan row for this date.</div>'
    # One shell, composed rather than re-assembled. `doc_title` keeps the tab
    # showing the date while the h1 stays the weekday, which is the split this
    # route always had; `tail` keeps the boot script at the end of the
    # document, where it was. Route content and behaviour are unchanged: the
    # same sections in the same order, the same ids the JS binds to, and the
    # same boot payload.
    body = ("<div class=sub>%s</div>%s"
            "<div class=bar><div class=streak id=streak>%d"
            "<small><span id=streakword>%s</span> unbroken</small></div>"
            "<div class=hist id=hist>%s</div></div>"
            "%s<div class=verdict id=verdict></div>"
            "%s%s"
            "%s"
            "%s"
            "%s%s"
            "%s<div class=note>Plan read from <code>%s</code>. Ticks are written to disk "
            "as you make them.</div>"
            % (e(iso), chips,
               streak, "day" if streak == 1 else "days",
               "".join('<i class="%s" title="%s: %s"></i>'
                       % ("" if h["status"] == "miss" else h["status"], h["date"], h["status"])
                       for h in hist),
               "".join(lanes), today_html, tasks_html, editor, empty_row, pacing, anki,
               notes, e(plan_path)))
    tail = ("<script>window.__day__=%s;\n%s</script>"
            % (presentation.script_safe_json(boot), DAY_JS))
    return presentation.surface_shell(weekday, body, theme_css=theme_css,
                                      doc_title=iso, extra_css=DAY_CSS,
                                      tail=tail)


def lan_address():
    """Best-effort local address, so the page can be opened from a phone.

    The UDP connect sends nothing; it only asks the routing table which local
    interface would be used to reach the internet.
    """
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 53))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


def day_info(plan, log, iso, plan_path, lanes_path):
    """Everything on the page that is not the tick row: fuses, per-lane
    behind/load, Anki counts, git evidence, and the reduced-mode notes.

    Every source except the plan is allowed to be missing; each absence
    becomes one plain sentence on the page instead of a failure.
    """
    from datetime import date
    today = date.fromisoformat(iso)
    info = {"lanes": {}, "fuses": [], "notes": []}

    wiring, fuses, errors = {}, [], []
    if os.path.exists(lanes_path):
        wiring, fuses, errors = parse_lanes(lanes_path)
        errors += lint_lane_paths(wiring, lanes_path)
    else:
        info["notes"].append("No lanes.md beside the plan, so fuses, card "
                             "counts and notes buttons are off.")
    for err in errors:
        info["notes"].append("Wiring: %s (%s)" % (err, os.path.basename(lanes_path)))

    decks = [w["deck"] for w in wiring.values() if w.get("deck")]
    counts, deck_names = anki_read(decks) if decks else (None, None)
    if decks and counts is None:
        # The exact locked unavailable copy (10-UI-SPEC.md); a failure must
        # never render as a stale or zero-looking card count (D-05).
        info["anki_unavailable"] = True
    else:
        info["anki_served"] = True
        line = anki_line(counts)
        if line:
            info["anki_line"] = line
    if deck_names:
        for err in lint_lane_decks(wiring, deck_names):
            info["notes"].append("Wiring: %s (%s)" % (err, os.path.basename(lanes_path)))

    touched = touched_today(os.path.dirname(os.path.abspath(plan_path)) or ".", iso)

    rail = list(fuses)
    for lane, w in wiring.items():
        if w.get("fuse_date"):
            rail.append((w.get("fuse") or lane, w["fuse_date"]))
    for name, fiso in sorted(rail, key=lambda f: f[1]):
        days = (date.fromisoformat(fiso) - today).days
        if days >= 0:
            info["fuses"].append((name, days))

    for lane in DAY_LANES:
        w = wiring.get(lane, {})
        files = lane_files(w, lanes_path) if w else []
        li = {"behind": lane_behind(plan, log, lane, iso), "load": None,
              "anki": counts.get(w.get("deck")) if counts and w.get("deck") else None,
              "evidence": None, "files": files, "has_notes": bool(files)}
        if w.get("fuse_date"):
            li["load"] = lane_load(plan, log, lane, iso, w["fuse_date"])
        if w.get("notes") and touched:
            li["evidence"] = w["notes"].replace("\\", "/").lower() in touched
        info["lanes"][lane] = li
    from surfaces import task_ledger
    assignment_paths = []
    for w in wiring.values():
        declared = w.get("assignments")
        if not declared:
            continue
        resolved = resolve_notes(declared, lanes_path)
        if resolved and resolved not in assignment_paths:
            assignment_paths.append(resolved)
        elif not resolved:
            intended = os.path.expanduser(declared)
            if not os.path.isabs(intended):
                intended = os.path.join(wiring_bases(lanes_path)[0], intended)
            intended = os.path.abspath(intended)
            if intended not in assignment_paths:
                assignment_paths.append(intended)
    info["tasks"] = task_ledger.snapshot(assignment_paths, iso)
    return info


def day_text(iso, weekday, row, log, streak, info):
    done = log.get(iso, set())
    L = ["%s  %s   streak %d" % (iso, weekday, streak)]
    if info["fuses"]:
        L.append("  fuses: " + "  ·  ".join("%s %dd" % f for f in info["fuses"]))
    for lane in DAY_LANES:
        li = info["lanes"].get(lane, {})
        badges = "   ".join(txt for _, txt in lane_badges(li))
        mark = "x" if lane in done else " "
        L.append("  [%s] %-9s %s"
                 % (mark, lane, task_text(row.get(lane) or "standing daily item")))
        if badges:
            L.append("      %-9s %s" % ("", badges))
    L.append("  %s so far. Floor = %s." % (day_status(done), ", ".join(FLOOR_LANES)))
    # 10-04: snapshot-derived per-subject pacing, then the separate
    # owner-labelled Anki signal -- two owners, never summed (D-05).
    if info.get("pacing"):
        for line in pacing_lines(info["pacing"]):
            L.append("  " + line)
        L.append("    itembank snapshot %s" % info["pacing"]["claim"]["snapshot_id"])
    if info.get("anki_unavailable"):
        L.append("  " + ANKI_UNAVAILABLE_COPY)
    elif info.get("anki_line"):
        L.append("  " + info["anki_line"])
    tasks = (info.get("tasks") or {}).get("tasks") or []
    if tasks:
        L.append("  Tasks, owned by their assignment ledgers:")
        for bucket in ("Now", "Next", "Later"):
            grouped = [task for task in tasks if task["bucket"] == bucket]
            if grouped:
                L.append("    %s" % bucket)
                for task in grouped:
                    L.append("      [%s] %s: %s, %s, estimate %s" % (
                        "x" if task["checked"] else " ", task["course"],
                        task["name"], task["due_label"], task["estimate"]))
                    L.append("          purpose: %s; gate: %s; source: %s" % (
                        task["purpose"], task["completion_gate"], task["source"]))
    for issue in (info.get("tasks") or {}).get("issues") or []:
        L.append("  task %s: %s (%s)" % (
            issue["state"], issue["reason"], issue["owner"]))
    for m in info["notes"]:
        L.append("  note: %s" % m)
    if not row:
        L.append("  note: the plan has no row for today, so only the standing lanes show.")
    return "\n".join(L)


def day_state(plan_path, log_path, lanes_path, iso, base=""):
    """Everything `cmd_day` used to compute in its pre-bind block, factored
    out into one mutable dict so a daemon can hold one of these per served
    plan instead of duplicating the block per launch (SURF-01 extended to
    the day surface). Holds the parsed plan, the resolved log/lanes paths,
    the derived evidence log (from `log_path`'s own directory, not the
    plan's -- plan 01-10's decision, preserved exactly), the reconstructed
    tick log, the `iso`/`today` pair, and the 60-second render cache.

    `base` is the plan-scoped POST prefix (T-2-12) `day_render` passes on to
    `day_page`: the default empty string keeps `cmd_day`'s single-plan
    launch posting to root-relative paths exactly as before; a daemon
    serving several plans gives each state its own `/day/<stem>`.

    10-04 (T-10-17): `cache` is explicitly NOT a claim authority. It holds
    at most the lanes info and the external Anki read (whose latency is the
    only reason caching exists at all); `day_render` re-captures the
    evidence snapshot and every itembank pacing claim fresh on every render
    and never reads a pacing value out of this dict.
    """
    from datetime import date
    today = date.fromisoformat(iso)
    plan = parse_plan(plan_path, today.year)

    # A lane tick is an event (D-11 extended to the day surface, plan
    # 01-10); `daily_log.md` is a render of it. The evidence log lives
    # beside wherever the tick log itself lives, so a `--log` override
    # (used by tests, or by a learner who keeps the log somewhere other
    # than beside the plan) keeps its own evidence rather than sharing one
    # with the plan file's directory.
    evidence_log = evidence.log_path(os.path.dirname(os.path.abspath(log_path)) or ".")
    if os.path.exists(evidence_log):
        log = evidence.day_log_from_events(evidence_log)
    else:
        print("note: no _evidence/evidence.jsonl found yet; reading ticks straight "
              "from %s. Run `itembank migrate` to bring this history into the "
              "evidence log." % log_path)
        log = load_day_log(log_path)

    return {"plan": plan, "plan_path": plan_path, "log_path": log_path,
            "lanes_path": lanes_path, "evidence_log": evidence_log, "log": log,
            "iso": iso, "today": today, "base": base,
            "cache": {"at": 0.0, "info": None}}


def day_render(state):
    """The body of `cmd_day`'s old `render()` closure: the 60-second
    `day_info` cache refresh and the `day_page(...)` call, returning
    encoded bytes. The one render function the CLI and the daemon both
    call (D-08 extended to the day surface) -- no second copy of this
    substitution chain lives in `surfaces/daemon.py`.

    10-04 (T-10-17): the render cache can cover only external Anki latency
    and the lanes info. Every itembank pacing claim is captured FRESH on
    every render from ONE evidence snapshot (`day_pacing`), so a cached
    value can never become a pacing or cap claim; a cached Anki line
    discloses its age separately (D-05/SCHED-03) and is never evidence.
    """
    import time
    from surfaces import day_document
    cache = state["cache"]
    if time.time() - cache["at"] > 60 or cache["info"] is None:
        cache["info"] = day_info(state["plan"], state["log"], state["iso"],
                                 state["plan_path"], state["lanes_path"])
        cache["at"] = time.time()
    cfg = settings.load_settings(
        os.path.dirname(os.path.abspath(state["plan_path"])) or ".")
    info = dict(cache["info"])
    info["notes"] = list(info.get("notes", []))
    info["pacing"] = day_pacing(state, cfg)
    info["today"] = day_recommendation(state, cfg)
    banks = state.get("banks") or {}
    lessons = {}
    for stem, path in banks.items():
        try:
            lesson = parse_lesson(path)
        except Exception:
            lesson = None
        if lesson and lesson.get("headings"):
            lessons[stem] = sorted(h["slug"] for h in lesson["headings"])
    info["today"]["banks"] = sorted(banks)
    info["today"]["lessons"] = lessons
    if info.get("anki_line") is not None:
        age = max(0, int(time.time() - cache["at"]))
        info["notes"].append(
            "Anki counts are a cached read (%ds old, up to 60s); Anki is an "
            "external read-only signal and is never evidence." % age)
    row = state["plan"].get(state["iso"], {})
    css = theme_css(cfg)
    snapshot = day_document.snapshot(state["plan_path"],
                                     state["today"].year, state["iso"])
    return day_page(state["iso"], state["today"].strftime("%A"), row,
                    state["log"].get(state["iso"], set()),
                    day_streak(state["log"], state["today"]),
                    day_history(state["log"], state["today"]),
                    state["plan_path"], info,
                    base=state.get("base", ""), theme_css=css,
                    snapshot=snapshot).encode("utf-8")


def apply_day_edit(state, data, force=False):
    """The one surface wrapper around `day_document.save` for the in-page
    editor (plan 04-06). `data` carries `revision` plus `edits`; `force`
    is a daemon-level second confirmation and delegates the same way after
    the daemon's one-use token gate. On `saved`, the parsed plan is reloaded
    and only the render-info cache is invalidated -- tick/evidence state is
    never touched by a plan edit.
    """
    from surfaces import day_document
    revision = data.get("revision") if isinstance(data, dict) else None
    edits = data.get("edits") if isinstance(data, dict) else None
    if not isinstance(edits, dict) or not all(
            isinstance(v, str) for v in edits.values()):
        return {"status": "invalid",
                "reason": "edits must be a map of column to single-line text",
                "draft": edits if isinstance(edits, dict) else {}}
    if not isinstance(revision, str) or not revision:
        return {"status": "invalid",
                "reason": "a SHA-256 revision is required", "draft": edits}
    result = day_document.save(state["plan_path"], state["iso"], edits,
                               revision, force=bool(force))
    if result.get("status") == "saved":
        from datetime import date
        state["plan"] = parse_plan(state["plan_path"], state["today"].year)
        state["cache"]["info"] = None
        state["cache"]["at"] = 0.0
        result["row"] = state["plan"].get(state["iso"], {})
    return result


def apply_task_post(state, data):
    """Resolve a browser task id against a fresh owner snapshot and toggle it."""
    from surfaces import task_ledger
    if not isinstance(data, dict):
        return {"status": "invalid", "reason": "a JSON object is required"}
    if set(data) - {"task_id", "revision", "checked"}:
        return {"status": "invalid", "reason": "unexpected task fields"}
    if not isinstance(data.get("task_id"), str) or not data["task_id"]:
        return {"status": "invalid", "reason": "task_id is required"}
    if not isinstance(data.get("revision"), str) or not data["revision"]:
        return {"status": "invalid", "reason": "revision is required"}
    if not isinstance(data.get("checked"), bool):
        return {"status": "invalid", "reason": "checked must be true or false"}
    state["cache"]["info"] = None
    state["cache"]["at"] = 0.0
    info = day_info(state["plan"], state["log"], state["iso"],
                    state["plan_path"], state["lanes_path"])
    matches = [task for task in (info.get("tasks") or {}).get("tasks", [])
               if task["task_id"] == data["task_id"]]
    if len(matches) != 1:
        return {"status": "conflict",
                "reason": "task is missing or ambiguous; nothing was overwritten"}
    result = task_ledger.set_checked(matches[0], data["checked"],
                                     data["revision"], state["iso"])
    state["cache"]["info"] = None
    state["cache"]["at"] = 0.0
    return result


def apply_day_post(state, kind, data):
    """The body of `cmd_day`'s old POST handler, over one plan's `state`.

    `kind` is `"save"` or `"open"`. The `open` branch keeps resolving
    `(lane, index)` against the server-built `files` list from the last
    render and keeps its bounds check (T-2-10); an out-of-range index
    returns `None`, a sentinel the caller turns into a 404 rather than this
    function calling `send_error` itself, since it has no handler to call it
    on. The `save` branch keeps appending a `day_tick_event` per newly-
    ticked lane and a `retraction_event` per untick (T-2-11), keeps
    filtering lane names against `DAY_LANES`, keeps rebuilding `log` from
    `day_log_from_events`, and keeps writing `daily_log.md` through
    `render_daily_log` plus tmp-then-`os.replace`. Nothing here is
    reimplemented -- it is moved, verbatim in behaviour, from the handler
    this code came from.
    """
    if kind == "open":
        # Only paths this server itself resolved are openable; a client
        # names a lane and an index, never a path.
        files = (state["cache"].get("info") or {}).get("lanes", {}) \
            .get(data.get("lane"), {}).get("files", [])
        i = data.get("i", 0)
        if i is None:
            i = 0
        if not isinstance(i, int) or isinstance(i, bool):
            return None          # caller turns None into a clean client-facing error
        if not (0 <= i < len(files)):
            return None
        open_in_editor(files[i][1])
        return {}

    # save: a tick is an append, an un-tick is a compensating retraction
    # (D-10 extended to the day surface): nothing here is ever deleted,
    # only appended. The lane name and date both come from this POST body
    # (T-1-27) -- the date is validated by evidence.day_tick_event() itself,
    # and the lane is filtered against DAY_LANES below, same as the check
    # this replaces already did.
    evidence_log = state["evidence_log"]
    log = state["log"]
    d = data.get("date") or state["iso"]
    prev_done = log.get(d, set())
    now_done = set(l for l in data.get("done", []) if l in DAY_LANES)
    for lane in sorted(now_done - prev_done):
        evidence.append_event(evidence_log, evidence.day_tick_event(d, lane))
    for lane in sorted(prev_done - now_done):
        target = None
        for ev in evidence.live_events(evidence_log):
            if (ev.get("event_type") == evidence.DAY_TICK_EVENT_TYPE
                    and ev.get("date") == d and ev.get("lane") == lane):
                target = ev.get("event_id")
        if target:
            evidence.append_event(
                evidence_log, evidence.retraction_event(target, "unticked in day"))
    log = evidence.day_log_from_events(evidence_log)
    state["log"] = log
    md = evidence.render_daily_log(log, DAY_LANES, FLOOR_LANES, day_status)
    log_path = state["log_path"]
    tmp = log_path + ".tmp"
    if os.path.dirname(log_path):
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(md)
    os.replace(tmp, log_path)
    return {"streak": day_streak(log, state["today"]),
            "status": day_status(log.get(d, set())),
            "hist": day_history(log, state["today"])}


def _day_edit(a, iso):
    """Structured row/cell edit twin for `itembank day --edit` (plan 04-02).

    Snapshot-only when no `--set` is given; a save requires the SHA-256
    revision the snapshot printed and routes through `day_document.save`, so
    the CLI and the browser editor (plan 04-06) prove the same data-loss
    boundary. This branch never touches the tick/check/due/server paths.
    """
    from surfaces import day_document

    edits = {}
    for item in a.set:
        key, _, value = item.partition("=")
        key = key.strip()
        if not key:
            sys.exit("bad --set %r; want COLUMN=TEXT" % item)
        edits[key] = value
    if not a.edit:
        sys.exit("--edit is required to use --set/--revision/--force")
    if not edits and (a.revision or a.force or a.confirm_force):
        sys.exit("--revision/--force/--confirm-force require at least one --set")
    if a.confirm_force and not a.force:
        sys.exit("--confirm-force requires --force")
    if a.force:
        if a.confirm_force != "OVERWRITE":
            sys.exit("--force requires --confirm-force OVERWRITE")
        if not a.revision:
            sys.exit("--force requires --revision")
    if edits and not a.revision:
        sys.exit("--set requires --revision (the SHA-256 printed by the snapshot)")

    if edits:
        result = day_document.save(a.plan, iso, edits, a.revision, force=a.force)
    else:
        from datetime import date
        result = day_document.snapshot(a.plan, date.fromisoformat(iso).year, iso)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") in ("ready", "saved") else 1


def cmd_day(a):
    """Sit the day cockpit against the daemon, scoped to this one plan.

    Keeps its date resolution, its plan parse and its `sys.exit` on an
    undated plan, keeps the `--check`/`--due` branch exactly as it is (that
    branch never served anything and does not change here), keeps building
    a `day_state`, and keeps printing its banner, the `--lan` phone line via
    `lan_address()` included. It no longer binds its own socket to do any
    of that -- `surfaces/daemon.py` is the only module in the codebase that
    defines an HTTP request handler; this command launches that daemon
    scoped to one plan instead of duplicating its route table (SURF-01's
    consolidation, finished).
    """
    from datetime import date

    today = date.fromisoformat(a.date) if a.date else date.today()
    iso = today.isoformat()
    if a.edit or a.set or a.revision or a.force or a.confirm_force:
        return _day_edit(a, iso)
    plan = parse_plan(a.plan, today.year)
    if not plan:
        sys.exit("no dated rows found in %s. A plan table needs a first column "
                 "like `2026-07-29` or `**Mon Jul 29**`." % a.plan)

    log_path = a.log or os.path.join(
        os.path.dirname(os.path.abspath(a.plan)) or ".", "daily_log.md")
    lanes_path = a.lanes or os.path.join(
        os.path.dirname(os.path.abspath(a.plan)) or ".", "lanes.md")

    if a.check or a.due:
        state = day_state(a.plan, log_path, lanes_path, iso)
        row = state["plan"].get(iso, {})
        info = day_info(state["plan"], state["log"], iso, a.plan, lanes_path)
        # 10-04: the --check branch captures the evidence snapshot ONCE for
        # every itembank pacing claim (count/cap/due per subject via
        # day_pacing), separate from the optional Anki read day_info already
        # did -- two owners, never summed, Anki never blocking (D-05/D-07).
        # There is no render cache here: everything is one fresh capture.
        cfg = settings.load_settings(
            os.path.dirname(os.path.abspath(a.plan)) or ".")
        info["pacing"] = day_pacing(state, cfg)
        print(day_text(iso, today.strftime("%A"), row, state["log"],
                       day_streak(state["log"], today), info))
        print("  log: %s" % log_path)
        return 0

    from surfaces.daemon import serve_scoped

    stem = os.path.splitext(os.path.basename(a.plan))[0]
    plan_dir = os.path.dirname(os.path.abspath(a.plan)) or "."

    print("itembank day")
    print("  %s, %s" % (today.strftime("%A"), iso))
    print("  plan    %s (%d dated rows)" % (a.plan, len(plan)))
    print("  log     %s" % log_path)

    def on_bound(port):
        if a.lan:
            print("  phone   http://%s:%d/day/%s   (same wifi only)"
                  % (lan_address(), port, stem))
        print("  Ticks are saved as you make them. Ctrl-C when you are done.")

    serve_scoped(
        plan_dir, {}, {stem: os.path.abspath(a.plan)}, a.port,
        host="0.0.0.0" if a.lan else "127.0.0.1",
        open_path="/day/%s" % stem, no_open=a.no_open, on_bound=on_bound,
        extra={"day_extra": {stem: {
            "log_path": log_path, "lanes_path": lanes_path, "iso": iso,
        }}})
    return 0
