"""The command palette: one keystroke that reaches everything a surface has.

The 2026-09-05 surface grid measured the problem this answers. 64 commands
and 46 routes exist; a person meets perhaps six of them, because the shelf
links courses, a course links its areas, and everything else is reachable
only by knowing it is there. A palette does not add authority and does not
add a capability. It makes the ones already built findable, which is the
cheapest door in the grid.

What it offers, and the three kinds are deliberately separate:

- **Go**, a navigation target that already exists as a GET route: a course,
  one of its areas, a bank's quiz or lesson or study view, the day plan, the
  report, settings, activity. Selecting one navigates.
- **Do**, an action the browser can already perform on its own behalf:
  switching the look through `POST /api/theme`, which is the same writer the
  settings page uses. Nothing destructive is offered, and nothing that
  settles a mark, scores an answer, or changes a course is offered at all,
  because those either do not exist yet as routes or belong to a surface
  that can show their consequences first.
- **Run**, a CLI command with its own help text, shown so it can be read and
  copied. It is never executed from here: the palette is a browser surface
  and the CLI is a separate one, and a browser that could run arbitrary
  local commands would be a different security posture than this project
  has. Copying is the honest affordance, and it is the one that makes 64
  commands discoverable at all.

The index is built server-side from the shipped surfaces, never from a
hand-kept list: courses come from `ia.course_shelf_state`, banks from the
daemon's own scan, commands from `cli.build_parser()`. A command added to
the parser appears in the palette with no further work.
"""
import html
import json

from surfaces import ia, looks


# Verbs, in the order the palette groups them. `run` is last because it is
# the one that does not act.
KINDS = ("go", "do", "run")

KIND_LABELS = {"go": "Go", "do": "Do", "run": "Run in a terminal"}

PLACEHOLDER = "Search courses, views, looks and commands"

EMPTY_COPY = "Nothing matches that."

HINT_COPY = ("Enter opens. Escape closes. A command is shown so you can "
             "copy it, never run from here.")


def _entry(kind, label, detail="", href="", action=None, copy=""):
    return {"kind": kind, "label": label, "detail": detail, "href": href,
            "action": action, "copy": copy}


def go_entries(root, banks, course_module=None):
    """Every navigation target the daemon actually serves right now."""
    out = [
        _entry("go", "Courses", "The shelf: every course this install holds",
               "/"),
        _entry("go", "Today", "What is due across every subject", "/day"),
        _entry("go", "Report", "The evidence report", "/report"),
        _entry("go", "Activity", "Durable agent and maintenance jobs",
               "/activity"),
        _entry("go", "Settings", "Look, theme and accent", "/settings"),
    ]
    try:
        shelf = ia.course_shelf_state(root, course=course_module) \
            if course_module is not None else ia.course_shelf_state(root)
    except Exception:
        shelf = {}
    # `course_shelf_state` returns its rows under `cards`; the key is read
    # rather than assumed, and a build without `course.py` yields none.
    for course in shelf.get("cards") or ():
        cid = course.get("course_id") or ""
        name = course.get("name") or cid
        if not cid:
            continue
        out.append(_entry("go", name, "Course overview", "/course/%s" % cid))
        for area in ia.COURSE_AREAS:
            # Overview is the course route itself, already offered above;
            # `/course/<id>/overview` is not a served path, and offering it
            # would be the one thing a palette must never do.
            if area == "overview":
                continue
            out.append(_entry(
                "go", "%s: %s" % (name, ia.COURSE_AREA_LABELS[area]),
                "Course area", "/course/%s/%s" % (cid, area)))
    for stem in sorted(banks or {}):
        out.append(_entry("go", "Sit %s" % stem, "Practice sitting",
                          "/quiz/%s" % stem))
        out.append(_entry("go", "Read %s" % stem, "Lesson", "/lesson/%s" % stem))
        out.append(_entry("go", "Study %s" % stem, "Study view",
                          "/study/%s" % stem))
    return out


def do_entries(selected_look=""):
    """Actions the browser may take on its own behalf. Today: the look axis,
    through the one writer the settings page already posts to."""
    out = []
    for row in looks.catalogue():
        if row["id"] == selected_look:
            continue
        out.append(_entry(
            "do", "Look: %s" % row["name"], row["blurb"], "",
            action={"route": "/api/theme",
                    "body": {"action": "look", "look": row["id"]},
                    "reload": True}))
    return out


def run_entries(parser=None):
    """Every CLI command, with its own help line, read from the parser."""
    from surfaces import cli

    parser = parser or cli.build_parser()
    out = []
    for action in parser._subparsers._group_actions:
        if not hasattr(action, "choices"):
            continue
        helps = {}
        for choice_action in getattr(action, "_choices_actions", ()):
            helps[choice_action.dest] = choice_action.help or ""
        for name in sorted(action.choices):
            sub = action.choices[name]
            inner = []
            if getattr(sub, "_subparsers", None):
                for group in sub._subparsers._group_actions:
                    if hasattr(group, "choices"):
                        inner.extend(sorted(group.choices))
            if inner:
                for leaf in inner:
                    out.append(_entry(
                        "run", "itembank %s %s" % (name, leaf),
                        helps.get(name, ""), copy="itembank %s %s"
                        % (name, leaf)))
                continue
            out.append(_entry("run", "itembank %s" % name,
                              helps.get(name, ""), copy="itembank %s" % name))
    return out


