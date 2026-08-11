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
import html, json, os, re, sys

import evidence
import retention
from surfaces import presentation, settings
from surfaces.theme import theme_css


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
    open(path, "w", encoding="utf-8").write("\n".join(L))


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


DAY_CSS = """
*{box-sizing:border-box}
body{margin:0;padding:14px 16px 24px;font:15px/1.45 -apple-system,BlinkMacSystemFont,
"Segoe UI",Roboto,sans-serif;background:var(--bg);color:var(--ink);
max-width:720px;margin-inline:auto;-webkit-text-size-adjust:100%}
h1{font-size:1.35rem;margin:0 0 1px}
.sub{color:var(--mut);font-size:.85rem;margin-bottom:10px}
.bar{display:flex;align-items:center;gap:14px;padding:9px 14px;border-radius:12px;
background:var(--card);border:1px solid var(--line);margin-bottom:10px}
.streak{font-size:1.6rem;font-weight:700;line-height:1}
.streak small{font-size:.75rem;font-weight:400;color:var(--mut);display:block}
.hist{display:flex;gap:4px;margin-left:auto}
.hist i{width:11px;height:22px;border-radius:3px;background:var(--chip);display:block}
.hist i.floor{background:var(--ok-bg)}
.hist i.full{background:var(--ok)}
label.lane{display:flex;gap:12px;align-items:flex-start;padding:9px 14px;margin-bottom:7px;
background:var(--card);border:1px solid var(--line);border-radius:12px;cursor:pointer;
-webkit-tap-highlight-color:transparent}
label.lane:has(input:checked){background:var(--ok-bg);border-color:var(--ok)}
label.lane input{appearance:none;-webkit-appearance:none;flex:0 0 auto;width:28px;height:28px;
margin:0;border:2px solid var(--line);border-radius:8px;background:var(--card);cursor:pointer}
label.lane input:checked{background:var(--ok);border-color:var(--ok)}
label.lane input:checked::after{content:"";display:block;width:8px;height:15px;margin:1px auto;
border:solid var(--card);border-width:0 3px 3px 0;transform:rotate(45deg)}
.name{font-weight:600}
.name .req{font-weight:400;font-size:.72rem;color:var(--mut);border:1px solid var(--line);
border-radius:20px;padding:1px 7px;margin-left:6px;vertical-align:1px}
.task{color:var(--mut);font-size:.88rem;margin-top:1px;display:block}
.verdict{padding:9px 14px;border-radius:12px;text-align:center;font-weight:600;
background:var(--card);border:1px solid var(--line)}
.verdict.floor{background:var(--ok-bg);border-color:var(--ok)}
.verdict.full{background:var(--ok);border-color:var(--ok);color:var(--card)}
.note{color:var(--mut);font-size:.8rem;margin-top:8px}
.note code{background:var(--chip);padding:1px 5px;border-radius:4px}
.chips{display:flex;flex-wrap:wrap;gap:5px;margin-bottom:10px}
.chip{font-size:.78rem;padding:3px 10px;border-radius:20px;background:var(--card);
border:1px solid var(--line);color:var(--ink);white-space:nowrap}
.chip b{font-weight:700}
.chip.amber{background:var(--chip);border-color:var(--warn);color:var(--warn)}
.chip.red{background:var(--bad-bg);border-color:var(--bad);color:var(--bad)}
.badges{display:flex;flex-wrap:wrap;gap:5px;margin-top:5px}
.badge{font-size:.72rem;padding:1px 8px;border-radius:20px;background:var(--chip);
color:var(--mut);font-weight:500}
.badge.warn{background:var(--chip);color:var(--warn)}
.badge.bad{background:var(--bad-bg);color:var(--bad)}
.dot{display:inline-block;width:8px;height:8px;border-radius:50%;
border:1.5px solid var(--line);margin-left:7px;vertical-align:1px}
.dot.on{background:var(--ok);border-color:var(--ok)}
button.open{flex:0 0 auto;align-self:center;font:inherit;font-size:.75rem;
padding:4px 10px;border-radius:8px;border:1px solid var(--line);background:var(--card);
color:var(--ink);cursor:pointer}
button.open:hover{border-color:var(--accent)}
.editor{display:none;border:1px solid var(--line);border-radius:12px;margin:12px 0;
background:var(--card);padding:14px}
.editor.on{display:block}
.editor legend{font-weight:600;padding:0 6px;font-size:1rem}
.editor .rev{font-size:.8rem;color:var(--mut);margin:0 0 10px;display:flex;
flex-wrap:wrap;gap:8px;align-items:center}
.editor .rev code{background:var(--chip);padding:1px 6px;border-radius:4px}
.editor .fields{display:flex;flex-direction:column;gap:10px}
.editor .field{display:flex;flex-direction:column;gap:4px}
.editor .field label{font-size:.78rem;color:var(--mut);font-weight:600}
.editor input[type=text]{font:inherit;font-size:15px;min-height:44px;padding:8px 10px;
border-radius:8px;border:1px solid var(--line);background:var(--bg);color:var(--ink)}
.editor input[type=text]:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.editor .field.invalid input{border-color:var(--bad);background:var(--bad-bg)}
.editor .field .err{display:none;font-size:.78rem;color:var(--bad)}
.editor .field.invalid .err{display:block}
.editor .status{min-height:24px;font-size:.85rem;color:var(--mut);margin:10px 0 0}
.editor .status.err{color:var(--bad);font-weight:600}
.editor .status.warn{color:var(--warn);font-weight:600}
.editor .status.ok{color:var(--ok);font-weight:600}
.editor .acts{display:flex;flex-wrap:wrap;gap:10px;margin-top:12px}
.editor #edit-recovery{display:none}
.editor #edit-recovery.on{display:flex}
.editor button{font:inherit;font-size:.9rem;min-height:44px;padding:8px 14px;border-radius:8px;
border:1px solid var(--line);background:var(--bg);color:var(--ink);cursor:pointer}
.editor button:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.editor button[data-primary]{background:var(--accent-soft);border-color:var(--accent);
color:var(--accent);font-weight:600}
.editor button:disabled{opacity:.55;cursor:default}
.editor .conflict{display:none;margin-top:12px;border-top:1px solid var(--line);padding-top:12px}
.editor .conflict.on{display:block}
.editor .conflict h3{margin:0 0 6px;font-size:1.05rem;color:var(--bad)}
.editor .panes{display:flex;flex-wrap:wrap;gap:12px;margin-top:8px}
.editor .pane{flex:1 1 280px;min-width:0}
.editor .pane h4{margin:0 0 4px;font-size:.85rem;color:var(--mut)}
.editor .pane .rev{font-size:.72rem;color:var(--mut);margin:0 0 6px}
.editor .pane pre{max-height:220px;overflow:auto;background:var(--bg);border:1px solid var(--line);
border-radius:8px;padding:10px;font:12px/1.45 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
color:var(--ink);white-space:pre-wrap;overflow-wrap:anywhere;margin:0 0 8px}
.editor .pane .acts{gap:8px;margin-top:0}
.editor .pane button{min-height:40px;font-size:.8rem;padding:6px 10px}
.editor .force{display:none;margin-top:12px;border-top:1px solid var(--line);padding-top:12px}
.editor .force.on{display:block}
.editor .force label{display:flex;gap:8px;align-items:flex-start;font-size:.85rem;
color:var(--bad)}
.editor .force input[type=checkbox]{width:22px;height:22px;flex:0 0 auto;margin:1px 0 0;
accent-color:var(--bad)}
@media (max-width:520px){
.editor .panes{flex-direction:column}
.editor .acts button{flex:1 1 auto}}
.pacing,.anki{margin:10px 0;padding:10px 12px;border:1px solid var(--line);
border-radius:10px;background:var(--bg)}
.pacing ul{margin:0;padding:0;list-style:none;display:flex;flex-direction:column;gap:4px}
.pacing li,.anki{font-size:.9rem;color:var(--ink)}
.pacing .snap{font-size:.72rem;color:var(--mut);margin:6px 0 0}
.owner{font-weight:600;color:var(--accent);text-transform:uppercase;font-size:.7rem;
letter-spacing:.04em;margin-right:6px}
"""


