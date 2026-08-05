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

import server


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
"Segoe UI",Roboto,sans-serif;background:#fbfbfa;color:#1a1a1a;
max-width:720px;margin-inline:auto;-webkit-text-size-adjust:100%}
h1{font-size:1.35rem;margin:0 0 1px}
.sub{color:#6b6b6b;font-size:.85rem;margin-bottom:10px}
.bar{display:flex;align-items:center;gap:14px;padding:9px 14px;border-radius:12px;
background:#fff;border:1px solid #e5e3df;margin-bottom:10px}
.streak{font-size:1.6rem;font-weight:700;line-height:1}
.streak small{font-size:.75rem;font-weight:400;color:#6b6b6b;display:block}
.hist{display:flex;gap:4px;margin-left:auto}
.hist i{width:11px;height:22px;border-radius:3px;background:#e5e3df;display:block}
.hist i.floor{background:#b9d4b0}
.hist i.full{background:#4f8f3f}
label.lane{display:flex;gap:12px;align-items:flex-start;padding:9px 14px;margin-bottom:7px;
background:#fff;border:1px solid #e5e3df;border-radius:12px;cursor:pointer;
-webkit-tap-highlight-color:transparent}
label.lane:has(input:checked){background:#f2f7f0;border-color:#b9d4b0}
label.lane input{appearance:none;-webkit-appearance:none;flex:0 0 auto;width:28px;height:28px;
margin:0;border:2px solid #c9c6c0;border-radius:8px;background:#fff;cursor:pointer}
label.lane input:checked{background:#4f8f3f;border-color:#4f8f3f}
label.lane input:checked::after{content:"";display:block;width:8px;height:15px;margin:1px auto;
border:solid #fff;border-width:0 3px 3px 0;transform:rotate(45deg)}
.name{font-weight:600}
.name .req{font-weight:400;font-size:.72rem;color:#6b6b6b;border:1px solid #ddd;
border-radius:20px;padding:1px 7px;margin-left:6px;vertical-align:1px}
.task{color:#4a4a4a;font-size:.88rem;margin-top:1px;display:block}
.verdict{padding:9px 14px;border-radius:12px;text-align:center;font-weight:600;
background:#fff;border:1px solid #e5e3df}
.verdict.floor{background:#f2f7f0;border-color:#b9d4b0}
.verdict.full{background:#4f8f3f;border-color:#4f8f3f;color:#fff}
.note{color:#6b6b6b;font-size:.8rem;margin-top:8px}
.note code{background:#efeeec;padding:1px 5px;border-radius:4px}
.chips{display:flex;flex-wrap:wrap;gap:5px;margin-bottom:10px}
.chip{font-size:.78rem;padding:3px 10px;border-radius:20px;background:#fff;
border:1px solid #e5e3df;color:#4a4a4a;white-space:nowrap}
.chip b{font-weight:700}
.chip.amber{background:#fdf3e3;border-color:#e8c98a;color:#7a5b16}
.chip.red{background:#fbe9e7;border-color:#e5a099;color:#8f2a1e}
.badges{display:flex;flex-wrap:wrap;gap:5px;margin-top:5px}
.badge{font-size:.72rem;padding:1px 8px;border-radius:20px;background:#efeeec;
color:#5a5a58;font-weight:500}
.badge.warn{background:#fdf3e3;color:#7a5b16}
.badge.bad{background:#fbe9e7;color:#8f2a1e}
.dot{display:inline-block;width:8px;height:8px;border-radius:50%;
border:1.5px solid #c9c6c0;margin-left:7px;vertical-align:1px}
.dot.on{background:#4f8f3f;border-color:#4f8f3f}
button.open{flex:0 0 auto;align-self:center;font:inherit;font-size:.75rem;
padding:4px 10px;border-radius:8px;border:1px solid #dcdad6;background:#fff;
color:#4a4a4a;cursor:pointer}
button.open:hover{border-color:#b9b6b0}
@media (prefers-color-scheme:dark){
body{background:#16171a;color:#e9e9e7}
.bar,label.lane,.verdict{background:#212226;border-color:#33343a}
.hist i{background:#33343a}
.sub,.streak small,.task,.note,.name .req{color:#9a9a98}
label.lane input{background:#212226;border-color:#4a4b52}
label.lane:has(input:checked){background:#1e2a1c;border-color:#3f6f33}
.verdict.floor{background:#1e2a1c;border-color:#3f6f33}
.note code{background:#2b2c31}
.chip{background:#212226;border-color:#33343a;color:#b9b9b7}
.chip.amber{background:#33290f;border-color:#6e5719;color:#e2bd66}
.chip.red{background:#3a1d19;border-color:#7c3a30;color:#e8988c}
.badge{background:#2b2c31;color:#a5a5a3}
.badge.warn{background:#33290f;color:#e2bd66}
.badge.bad{background:#3a1d19;color:#e8988c}
.dot{border-color:#4a4b52}
button.open{background:#212226;border-color:#4a4b52;color:#b9b9b7}}
"""


DAY_JS = """
var D=window.__day__;
function paint(){
 var on=[].slice.call(document.querySelectorAll('input')).filter(function(i){return i.checked})
        .map(function(i){return i.name});
 var floor=D.floor.every(function(l){return on.indexOf(l)>=0});
 var full=D.lanes.every(function(l){return on.indexOf(l)>=0});
 var v=document.getElementById('verdict');
 v.className='verdict '+(full?'full':floor?'floor':'');
 v.textContent=full?'Full day. Done.':floor?'Floor met. This day counts.'
   :'Floor needs '+D.floor.filter(function(l){return on.indexOf(l)<0}).join(', ')+'.';
 return on;
}
function save(){
 var on=paint();
 var r=new XMLHttpRequest();
 r.open('POST','/save');
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
function openFile(lane,i){
 var r=new XMLHttpRequest();
 r.open('POST','/open');
 r.setRequestHeader('Content-Type','application/json');
 r.send(JSON.stringify({lane:lane,i:i}));
}
document.addEventListener('change',function(ev){
 var el=ev.target;
 if(el.classList&&el.classList.contains('open')){
  if(el.value!==''){openFile(el.getAttribute('data-lane'),parseInt(el.value,10));el.value='';}
  return;
 }
 save();
});
document.addEventListener('click',function(ev){
 var b=ev.target.closest&&ev.target.closest('button.open');
 if(!b)return;
 ev.preventDefault();
 openFile(b.getAttribute('data-lane'),parseInt(b.getAttribute('data-i')||'0',10));
});
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


def day_page(iso, weekday, plan_row, done, streak, hist, plan_path, info=None):
    e = html.escape
    info = info or {}
    lane_info = info.get("lanes", {})
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
    notes = "".join('<div class="note">%s</div>' % e(m)
                    for m in info.get("notes", []))
    boot = {"date": iso, "lanes": list(DAY_LANES), "floor": list(FLOOR_LANES)}
    return ("<!doctype html><html lang=en><head><meta charset=utf-8>"
            "<meta name=viewport content='width=device-width,initial-scale=1'>"
            "<title>%s</title><style>%s</style></head><body>"
            "<h1>%s</h1><div class=sub>%s</div>%s"
            "<div class=bar><div class=streak id=streak>%d"
            "<small><span id=streakword>%s</span> unbroken</small></div>"
            "<div class=hist id=hist>%s</div></div>"
            "%s<div class=verdict id=verdict></div>"
            "%s<div class=note>Plan read from <code>%s</code>. Ticks are written to disk "
            "as you make them.</div>"
            "<script>window.__day__=%s;\n%s</script></body></html>"
            % (e(iso), DAY_CSS, e(weekday), e(iso), chips,
               streak, "day" if streak == 1 else "days",
               "".join('<i class="%s" title="%s: %s"></i>'
                       % ("" if h["status"] == "miss" else h["status"], h["date"], h["status"])
                       for h in hist),
               "".join(lanes), notes, e(plan_path),
               json.dumps(boot), DAY_JS))


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
        info["notes"].append("Anki is closed, so card counts are omitted.")
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
    for m in info["notes"]:
        L.append("  note: %s" % m)
    if not row:
        L.append("  note: the plan has no row for today, so only the standing lanes show.")
    return "\n".join(L)


def cmd_day(a):
    import webbrowser, threading
    from datetime import date

    today = date.fromisoformat(a.date) if a.date else date.today()
    iso = today.isoformat()
    plan = parse_plan(a.plan, today.year)
    if not plan:
        sys.exit("no dated rows found in %s. A plan table needs a first column "
                 "like `2026-07-29` or `**Mon Jul 29**`." % a.plan)
    row = plan.get(iso, {})

    log_path = a.log or os.path.join(
        os.path.dirname(os.path.abspath(a.plan)) or ".", "daily_log.md")
    lanes_path = a.lanes or os.path.join(
        os.path.dirname(os.path.abspath(a.plan)) or ".", "lanes.md")
    log = load_day_log(log_path)

    if a.check or a.due:
        info = day_info(plan, log, iso, a.plan, lanes_path)
        print(day_text(iso, today.strftime("%A"), row, log,
                       day_streak(log, today), info))
        print("  log: %s" % log_path)
        return 0

    cache = {"at": 0.0, "info": None}

    def render():
        import time
        if time.time() - cache["at"] > 60 or cache["info"] is None:
            cache["info"] = day_info(plan, log, iso, a.plan, lanes_path)
            cache["at"] = time.time()
        return day_page(iso, today.strftime("%A"), row, log.get(iso, set()),
                        day_streak(log, today), day_history(log, today),
                        a.plan, cache["info"]).encode("utf-8")

    class H(server.Handler):
        def do_GET(self):
            if self.path not in ("/", "/index.html"):
                self.send_error(404)
                return
            self.send_html(render())

        def do_POST(self):
            if self.path not in ("/save", "/open"):
                self.send_error(404)
                return
            try:
                data = self.read_json()
                if self.path == "/open":
                    # Only paths this server itself resolved are openable; a
                    # client names a lane and an index, never a path.
                    files = (cache["info"] or {}).get("lanes", {}) \
                        .get(data.get("lane"), {}).get("files", [])
                    i = int(data.get("i") or 0)
                    if not (0 <= i < len(files)):
                        self.send_error(404)
                        return
                    open_in_editor(files[i][1])
                    out = {}
                else:
                    d = data.get("date") or iso
                    log[d] = set(l for l in data.get("done", []) if l in DAY_LANES)
                    write_day_log(log_path, log)
                    out = {"streak": day_streak(log, today),
                           "status": day_status(log[d]),
                           "hist": day_history(log, today)}
            except Exception as exc:
                self.send_error(500, str(exc))
                return
            self.send_json(out)

    srv = server.bind(H, a.port, "0.0.0.0" if a.lan else "127.0.0.1")

    with srv:
        port = srv.server_address[1]
        print("itembank day")
        print("  %s, %s" % (today.strftime("%A"), iso))
        print("  plan    %s (%d dated rows)" % (a.plan, len(plan)))
        print("  log     %s" % log_path)
        print("  url     http://127.0.0.1:%d/" % port)
        if a.lan:
            print("  phone   http://%s:%d/   (same wifi only)" % (lan_address(), port))
        print("  Ticks are saved as you make them. Ctrl-C when you are done.")
        sys.stdout.flush()
        if not a.no_open:
            threading.Timer(0.4, lambda: webbrowser.open("http://127.0.0.1:%d/" % port)).start()
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            print("\nstopped. Today: %s. Streak %d."
                  % (day_status(log.get(iso, set())), day_streak(log, today)))
    return 0