def index(root, banks, selected_look="", course_module=None):
    """The whole palette as plain data, ready to serve as JSON."""
    entries = (go_entries(root, banks, course_module=course_module)
               + do_entries(selected_look) + run_entries())
    return {"schema_version": 1, "placeholder": PLACEHOLDER,
            "empty": EMPTY_COPY, "hint": HINT_COPY,
            "kinds": [{"id": k, "label": KIND_LABELS[k]} for k in KINDS],
            "entries": entries}


# The overlay's own rules. Every colour resolves through a token, because a
# palette that painted itself would be the one surface a look could not
# restyle.
PALETTE_CSS = """
.ib-palette[hidden]{display:none}
.ib-palette{position:fixed;inset:0;z-index:60;display:grid;
  align-items:start;justify-items:center;padding:10vh var(--space-3);
  background:rgba(0,0,0,.38)}
.ib-palette-box{width:min(640px,100%);background:var(--card);
  border:1px solid var(--line);border-radius:var(--r-3);overflow:hidden;
  box-shadow:0 18px 48px rgba(0,0,0,.22)}
.ib-palette input{width:100%;font:inherit;font-size:var(--text-lesson);padding:16px 18px;
  border:0;border-bottom:1px solid var(--line);background:var(--card);
  color:var(--ink)}
.ib-palette input:focus-visible{outline:2px solid var(--accent);
  outline-offset:-2px}
.ib-palette ul{list-style:none;margin:0;padding:6px;max-height:52vh;
  overflow:auto}
.ib-palette li{border-radius:var(--r-1)}
.ib-palette button{display:grid;gap:2px;width:100%;text-align:left;
  font:inherit;background:transparent;border:0;color:inherit;cursor:pointer;
  padding:10px 12px;min-height:44px;border-radius:var(--r-1)}
.ib-palette li[data-active] button,.ib-palette button:hover{
  background:var(--chip)}
.ib-palette button:focus-visible{outline:2px solid var(--accent);
  outline-offset:-2px}
.ib-palette-kind{font-family:var(--font-ledger);font-size:var(--text-xs);
  letter-spacing:.08em;text-transform:uppercase;color:var(--mut)}
.ib-palette-label{font-size:var(--text-body);font-weight:600;overflow-wrap:anywhere}
.ib-palette-detail{font-size:var(--text-xs);color:var(--mut);overflow-wrap:anywhere}
.ib-palette-foot{display:flex;flex-wrap:wrap;gap:var(--space-2);
  justify-content:space-between;padding:10px 14px;
  border-top:1px solid var(--line);font-size:var(--text-xs);color:var(--mut)}
.ib-palette-empty{padding:18px;color:var(--mut);font-size:var(--text-xs)}
.ib-palette-open{position:fixed;right:var(--space-3);bottom:var(--space-3);
  z-index:20;font:inherit;font-size:var(--text-xs);font-weight:600;min-height:44px;
  padding:10px 14px;border-radius:999px;border:1px solid var(--line);
  background:var(--card);color:var(--ink);cursor:pointer}
@media (max-width:767px){.ib-palette{padding:6vh var(--space-2)}}
"""