DAY_JS = """
var D=window.__day__;
var SNAP=D.snapshot||{};
var INVALID_COPY="Plan not saved. Fix the highlighted cells and try again.";
var CONFLICT_HEADING="Plan changed outside itembank \u2014 nothing was overwritten.";
var FORCE_COPY="I understand this replaces these edited cells using the latest plan version.";
var baseline={},draft={},forceToken="",forceDraftHash="",forceRevision="",dirty=false;
var status=document.getElementById('edit-status');
var saveBtn=document.getElementById('save-edits');
var forcePanel=document.getElementById('force-panel');
function revShort(r){return r?r.slice(0,12):"";}
function inputs(){return [].slice.call(document.querySelectorAll('.editor input[type=text]'));}
function values(){
 var o={};
 inputs().forEach(function(i){o[i.name]=i.value;});
 return o;
}
function setDraft(o){draft={};Object.keys(o).forEach(function(k){draft[k]=o[k];});}
function setBaseline(o){baseline={};Object.keys(o).forEach(function(k){baseline[k]=o[k];});}
function isDirty(){
 var v=values(),k;
 for(k in baseline){if(v[k]!==baseline[k]){return true;}}
 return false;
}
function setDirty(){
 dirty=isDirty();
 saveBtn.disabled=!dirty;
 if(dirty){window.addEventListener('beforeunload',beforeunload);}
 else{window.removeEventListener('beforeunload',beforeunload);}
}
function beforeunload(e){
 e.preventDefault();
 e.returnValue="You have unsaved plan changes.";
}
function say(t,cls){status.textContent=t;status.className="status "+(cls||"");}
function draftHash(o){
 var keys=Object.keys(o).sort(),parts=[];
 keys.forEach(function(k){parts.push(JSON.stringify(k)+":"+JSON.stringify(o[k]));});
 return parts.join(",");
}
function highlightErrors(fields){
 inputs().forEach(function(i){
  i.closest('.field').classList.toggle('invalid',fields.indexOf(i.name)>=0);
 });
}
function post(path,payload,cb){
 var r=new XMLHttpRequest();
 r.open('POST',D.base+path);
 r.setRequestHeader('Content-Type','application/json');
 r.onload=function(){try{cb(JSON.parse(r.responseText));}catch(e){}};
 r.send(JSON.stringify(payload));
}
function copyText(t,btn){
 if(navigator.clipboard&&navigator.clipboard.writeText){
  navigator.clipboard.writeText(t).then(function(){btn.textContent="Copied";});
 }else{
  var ta=document.createElement('textarea');
  ta.value=t;ta.style.position='fixed';ta.style.opacity='0';
  document.body.appendChild(ta);ta.select();
  try{document.execCommand('copy');btn.textContent="Copied";}catch(e){}
  document.body.removeChild(ta);
 }
}
function downloadText(name,t){
 var a=document.createElement('a');
 a.href=URL.createObjectURL(new Blob([t],{type:'text/plain'}));
 a.download=name;a.click();
 setTimeout(function(){URL.revokeObjectURL(a.href);},1000);
}
function fillPanels(draftCells,currentCells,currentDoc,draftRev,currentRev){
 var d=document.getElementById('draft-pane'),c=document.getElementById('current-pane');
 d.querySelector('[data-draft-cells]').textContent=
  draftCells?JSON.stringify(draftCells,null,1):"";
 d.querySelector('[data-draft-rev]').textContent="Your draft \u00b7 revision "+revShort(draftRev);
 c.querySelector('[data-current-cells]').textContent=
  currentCells?JSON.stringify(currentCells,null,1):"";
 c.querySelector('[data-current-rev]').textContent="Current file \u00b7 revision "+revShort(currentRev);
 document.getElementById('current-doc').textContent=currentDoc||"";
}
function showConflict(d){
 forceToken=d.force_token||"";
 forceDraftHash=d.force_draft_hash||"";
 forceRevision=d.current&&d.current.revision?d.current.revision:SNAP.revision;
 setDraft(values());
 fillPanels(draft,currentCells(d),(d.current&&d.current.document)||SNAP.document,
   SNAP.revision,d.current.revision);
 document.getElementById('conflict').classList.add('on');
 forcePanel.classList.add('on');
 document.getElementById('force-confirm').checked=false;
 document.getElementById('force-btn').disabled=true;
 var h=document.getElementById('conflict-heading');
 h.textContent=CONFLICT_HEADING;
 h.focus();
}
function currentCells(d){
 return d.current&&d.current.cells?d.current.cells:SNAP.cells;
}
function saveEdits(){
 var changed={},v=values(),k,forceRev=SNAP.revision;
 if(document.getElementById('conflict').classList.contains('on')){
  forceRev=forceRevision;
 }
 for(k in baseline){if(v[k]!==baseline[k]){changed[k]=v[k];}}
 if(!Object.keys(changed).length){return;}
 say("Saving\u2026");
 saveBtn.disabled=true;
 post('/edit',{revision:forceRev,edits:changed},function(d){
  if(d.status==="saved"){
   SNAP.revision=d.revision;
   setBaseline(d.cells);
   setDraft({});
   document.getElementById('conflict').classList.remove('on');
   forcePanel.classList.remove('on');
   forceToken="";forceDraftHash="";
   say("Saved. Plan version "+revShort(d.revision)+".","ok");
   location.reload();
   return;
  }
  if(d.status==="conflict"){showConflict(d);return;}
  highlightErrors(d.errors||[]);
  if(d.status==="invalid"){
   say(INVALID_COPY,"err");
  }else{
   say((d.reason||"Plan not available.")+" Retry, or copy/download the plan and reload.","warn");
   document.getElementById('current-doc').textContent=d.document||SNAP.document||"";
   document.getElementById('edit-recovery').classList.add('on');
  }
  saveBtn.disabled=!isDirty();
 });
}
function retryEdits(){
 document.getElementById('edit-recovery').classList.remove('on');
 saveEdits();
}
function reloadCurrent(){
 say("Reloading current plan\u2026");
 getPage();
}
function reapplyDraft(){
 var k;
 for(k in draft){var i=document.querySelector('.editor input[name="'+k+'"]');if(i){i.value=draft[k];}}
 highlightErrors([]);
 document.getElementById('conflict').classList.remove('on');
 forcePanel.classList.remove('on');
 forceToken="";forceDraftHash="";
 setDirty();
 var first=inputs()[0];
 if(first){first.focus();}
}
function getPage(){
 var r=new XMLHttpRequest();
 r.open('GET',D.base);
 r.onload=function(){
  try{
   var m=r.responseText.match(/window\.__day__=(\{.*?\});\n/s);
   if(!m){return;}
   var b=JSON.parse(m[1]);
   SNAP=b.snapshot||SNAP;
   setBaseline(SNAP.cells||{});
   inputs().forEach(function(i){i.value=baseline[i.name]||"";});
   document.getElementById('revision-code').textContent=revShort(SNAP.revision);
   say("Current plan reloaded. Your recoverable draft is still available.","warn");
   setDirty();
  }catch(e){}
 };
 r.send();
}
function openFile(lane,i){
 var r=new XMLHttpRequest();
 r.open('POST',D.base+'/open');
 r.setRequestHeader('Content-Type','application/json');
 r.send(JSON.stringify({lane:lane,i:i}));
}
function editMode(){
 document.getElementById('editor').classList.add('on');
 document.getElementById('edit-btn').disabled=true;
 var first=inputs()[0];
 if(first){first.focus();}
}
function initEditor(){
 setBaseline(SNAP.cells||{});
 setDraft({});
 forceRevision=SNAP.revision;
 setDirty();
 document.getElementById('edit-btn').addEventListener('click',function(){editMode();});
 saveBtn.addEventListener('click',saveEdits);
 document.getElementById('copy-revision').addEventListener('click',function(){
  copyText(SNAP.revision||"",this);
 });
 document.getElementById('discard-edits').addEventListener('click',function(){
  inputs().forEach(function(i){i.value=baseline[i.name]||"";});
  highlightErrors([]);
  setDraft({});
  setDirty();
  say("Edits discarded.","");
 });
 inputs().forEach(function(i){
  i.addEventListener('input',setDirty);
 });
 document.getElementById('reload-current').addEventListener('click',reloadCurrent);
 document.getElementById('reapply-draft').addEventListener('click',reapplyDraft);
 document.getElementById('retry-edits').addEventListener('click',retryEdits);
 document.getElementById('copy-draft').addEventListener('click',function(){
  copyText(JSON.stringify(draft,null,1),this);
 });
 document.getElementById('download-draft').addEventListener('click',function(){
  downloadText("draft-plan.json",JSON.stringify(draft,null,1));
 });
 document.getElementById('copy-current').addEventListener('click',function(){
  copyText(document.getElementById('current-doc').textContent,this);
 });
 document.getElementById('download-current').addEventListener('click',function(){
  downloadText("current-plan.md",document.getElementById('current-doc').textContent);
 });
 document.getElementById('copy-unavailable').addEventListener('click',function(){
  copyText(document.getElementById('current-doc').textContent,this);
 });
 document.getElementById('download-unavailable').addEventListener('click',function(){
  downloadText("current-plan.md",document.getElementById('current-doc').textContent);
 });
 document.getElementById('force-confirm').addEventListener('change',function(){
  document.getElementById('force-btn').disabled=!this.checked;
 });
 document.getElementById('force-btn').addEventListener('click',function(){
  var v=values(),changed={},k;
  for(k in baseline){if(v[k]!==baseline[k]){changed[k]=v[k];}}
  if(!Object.keys(changed).length){return;}
  var hash=draftHash(changed);
  if(hash!==forceDraftHash){forceToken="";forceDraftHash="";return;}
  say("Confirming force overwrite\u2026");
  this.disabled=true;
  post('/edit',{revision:forceRevision,edits:changed,force_token:forceToken,
                confirmation:FORCE_COPY,force:true},function(d){
   if(d.status==="saved"){
    SNAP.revision=d.revision;
    setBaseline(d.cells);
    forceToken="";forceDraftHash="";
    document.getElementById('conflict').classList.remove('on');
    forcePanel.classList.remove('on');
    say("Force overwrite saved. Plan version "+revShort(d.revision)+".","ok");
    location.reload();
    return;
   }
   document.getElementById('force-confirm').checked=false;
   document.getElementById('force-btn').disabled=true;
   if(d.status==="conflict"){
    showConflict(d);
   }else{
    say((d.reason||"Force overwrite not completed.")+" Your draft is still here.","err");
   }
  });
 });
}
function paint(){
 var on=[].slice.call(document.querySelectorAll('input[type=checkbox].lane'))
        .filter(function(i){return i.checked}).map(function(i){return i.name});
 var floor=D.floor.every(function(l){return on.indexOf(l)>=0});
 var full=D.lanes.every(function(l){return on.indexOf(l)>=0});
 var v=document.getElementById('verdict');
 v.className='verdict '+(full?'full':floor?'floor':'');
 v.textContent=full?'Full day. Done.':floor?'Floor met. This day counts.'
   :'Floor needs '+D.floor.filter(function(l){return on.indexOf(l)<0}).join(', ')+'.';
 return on;
}
function saveTicks(){
 var on=paint();
 var r=new XMLHttpRequest();
 r.open('POST',D.base+'/save');
 r.setRequestHeader('Content-Type','application/json');
 r.onload=function(){
  try{
   var d=JSON.parse(r.responseText);
   document.getElementById('streak').firstChild.nodeValue=d.streak;
   document.getElementById('streakword').textContent=d.streak===1?'day':'days';
   var h=document.getElementById('hist');h.innerHTML='';
   d.hist.forEach(function(x){var i=document.createElement('i');
     i.className=x.status==='miss'?'':x.status;i.title=x.date+': '+x.status;h.appendChild(i)});
  }catch(e){}
 };
 r.send(JSON.stringify({date:D.date,done:on}));
}
document.addEventListener('change',function(ev){
 var el=ev.target;
 if(el.classList&&el.classList.contains('open')){
  if(el.value!==''){openFile(el.getAttribute('data-lane'),parseInt(el.value,10));el.value='';}
  return;
 }
 if(el.classList&&el.classList.contains('day-edit')){return;}
 saveTicks();
});
document.addEventListener('click',function(ev){
 var b=ev.target.closest&&ev.target.closest('button.open');
 if(!b)return;
 ev.preventDefault();
 openFile(b.getAttribute('data-lane'),parseInt(b.getAttribute('data-i')||'0',10));
});
if(SNAP.status==="ready"){
 initEditor();
}
paint();
"""


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
    empty_row = ""
    if not plan_row:
        empty_row = '<div class="empty">No plan row for this date.</div>'
    return ("<!doctype html><html lang=en><head><meta charset=utf-8>"
            "<meta name=viewport content='width=device-width,initial-scale=1'>"
            "<title>%s</title><style>%s</style></head><body>"
            "<h1>%s</h1><div class=sub>%s</div>%s"
            "<div class=bar><div class=streak id=streak>%d"
            "<small><span id=streakword>%s</span> unbroken</small></div>"
            "<div class=hist id=hist>%s</div></div>"
            "%s<div class=verdict id=verdict></div>"
            "%s"
            "%s"
            "%s%s"
            "%s<div class=note>Plan read from <code>%s</code>. Ticks are written to disk "
            "as you make them.</div>"
            "<script>window.__day__=%s;\n%s</script></body></html>"
            % (e(iso), theme_css + DAY_CSS, e(weekday), e(iso), chips,
               streak, "day" if streak == 1 else "days",
               "".join('<i class="%s" title="%s: %s"></i>'
                       % ("" if h["status"] == "miss" else h["status"], h["date"], h["status"])
                       for h in hist),
               "".join(lanes), editor, empty_row, pacing, anki, notes,
               e(plan_path),
               presentation.script_safe_json(boot), DAY_JS))


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
