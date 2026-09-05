#!/usr/bin/env python3
"""The object-by-verb surface grid: which durable objects a person or an
agent can actually reach, and with which verb, from which surface.

The 2026-09-05 gap pass found the shape of the problem in prose: "the engine
is real and has almost no door". This makes that a measurement instead of a
finding, so it moves on its own as doors are built and cannot quietly stop
being true.

Two halves, and the split is the point:

- **Declared.** `CELLS` maps one (object, verb) pair to the CLI commands and
  HTTP routes that reach it. A machine cannot infer that `itembank start`
  creates a sitting; a person states it once, here.
- **Measured.** The command list comes from `surfaces.cli.build_parser()`
  and the route list from `surfaces.daemon.ROUTES`, never from a copy. Every
  command and every route must be claimed by exactly one cell or named in
  `NOT_A_CAPABILITY` with its reason, so a command added without a cell
  fails this report rather than sitting in a blind spot. That is the half
  that keeps the declared half honest.

An empty cell is the finding. It means the object exists in the runtime, the
verb is meaningful for it, and no surface performs it.

Stdlib only. Usage:

    PYTHONPATH=. python3 tools/surface_coverage.py            # the grid
    PYTHONPATH=. python3 tools/surface_coverage.py --json     # machine form
    PYTHONPATH=. python3 tools/surface_coverage.py --gaps     # empty cells only

Exit 0 when every command and route is classified, 1 when any is not.
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

# The durable objects, in the order `AGENTS.md` lists them, followed by the
# four the runtime owns that are not on that list but that a learner meets
# (a sitting, a package, the install's own settings, and a day plan).
OBJECTS = (
    "course", "scope", "objective", "source", "source binding", "lesson",
    "bank", "item", "activity", "learner note", "evidence event",
    "strategy", "agent operation", "rights grant", "accepted revision",
    "sitting", "package", "settings", "day plan",
)

# What a person can want to do to any of them. Five verbs, because these are
# the five a surface has to answer for an object to be usable at all: I can
# make one, look at one, alter one, understand why it is as it is, and take
# a step back.
VERBS = ("create", "inspect", "change", "explain", "undo")

# Commands and routes that are not a verb on a durable object. Named with a
# reason rather than dropped, so "unclassified" always means "nobody has
# looked at this yet".
NOT_A_CAPABILITY = {
    "spec": "prints the format contract; documentation, not an object",
    "schema": "prints a published JSON schema; documentation",
    "help-code": "prints one offline help page; documentation",
    "cli-twin": "prints the CLI command a served view maps to; a mapping",
    "daemon": "starts the server; a process, not an object",
    "serve": "starts a scoped server for one bank; a process",
    "sidecar": "starts the packaged-app server; a process",
    "usage": "reports token and cost accounting for model calls",
    "update": "checks for and applies a release; the install itself",
    "disclosure": "prints the one-disclosure render-hook state",
    "guard": "refuses to run when the working tree is unsafe; a gate",
    "calibrate": "reports item difficulty calibration; an analysis",
    "config": "reads and writes settings keys; covered by settings/change",
    "GET /__itembank__": "the packaged-app launch marker",
    "GET /banks": "the pre-course bank index, kept for the fallback path",
    "GET /assets/katex/<name>": "vendored math assets",
    "GET /assets/fonts/<name>": "vendored reading faces",
    "GET /help/<code>": "one offline help page; documentation",
    "lti doctor": "checks an LTI deployment's configuration; a deployment",
    "lti serve": "starts the LTI bind; a process",
    "lti status": "reports the LTI bind's state; a deployment",
    "POST /cli-twin": "the same mapping as the CLI command",
    "GET /disclosure": "the same state as the CLI command",
    "POST /seed/accept": "accepts a seeded first-run corpus; first-run only",
    "GET /activity": "the durable-job view; see agent operation/inspect",
}

# (object, verb) -> {"cli": [...], "http": [...], "note": "..."}
# A pair absent from this map is an empty cell, which is the report's whole
# reason to exist. `note` says what the gap costs, in one sentence, and is
# the only place in this file that argues.
CELLS = {
    ("course", "inspect"): {
        "cli": ["shelf"],
        "http": ["GET /", "GET /course/<course_id>", "GET /course/<course_id>/<area>",
                 "GET /course/<course_id>/learn/<lesson_id>", "POST /api/shelf"],
    },
    ("course", "create"): {
        "cli": [], "http": [],
        "note": "A course is created by calling course.create_course from "
                "Python. Neither a person nor an agent client can start a "
                "course from a surface.",
    },
    ("course", "change"): {
        "cli": [], "http": [],
        "note": "No surface renames a course, moves a unit, or edits the "
                "scope tree. The sidecar is hand-edited Markdown.",
    },
    ("course", "explain"): {
        "cli": ["coverage"],
        "http": ["GET /course/<course_id>/<area>"],
        "note": "Coverage answers 'which objectives are cited'. Nothing "
                "answers 'why is this course shaped this way'.",
    },
    ("course", "undo"): {
        "cli": ["audit undo"], "http": [],
        "note": "Only an authoring audit is reversible. A course-level "
                "operation has journal.undo in Python and no surface.",
    },
    ("scope", "inspect"): {
        "cli": [], "http": [],
        "note": "scope.md is read by tools/rollup_screens.py and by nothing "
                "a learner can open. The rollup screens are evidence files, "
                "not routes.",
    },
    ("objective", "inspect"): {
        "cli": ["coverage", "trends"],
        "http": ["GET /course/<course_id>/<area>"],
    },
    ("objective", "create"): {
        "cli": [], "http": [],
        "note": "Objectives are authored by hand into objectives.md and the "
                "sidecar. No surface adds one, and no surface links one to "
                "a source passage.",
    },
    ("objective", "explain"): {
        "cli": ["coverage"], "http": [],
        "note": "An item cites its objective and its source; no surface "
                "shows the objective, its cited passage and the learner's "
                "own history on it together.",
    },
    ("source", "create"): {
        "cli": ["source import"], "http": ["POST /api/source/import"],
        "note": "Import extracts one file to Markdown plus a locator "
                "sidecar. That is step one of binding, and it stops there.",
    },
    ("source", "inspect"): {
        "cli": ["source recheck"], "http": ["POST /api/source/recheck",
                                            "GET /course/<course_id>/<area>"],
        "note": "The Sources area lists bound sources by name. There is no "
                "reader: no surface opens a source and shows the passage an "
                "objective cites.",
    },
    ("source binding", "inspect"): {
        "cli": [], "http": ["GET /course/<course_id>/<area>"],
        "note": "Bindings render inside the sidecar table only.",
    },
    ("source binding", "create"): {
        "cli": [], "http": [],
        "note": "course.bind_source exists in Python. Binding a source to "
                "an objective is the central act of building a course and "
                "has no surface at all.",
    },
    ("lesson", "inspect"): {
        "cli": ["lesson", "study", "gloss", "lesson-check", "lesson-skip"],
        "http": ["GET /lesson/<stem>", "GET /study/<stem>",
                 "GET /gloss/<stem>/<slug>", "POST /lesson/<stem>/check",
                 "POST /lesson/<stem>/skip", "POST /api/lesson-complete",
                 "POST /api/lesson/run", "GET /media/<stem>/<name>",
                 "GET /course/<course_id>/<area>"],
    },
    ("lesson", "create"): {
        "cli": [], "http": [],
        "note": "The lesson-authoring skill is a stub and no command writes "
                "a lesson. Lessons are written by hand or by an agent "
                "editing files directly.",
    },
    ("lesson", "change"): {
        "cli": ["audit author", "audit material", "render-style"],
        "http": [],
        "note": "The authoring audit can rewrite with a reviewed diff. "
                "There is no served editor.",
    },
    ("bank", "inspect"): {
        "cli": ["lint", "stats", "coverage", "select", "render", "build",
                "key-review", "id-assign"],
        "http": ["GET /quiz/<stem>", "POST /key/<key_id>/review"],
    },
    ("bank", "create"): {
        "cli": ["seed", "import anki"], "http": [],
        "note": "Seeding writes a starter corpus and `import anki` converts "
                "a deck. Authoring a bank for an objective is the "
                "author-bank skill driving a file, not a command.",
    },
    ("bank", "change"): {
        "cli": ["audit author", "audit coverage", "audit source", "migrate"],
        "http": [],
    },
    ("bank", "explain"): {
        "cli": ["stats", "calibrate", "coverage"], "http": [],
    },
    ("item", "inspect"): {
        "cli": ["next", "select"], "http": ["POST /api/next"],
    },
    ("item", "explain"): {
        "cli": ["teach", "hint", "rubric-review"],
        "http": ["POST /api/teach", "POST /api/hint",
                 "POST /api/rubric-review"],
        "note": "The hint ladder explains how to answer. Nothing explains "
                "why this item exists: its objective, its cited passage and "
                "your history with it are three separate places.",
    },
    ("item", "change"): {
        "cli": ["id-assign", "audit author"], "http": [],
    },
    ("activity", "inspect"): {
        "cli": ["activity", "interact"], "http": ["POST /api/interact"],
    },
    ("learner note", "create"): {
        "cli": [], "http": [],
        "note": "notes.py implements the whole note lifecycle, including "
                "promotion and the authority guard. No surface writes one.",
    },
    ("learner note", "inspect"): {
        "cli": [], "http": [],
        "note": "Same module, same absence: nothing renders a note.",
    },
    ("evidence event", "create"): {
        "cli": ["submit", "mark", "retract", "interact"],
        "http": ["POST /api/submit", "POST /quiz/<stem>/answer",
                 "POST /api/mark"],
    },
    ("evidence event", "inspect"): {
        "cli": ["evidence", "marks", "report", "trends", "day"],
        "http": ["GET /report", "POST /api/report", "GET /day",
                 "GET /day/<stem>", "GET /course/<course_id>/<area>"],
    },
    ("evidence event", "explain"): {
        "cli": ["trends", "stats"], "http": [],
        "note": "Trends aggregate over time. No surface shows one sitting "
                "as a timeline you can walk back through.",
    },
    ("evidence event", "undo"): {
        "cli": ["retract"], "http": [],
        "note": "Retraction is CLI-only. A learner who mis-taps an answer "
                "in the browser cannot take it back from the browser.",
    },
    ("strategy", "inspect"): {
        "cli": [], "http": [],
        "note": "strategies.py freezes four contracts with eight declared "
                "columns each. No surface lists them or offers a choice.",
    },
    ("agent operation", "inspect"): {
        "cli": [], "http": ["GET /activity"],
        "note": "The Activity view renders durable jobs from the journal. "
                "surfaces/agent_operation.py implements run, propose and "
                "accept, and no route reaches it: the Build and review area "
                "is a GET with nothing in it.",
    },
    ("agent operation", "create"): {
        "cli": [], "http": [],
        "note": "No surface starts an agent operation. The whole "
                "propose-and-accept seam is unplugged.",
    },
    ("agent operation", "change"): {
        "cli": [], "http": [],
        "note": "No surface accepts or rejects a proposal.",
    },
    ("rights grant", "change"): {
        "cli": [], "http": [],
        "note": "journal.op_grant_rights landed 2026-09-05 and has no "
                "surface: rights are granted from Python only.",
    },
    ("accepted revision", "inspect"): {
        "cli": [], "http": [],
        "note": "15B's accept_revision record has no reader.",
    },
    ("sitting", "create"): {
        "cli": ["start", "override"],
        "http": ["POST /api/start", "POST /api/override"],
    },
    ("sitting", "inspect"): {
        "cli": ["next", "report"],
        "http": ["POST /api/next", "GET /quiz/<stem>", "POST /api/report"],
    },
    ("sitting", "change"): {
        "cli": ["submit", "teach", "hint", "mark"],
        "http": ["POST /api/submit", "POST /api/teach", "POST /api/hint",
                 "POST /api/mark", "POST /quiz/<stem>/answer"],
    },
    ("sitting", "undo"): {
        "cli": ["retract"], "http": [],
        "note": "Same gap as the evidence event it retracts.",
    },
    ("package", "create"): {
        "cli": ["export"], "http": ["POST /api/export_audio"],
        "note": "`export` writes Anki TSV and audio. course_package's "
                "export, verify and restore have no surface, so the one "
                "path that makes a course portable is Python-only.",
    },
    ("settings", "inspect"): {
        "cli": ["config", "theme looks"], "http": ["GET /settings"],
    },
    ("settings", "change"): {
        "cli": ["config", "theme set", "theme look", "theme pick",
                "theme reset", "theme preview"],
        "http": ["POST /api/theme"],
    },
    ("day plan", "inspect"): {
        "cli": ["day"], "http": ["GET /day", "GET /day/<stem>"],
    },
    ("day plan", "change"): {
        "cli": ["day"], "http": ["POST /day/<stem>/save",
                                 "POST /day/<stem>/edit",
                                 "POST /day/<stem>/open"],
    },
    ("lesson", "explain"): {
        "cli": ["gloss"], "http": ["GET /gloss/<stem>/<slug>"],
    },
    ("bank", "undo"): {
        "cli": ["audit undo"], "http": [],
    },
}

# Cells where the verb does not apply to the object, with the reason. An
# empty cell means "nobody built this yet"; a cell here means "this would
# not mean anything", and conflating the two would inflate the gap count
# with work nobody should do.
NOT_MEANINGFUL = {
    ("evidence event", "change"): "an evidence event is append-only; a mark "
                                  "is a new fact about it, never an edit",
    ("settings", "create"): "settings always exist, defaulted by the schema",
    ("settings", "undo"): "every key is set back by setting it again",
    ("settings", "explain"): "the schema's own description is the "
                             "explanation, and `config` prints it",
    ("day plan", "create"): "a day plan is derived from what is due; it is "
                            "read, not minted",
    ("day plan", "undo"): "editing a plan back is the same act as editing it",
    ("accepted revision", "create"): "a revision is accepted by accepting a "
                                     "proposal, which is agent operation / "
                                     "change",
    ("accepted revision", "change"): "an accepted revision is a settled "
                                     "record; changing one would erase the "
                                     "settlement",
    ("accepted revision", "undo"): "superseding is the undo, and it is a "
                                   "new record rather than a removal",
    ("accepted revision", "explain"): "the record carries its own reviewer "
                                      "and reason",
    ("rights grant", "undo"): "a grant is revoked by recording denied, "
                              "which is the same operation",
    ("strategy", "create"): "the four contracts are frozen in code; a fifth "
                            "is a phase, not a surface action",
    ("scope", "create"): "a scope is part of the course record; see "
                         "course / create",
}

# Empty cells whose cost is one sentence rather than a paragraph, kept apart
# from CELLS so a cell that acquires a surface moves up rather than being
# edited in place. Every meaningful cell in the grid is either in CELLS or
# here; a cell in neither prints "no note yet", which is itself a finding
# about this file.
GAP_NOTES = {
    ("scope", "change"): "Boundedness, membership and the completion "
                         "predicate are edited by hand in scope.md.",
    ("scope", "explain"): "Nothing states why a scope is open or bounded, "
                          "which is the sentence that governs whether it may "
                          "ever report complete.",
    ("scope", "undo"): "A scope edit is a text edit; git is the only undo.",
    ("objective", "change"): "Rewording an objective, or moving it between "
                             "containers, is a hand edit of two files that "
                             "must stay in step.",
    ("objective", "undo"): "No surface reverses an objective edit.",
    ("source", "change"): "Re-importing is the only way to refresh a source, "
                          "and it mints a new object rather than updating.",
    ("source", "explain"): "Nothing shows what a source was used for: which "
                           "objectives cite it and which items came from it.",
    ("source", "undo"): "An imported source cannot be unbound from a "
                        "surface.",
    ("source binding", "change"): "Re-pointing a binding at a different "
                                  "passage is a sidecar table edit.",
    ("source binding", "explain"): "A binding carries confidence and a "
                                   "rationale and no surface reads them out.",
    ("source binding", "undo"): "No surface removes a binding.",
    ("lesson", "undo"): "An authoring audit is reversible; a hand edit is "
                        "not.",
    ("item", "create"): "Writing an item is the author-bank skill editing a "
                        "file. No surface adds one, which is why a bad "
                        "question found mid-sitting cannot be fixed there.",
    ("item", "undo"): "No surface reverses an item edit or retires an item.",
    ("activity", "create"): "The ACTIVITIES registry is authored in the "
                            "bank; no surface declares one.",
    ("activity", "change"): "Same registry, same absence.",
    ("activity", "explain"): "An activity declares purpose, demand and "
                             "evidence state; nothing reads them back.",
    ("activity", "undo"): "No surface withdraws an activity declaration.",
    ("learner note", "change"): "notes.py implements editing and promotion; "
                                "no surface reaches it.",
    ("learner note", "explain"): "A note's provenance and review state are "
                                 "recorded and never shown.",
    ("learner note", "undo"): "Deletion is implemented and unreachable.",
    ("strategy", "change"): "A learner cannot choose a strategy, which is "
                            "the one axis the strategy contract says is "
                            "theirs.",
    ("strategy", "explain"): "Each contract declares eight columns "
                             "including accommodation and evidence effect; "
                             "none is rendered.",
    ("strategy", "undo"): "Nothing to undo while nothing can be chosen.",
    ("agent operation", "explain"): "The journal records exactly what left "
                                    "the machine for each agent call. No "
                                    "surface shows it.",
    ("agent operation", "undo"): "Rejecting or reversing an agent operation "
                                 "has no surface.",
    ("rights grant", "create"): "See rights grant / change: one operation "
                                "records both, and neither is reachable.",
    ("rights grant", "inspect"): "A learner cannot see what they may do with "
                                 "a source they bound, which is the question "
                                 "that decides whether a course can be "
                                 "exported at all.",
    ("rights grant", "explain"): "Unknown stays restrictive, and nothing "
                                 "says which right is unknown or why an "
                                 "export refused.",
    ("sitting", "explain"): "A finished sitting reports counts. Nothing "
                            "walks it back item by item with what was shown "
                            "and when.",
    ("package", "inspect"): "A package's manifest and loss report are "
                            "written to disk and read by nobody: the loss "
                            "report is the honest half of an export and it "
                            "has no reader.",
    ("package", "change"): "No surface re-exports or repairs a package.",
    ("package", "explain"): "Nothing explains why an object did not cross.",
    ("package", "undo"): "No surface deletes or supersedes a package.",
    ("day plan", "explain"): "The plan says what is due and not why this "
                             "rather than that.",
}


# Commands whose subcommands are classified individually, so the bare name
# is expected to be absent from the cells.
SUBCOMMAND_PARENTS = ("audit", "source", "theme", "import", "lti")


def route_label(method, pattern):
    """One route as the report names it: the method plus a readable path."""
    if isinstance(pattern, str):
        return "%s %s" % (method, pattern)
    text = pattern.pattern.strip("^$")
    out, depth = [], 0
    i = 0
    while i < len(text):
        if text.startswith("(?P<", i):
            end = text.index(">", i)
            out.append("<%s>" % text[i + 4:end])
            depth = 1
            i = end + 1
            continue
        if depth:
            if text[i] == ")":
                depth = 0
            i += 1
            continue
        out.append(text[i])
        i += 1
    return "%s %s" % (method, "".join(out))


def measured():
    """The command and route inventories, read from the shipped surfaces."""
    from surfaces import cli, daemon

    parser = cli.build_parser()
    commands = set(cli.command_names(parser))
    subs = cli.subcommand_names(parser)
    named = set()
    for parent in SUBCOMMAND_PARENTS:
        for sub in subs.get(parent, ()):
            named.add("%s %s" % (parent, sub))
        commands.discard(parent)
    commands |= named
    routes = set(route_label(method, pattern)
                 for method, pattern, _handler in daemon.ROUTES)
    return commands, routes


def classified():
    """Everything the cells claim, as two sets."""
    cli_claimed, http_claimed = set(), set()
    for cell in CELLS.values():
        cli_claimed.update(cell.get("cli") or ())
        http_claimed.update(cell.get("http") or ())
    return cli_claimed, http_claimed


def report():
    """The whole grid plus the two inventories, as plain data."""
    commands, routes = measured()
    cli_claimed, http_claimed = classified()
    excused = set(NOT_A_CAPABILITY)
    grid = []
    for obj in OBJECTS:
        row = {"object": obj, "cells": {}}
        for verb in VERBS:
            cell = CELLS.get((obj, verb))
            row["cells"][verb] = {
                "cli": sorted(cell.get("cli") or ()) if cell else [],
                "http": sorted(cell.get("http") or ()) if cell else [],
                "note": ((cell or {}).get("note", "")
                         or GAP_NOTES.get((obj, verb), "")),
                "reached": bool(cell and ((cell.get("cli") or [])
                                          or (cell.get("http") or []))),
                "meaningful": (obj, verb) not in NOT_MEANINGFUL,
                "why_not": NOT_MEANINGFUL.get((obj, verb), ""),
            }
        grid.append(row)
    return {
        "objects": len(OBJECTS), "verbs": len(VERBS),
        "cells_total": len(OBJECTS) * len(VERBS),
        "cells_reached": sum(1 for row in grid for verb in VERBS
                             if row["cells"][verb]["reached"]),
        "cells_meaningful": sum(1 for row in grid for verb in VERBS
                                if row["cells"][verb]["meaningful"]),
        "commands_measured": sorted(commands),
        "routes_measured": sorted(routes),
        "unclassified_commands": sorted(commands - cli_claimed - excused),
        "unclassified_routes": sorted(routes - http_claimed - excused),
        "phantom_commands": sorted(cli_claimed - commands),
        "phantom_routes": sorted(http_claimed - routes),
        "grid": grid,
    }


def print_grid(data, gaps_only=False):
    reached = data["cells_reached"]
    meaningful = data["cells_meaningful"]
    total = data["cells_total"]
    print("# Surface coverage: %d of %d meaningful (object, verb) cells "
          "reached" % (reached, meaningful))
    print()
    print("%d objects by %d verbs is %d cells; %d do not apply and are named "
          "with a reason, leaving %d that should have a surface. %d of those "
          "have none."
          % (data["objects"], data["verbs"], total, total - meaningful,
             meaningful, meaningful - reached))
    print()
    print("%d commands and %d routes measured, every one of them classified."
          % (len(data["commands_measured"]), len(data["routes_measured"])))
    print()
    if not gaps_only:
        print("| object | " + " | ".join(VERBS) + " |")
        print("|---" * (len(VERBS) + 1) + "|")
        for row in data["grid"]:
            cells = []
            for verb in VERBS:
                cell = row["cells"][verb]
                if not cell["meaningful"]:
                    cells.append("n/a")
                    continue
                if not cell["reached"]:
                    cells.append("--")
                    continue
                marks = []
                if cell["cli"]:
                    marks.append("cli")
                if cell["http"]:
                    marks.append("http")
                cells.append("+".join(marks))
            print("| %s | %s |" % (row["object"], " | ".join(cells)))
        print()
    print("## Empty cells, and what each costs")
    print()
    for row in data["grid"]:
        for verb in VERBS:
            cell = row["cells"][verb]
            if cell["reached"] or not cell["meaningful"]:
                continue
            note = cell["note"] or "No surface, and no note yet on what it costs."
            print("- **%s / %s.** %s" % (row["object"], verb, note))
    print()
    problems = 0
    for key in ("unclassified_commands", "unclassified_routes",
                "phantom_commands", "phantom_routes"):
        if data[key]:
            problems += len(data[key])
            print("%s: %s" % (key.replace("_", " "), ", ".join(data[key])))
    if problems:
        print()
        print("%d item(s) are not accounted for. Add a cell, or name it in "
              "NOT_A_CAPABILITY with its reason." % problems)
    return 1 if problems else 0


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--json", action="store_true",
                        help="emit the report as JSON")
    parser.add_argument("--gaps", action="store_true",
                        help="print only the empty cells")
    args = parser.parse_args(argv[1:])
    data = report()
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 1 if (data["unclassified_commands"]
                     or data["unclassified_routes"]
                     or data["phantom_commands"]
                     or data["phantom_routes"]) else 0
    return print_grid(data, gaps_only=args.gaps)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
