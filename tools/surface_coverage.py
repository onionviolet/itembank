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
    "GET /palette": "the command palette's index: it lists the routes and "
                    "commands that already exist and reaches nothing new",
}

# (object, verb) -> {"cli": [...], "http": [...], "note": "..."}
# A pair absent from this map is an empty cell, which is the report's whole
# reason to exist. `note` says what the gap costs, in one sentence, and is
# the only place in this file that argues.
CELLS = {
    ("course", "inspect"): {
        "cli": ["shelf", "course show", "course blueprint-gate", "course audit", "course staleness"],
        "http": ["GET /", "GET /course/<course_id>", "GET /course/<course_id>/<area>",
                 "GET /course/<course_id>/learn/<lesson_id>", "POST /api/shelf", "POST /api/course/blueprint-gate", "POST /api/course/audit", "POST /api/course/staleness"],
    },
    ("course", "create"): {
        "cli": ["course create"], "http": ["POST /api/course/create"],
        "note": "Filled 2026-09-05 by plan 19A-01, the phase's first cell. "
                "Both surfaces reach `course.create_course` through "
                "`surfaces/course_ops.py`, whose request is validated "
                "against schemas/course_operation.schema.json before "
                "anything is read.",
    },
    ("course", "change"): {
        "cli": ["course rename", "course add-container", "course bind-blueprint", "course accept-migration", "course reject-migration"],
        "http": ["POST /api/course/rename",
                 "POST /api/course/add-container", "POST /api/course/bind-blueprint",
                 "POST /api/course/accept-migration", "POST /api/course/reject-migration"],
        "note": "Renaming and adding a structural container are both "
                "reached. A container adds zero edges, because where a unit "
                "sits in the outline is structure and not a prerequisite "
                "claim. Moving an existing container and editing the scope "
                "tree are still hand edits.",
    },
    ("course", "explain"): {
        "cli": ["coverage"],
        "http": ["GET /course/<course_id>/<area>"],
        "note": "Coverage answers 'which objectives are cited'. Nothing "
                "answers 'why is this course shaped this way'.",
    },
    ("course", "undo"): {
        "cli": ["audit undo"], "http": [],
        "note": "Only an authoring audit is reversible. Course migration settlement is a change operation.",
    },
    ("scope", "inspect"): {
        "cli": [], "http": [],
        "note": "scope.md is read by tools/rollup_screens.py and by nothing "
                "a learner can open. The rollup screens are evidence files, "
                "not routes.",
    },
    ("objective", "inspect"): {
        "cli": ["coverage", "trends", "course structure"],
        "http": ["GET /course/<course_id>/<area>",
                 "POST /api/course/structure"],
        "note": "`course structure` reads the containers, the objectives in "
                "authored order, and each edge as this build reads it, with "
                "the warnings the authored order earns. It reports and "
                "never corrects.",
    },
    ("objective", "create"): {
        "cli": ["course add-objective", "course add-edge"],
        "http": ["POST /api/course/add-objective",
                 "POST /api/course/add-edge"],
        "note": "Filled 2026-09-05 by 19A-03. An objective is added with "
                "origin `local` and zero edges; a prerequisite between two "
                "objectives is a separate, explicit act, because a course "
                "whose week 2 follows week 1 has said nothing about what "
                "must be learned first.",
    },
    ("objective", "change"): {
        "cli": ["course rename-objective", "course split-objective",
                "course merge-objectives", "course overlay-objective"],
        "http": ["POST /api/course/rename-objective",
                 "POST /api/course/split-objective",
                 "POST /api/course/merge-objectives",
                 "POST /api/course/overlay-objective"],
        "note": "Filled 2026-09-05 by 19A-03, and every one of the four adds "
                "rows and deletes none. The identity a learner's evidence "
                "was recorded against stays in the file, or that evidence "
                "stops naming anything, so a rename is a new row plus a "
                "migration recorded `proposed`. 19A-07 adds the two reviewer "
                "settlement doors without deleting either identity.",
    },
    ("objective", "undo"): {
        "cli": ["course accept-migration", "course reject-migration",
                "course reverse-operation"],
        "http": ["POST /api/course/accept-migration",
                 "POST /api/course/reject-migration",
                 "POST /api/course/reverse-operation"],
        "note": "A proposed identity move is declined by recording a "
                "rejection. An accepted or rejected settlement carries one "
                "operation id on its CAS journal entry, and reverse-operation "
                "restores that entry's exact before-image without deleting "
                "the proposal or rewriting evidence.",
    },
    ("objective", "explain"): {
        "cli": ["coverage"], "http": [],
        "note": "An item cites its objective and its source; no surface "
                "shows the objective, its cited passage and the learner's "
                "own history on it together.",
    },
    ("source", "create"): {
        "cli": ["source import", "course add-source"],
        "http": ["POST /api/source/import",
                 "POST /api/course/add-source"],
        "note": "Two steps, and 19A-02 built the second. Import extracts "
                "one file to Markdown plus a locator sidecar and registers "
                "the object; `course add-source` records it in the course "
                "that will use it, which is the row `graph.add_source` "
                "writes and which nothing called until now. A source the "
                "registry holds and the sidecar does not name is invisible "
                "to the Sources area, to `bind list`, and to a package "
                "manifest that walks the sidecar.",
    },
    ("source", "inspect"): {
        "cli": ["source recheck"], "http": ["POST /api/source/recheck",
                                            "GET /course/<course_id>/<area>"],
        "note": "The Sources area lists bound sources by name. There is no "
                "reader: no surface opens a source and shows the passage an "
                "objective cites.",
    },
    ("source binding", "inspect"): {
        "cli": ["bind list"],
        "http": ["GET /course/<course_id>/<area>",
                 "POST /api/course/bindings"],
    },
    ("source binding", "explain"): {
        "cli": ["bind list"], "http": ["POST /api/course/bindings"],
        "note": "Filled 2026-09-05 by 19A-02. Every row comes back through "
                "`graph.validate_binding`, so a state this build cannot "
                "read degrades to unknown and never to covered, and the "
                "right the binding consumes is re-read through "
                "`course.rights_for_binding` and reported beside the "
                "snapshot the row stored. A snapshot saying granted after "
                "the grant was revoked is history, not permission, and "
                "that divergence is the one thing a coverage claim cannot "
                "notice about itself.",
    },
    ("source binding", "create"): {
        "cli": ["bind source", "bind treatment"],
        "http": ["POST /api/course/bind", "POST /api/course/bind-treatment",
                 "POST /api/bind"],
        "note": "Filled 2026-09-05, the first cell this grid caused to be "
                "built. Both surfaces reach `course.bind_source` and "
                "`course.bind_treatment`; neither writes a row itself. "
                "Re-homed under /api/course/ by 19A-01; POST /api/bind is "
                "the deprecated alias, still serving. 19A-04 gave the "
                "treatment write its own operation, because `treatment` is "
                "required there and the bind node cannot say so.",
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
        "cli": ["course replay"],
        "http": ["GET /activity", "POST /api/course/replay"],
        "note": "The Activity view renders durable jobs from the journal. "
                "Plan 19A-05 added replay on both operating surfaces, "
                "including the next resumable protocol step and egress.",
    },
    ("agent operation", "create"): {
        "cli": ["course begin-operation"],
        "http": ["POST /api/course/begin-operation"],
        "note": "Plan 19A-05 declares intent, role, autonomy and scope "
                "before work starts, through one journal-backed operation.",
    },
    ("agent operation", "change"): {
        "cli": ["course recommend", "course recommend-pass",
                "course apply-recommendation"],
        "http": ["POST /api/course/recommend",
                 "POST /api/course/recommend-pass",
                 "POST /api/course/apply-recommendation"],
        "note": "Plan 19A-05 exposes single and pass recommendation, then "
                "keeps acceptance separate and rights-gated. Acceptance's "
                "CAS journal row also carries its operation identity.",
    },
    ("agent operation", "explain"): {
        "cli": ["course autonomy"],
        "http": ["POST /api/course/autonomy"],
        "note": "Plan 19A-05 reads the granted policy from settings and "
                "dry-runs a declaration without letting a request grant "
                "itself authority.",
    },
    ("agent operation", "undo"): {
        "cli": ["course reverse-operation"],
        "http": ["POST /api/course/reverse-operation"],
        "note": "Plan 19A-05 reverses the operation's accepted writes "
                "through journal.undo and their recorded before-images.",
    },
    ("rights grant", "inspect"): {
        "cli": ["bind list"], "http": ["GET /course/<course_id>/<area>"],
        "note": "The Sources area states the read right each source carries, "
                "and `bind list` prints all seven. Nothing yet explains a "
                "refusal after the fact.",
    },
    ("rights grant", "create"): {
        "cli": ["bind rights", "source import"],
        "http": ["POST /api/course/rights", "POST /api/rights",
                 "POST /api/source/import"],
        "note": "One operation records a grant and a denial, so create and "
                "change are the same call; both are listed because both are "
                "true.",
    },
    ("rights grant", "explain"): {
        "cli": ["bind treatments", "bind list"],
        "http": ["POST /api/course/treatments",
                 "POST /api/course/bindings"],
        "note": "Filled 2026-09-05 by 19A-04, which gave "
                "`graph.TREATMENT_RIGHTS` its first reader. The eleven-kind "
                "mapping decides which treatments a course may use for a "
                "source, and until this it could only be discovered by "
                "attempting a binding and being refused: a learner with "
                "`read` and not `transform` could bind a direct reading and "
                "not a guided lesson, and nothing said so beforehand. The "
                "table now answers per source, with the right each kind "
                "consumes and its state right now. What is still missing is "
                "the refusal's own history: why an export or a package that "
                "already refused did so, which is 19A-08's read.",
    },
    ("rights grant", "change"): {
        "cli": ["bind rights"],
        "http": ["POST /api/course/rights", "POST /api/rights"],
        "note": "Filled 2026-09-05 beside the binding it gates: a binding "
                "refused for a right nobody declared has to have its way out "
                "on the same surface.",
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
        "cli": ["export", "course export-package"],
        "http": ["POST /api/export_audio",
                 "POST /api/course/export-package"],
        "note": "`course export-package` writes one local plain-directory "
                "package through fixed staging and publishes it below the "
                "approved root's _packages directory.",
    },
    ("package", "inspect"): {
        "cli": ["course verify-package", "course package-losses"],
        "http": ["POST /api/course/verify-package",
                 "POST /api/course/package-losses"],
        "note": "Both reads expose the exact loss report and current "
                "completeness and restorable truth.",
    },
    ("package", "change"): {
        "cli": ["course restore-package"],
        "http": ["POST /api/course/restore-package"],
        "note": "Restore consumes a package without changing it, stages a "
                "fresh course, and publishes under course identity.",
    },
    ("package", "explain"): {
        "cli": ["course package-losses"],
        "http": ["POST /api/course/package-losses"],
        "note": "The loss surface explains every object or capability that "
                "did not travel and why.",
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
    ("source", "change"): "Re-importing is the only way to refresh a source, "
                          "and it mints a new object rather than updating.",
    ("source", "explain"): "The Sources area now states each source's read "
                           "right, but not what it was used FOR: which "
                           "objectives cite it and which items came from it.",
    ("source", "undo"): "An imported source cannot be unbound from a "
                        "surface.",
    ("source binding", "change"): "Re-pointing a binding at a different "
                                  "passage is a sidecar table edit.",
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
    ("sitting", "explain"): "A finished sitting reports counts. Nothing "
                            "walks it back item by item with what was shown "
                            "and when.",
    ("package", "undo"): "No surface deletes or supersedes a package.",
    ("day plan", "explain"): "The plan says what is due and not why this "
                             "rather than that.",
}


# Commands whose subcommands are classified individually, so the bare name
# is expected to be absent from the cells.
SUBCOMMAND_PARENTS = ("audit", "bind", "course", "source", "theme",
                      "import", "lti")


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