PALETTE_HTML = """
<button type="button" class="ib-palette-open" data-palette-open
  aria-haspopup="dialog">Search &amp; commands</button>
<div class="ib-palette" data-palette hidden role="dialog" aria-modal="true"
  aria-label="Command palette">
  <div class="ib-palette-box">
    <input id="ib-palette-input" type="text" autocomplete="off"
      spellcheck="false" placeholder="__PLACEHOLDER__"
      aria-label="__PLACEHOLDER__" data-palette-input>
    <ul data-palette-list role="listbox" aria-label="Results"></ul>
    <p class="ib-palette-empty" data-palette-empty hidden>__EMPTY__</p>
    <p class="ib-palette-foot"><span>__HINT__</span>
      <span class="mono" data-palette-status role="status"></span></p>
  </div>
</div>
<script>
(function () {
  var box = document.querySelector("[data-palette]");
  if (!box) { return; }
  var input = box.querySelector("[data-palette-input]");
  var list = box.querySelector("[data-palette-list]");
  var none = box.querySelector("[data-palette-empty]");
  var status = box.querySelector("[data-palette-status]");
  var opener = document.querySelector("[data-palette-open]");
  var entries = null, shown = [], active = 0, returnTo = null;

  function say(text) { status.textContent = text || ""; }

  function load() {
    if (entries) { return Promise.resolve(entries); }
    return fetch(window.location.origin + "/palette")
      .then(function (r) { return r.json(); })
      .then(function (data) { entries = data.entries || []; return entries; })
      .catch(function () { entries = []; say("Could not load the index."); return entries; });
  }

  function score(entry, needle) {
    var hay = (entry.label + " " + entry.detail).toLowerCase();
    if (!needle) { return 1; }
    var at = hay.indexOf(needle);
    if (at < 0) {
      var parts = needle.split(" ").filter(Boolean);
      for (var i = 0; i < parts.length; i++) {
        if (hay.indexOf(parts[i]) < 0) { return 0; }
      }
      return 1;
    }
    return at === 0 ? 3 : 2;
  }

  function render() {
    var needle = input.value.trim().toLowerCase();
    shown = (entries || []).map(function (entry) {
      return {entry: entry, s: score(entry, needle)};
    }).filter(function (row) { return row.s > 0; })
      .sort(function (a, b) { return b.s - a.s; })
      .slice(0, 60).map(function (row) { return row.entry; });
    active = 0;
    list.innerHTML = "";
    none.hidden = shown.length > 0;
    shown.forEach(function (entry, i) {
      var li = document.createElement("li");
      li.setAttribute("role", "option");
      if (i === 0) { li.setAttribute("data-active", "1"); li.setAttribute("aria-selected", "true"); }
      var button = document.createElement("button");
      button.type = "button";
      var kind = document.createElement("span");
      kind.className = "ib-palette-kind";
      kind.textContent = entry.kind === "go" ? "Go"
        : (entry.kind === "do" ? "Do" : "Copy");
      var label = document.createElement("span");
      label.className = "ib-palette-label";
      label.textContent = entry.label;
      var detail = document.createElement("span");
      detail.className = "ib-palette-detail";
      detail.textContent = entry.detail || "";
      button.appendChild(kind); button.appendChild(label);
      if (entry.detail) { button.appendChild(detail); }
      button.addEventListener("click", function () { choose(i); });
      li.appendChild(button);
      list.appendChild(li);
    });
  }

  function mark() {
    Array.prototype.forEach.call(list.children, function (li, i) {
      if (i === active) {
        li.setAttribute("data-active", "1");
        li.setAttribute("aria-selected", "true");
        li.scrollIntoView({block: "nearest"});
      } else {
        li.removeAttribute("data-active");
        li.setAttribute("aria-selected", "false");
      }
    });
  }

  function choose(i) {
    var entry = shown[i];
    if (!entry) { return; }
    if (entry.href) { window.location.assign(entry.href); return; }
    if (entry.action) {
      say("Applying…");
      fetch(window.location.origin + entry.action.route, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(entry.action.body)
      }).then(function (r) {
        if (!r.ok) { throw new Error("refused"); }
        if (entry.action.reload) { window.location.reload(); }
        else { say("Done."); }
      }).catch(function () { say("That was refused. Nothing changed."); });
      return;
    }
    if (entry.copy) {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(entry.copy).then(function () {
          say("Copied: " + entry.copy);
        }).catch(function () { say(entry.copy); });
      } else {
        say(entry.copy);
      }
    }
  }

  function open() {
    returnTo = document.activeElement;
    box.hidden = false;
    input.value = "";
    say("");
    load().then(function () { render(); input.focus(); });
  }

  function close() {
    box.hidden = true;
    if (returnTo && returnTo.focus) { returnTo.focus(); }
  }

  document.addEventListener("keydown", function (event) {
    var key = (event.key || "").toLowerCase();
    if (key === "k" && (event.metaKey || event.ctrlKey)) {
      event.preventDefault();
      if (box.hidden) { open(); } else { close(); }
      return;
    }
    if (box.hidden) { return; }
    if (key === "escape") { event.preventDefault(); close(); return; }
    if (key === "arrowdown" || key === "arrowup") {
      event.preventDefault();
      if (!shown.length) { return; }
      active = (active + (key === "arrowdown" ? 1 : -1) + shown.length)
        % shown.length;
      mark();
      return;
    }
    if (key === "enter" && document.activeElement === input) {
      event.preventDefault();
      choose(active);
    }
  });
  input.addEventListener("input", render);
  if (opener) { opener.addEventListener("click", open); }
  box.addEventListener("click", function (event) {
    if (event.target === box) { close(); }
  });
})();
</script>
"""


def palette_markup():
    """The overlay markup and its client, with the fixed copy substituted."""
    return (PALETTE_HTML
            .replace("__PLACEHOLDER__", html.escape(PLACEHOLDER))
            .replace("__EMPTY__", html.escape(EMPTY_COPY))
            .replace("__HINT__", html.escape(HINT_COPY)))


def palette_json(root, banks, selected_look="", course_module=None):
    return json.dumps(index(root, banks, selected_look=selected_look,
                            course_module=course_module),
                      ensure_ascii=False)
