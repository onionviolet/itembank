#!/usr/bin/env python3
"""The command palette offers what exists, and only what exists.

Three failures this guards against, in the order they would hurt:

- **A dead entry.** The palette's whole value is that selecting something
  gets you there. Every `go` entry's href must match a route the daemon
  actually serves, and every `run` entry must name a command the parser
  actually has, both checked against the shipped tables rather than a list.
- **A door the palette should not open.** It is a finding surface, not an
  authority surface: no entry may post to a route that scores, marks,
  retracts, or otherwise settles anything, and no entry may claim to run a
  local command.
- **A route offered where there is no server.** A page written to disk by
  `build` has no daemon behind it, so a palette in it would offer links
  that 404 on the filesystem.

Standard library only, runnable as `python tests/palette_check.py`.
"""
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from surfaces import cli, daemon, palette                    # noqa: E402

FAILURES = []

# Routes a palette entry may post to. The look writer is the only one: it
# changes how a page looks and nothing about what is true.
ALLOWED_ACTION_ROUTES = ("/api/theme",)

# Words that name an authority act. An entry offering one would be the
# palette settling something a surface should show the consequences of.
FORBIDDEN_ACTION_WORDS = ("submit", "mark", "score", "retract", "override",
                          "accept", "grant", "delete", "remove")


def fail(msg):
    print("FAIL: " + msg)
    FAILURES.append(msg)


def route_matchers():
    """Every GET route as something an href can be tested against."""
    exact, patterns = set(), []
    for method, pattern, _handler in daemon.ROUTES:
        if method != "GET":
            continue
        if isinstance(pattern, str):
            exact.add(pattern)
        else:
            patterns.append(pattern)
    return exact, patterns


def check_every_go_entry_resolves():
    exact, patterns = route_matchers()
    index = palette.index(ROOT, {"sample_bank": "fixtures/sample_bank.md"})
    seen = 0
    for entry in index["entries"]:
        if entry["kind"] != "go":
            continue
        seen += 1
        href = entry["href"]
        if not href.startswith("/"):
            fail("go entry %r has href %r, which is not a served path"
                 % (entry["label"], href))
            continue
        if href in exact:
            continue
        if any(p.match(href) for p in patterns):
            continue
        fail("go entry %r points at %r, which no GET route serves"
             % (entry["label"], href))
    if seen < 5:
        fail("the palette offered %d navigation entries; the fixed views "
             "alone are five" % seen)


def check_every_run_entry_names_a_real_command():
    names = set(cli.command_names())
    subs = cli.subcommand_names()
    index = palette.index(ROOT, {})
    seen = 0
    for entry in index["entries"]:
        if entry["kind"] != "run":
            continue
        seen += 1
        if not entry["copy"].startswith("itembank "):
            fail("run entry %r does not copy an itembank command"
                 % entry["label"])
            continue
        parts = entry["copy"].split()[1:]
        if parts[0] not in names:
            fail("run entry %r names %r, which the parser does not have"
                 % (entry["label"], parts[0]))
            continue
        if len(parts) > 1 and parts[1] not in subs.get(parts[0], ()):
            fail("run entry %r names subcommand %r, which %r does not have"
                 % (entry["label"], parts[1], parts[0]))
        if entry["href"] or entry["action"]:
            fail("run entry %r offers to act; a command is shown to be "
                 "copied, never run from a browser" % entry["label"])
    if seen != len(names) - len(subs) + sum(len(v) for v in subs.values()):
        fail("the palette offered %d commands; the parser has a different "
             "number, so one of them is not reading the other" % seen)


def check_no_entry_settles_anything():
    index = palette.index(ROOT, {})
    for entry in index["entries"]:
        action = entry.get("action")
        if not action:
            continue
        if action["route"] not in ALLOWED_ACTION_ROUTES:
            fail("entry %r posts to %r; the palette may only reach %s"
                 % (entry["label"], action["route"],
                    ", ".join(ALLOWED_ACTION_ROUTES)))
        body = action.get("body") or {}
        for key, value in body.items():
            text = ("%s %s" % (key, value)).lower()
            for word in FORBIDDEN_ACTION_WORDS:
                if word in text:
                    fail("entry %r carries %r in its body; the palette is a "
                         "finding surface and settles nothing"
                         % (entry["label"], word))


def check_offline_build_carries_no_palette():
    """`build` writes a page with no server behind it."""
    workdir = tempfile.mkdtemp(prefix="palette_build_")
    out = os.path.join(workdir, "quiz.html")
    proc = subprocess.run(
        [sys.executable, os.path.join(ROOT, "itembank.py"), "build",
         os.path.join(ROOT, "fixtures", "sample_bank.md"), out],
        capture_output=True, text=True)
    if proc.returncode != 0:
        fail("build failed, so the offline check could not run: %s"
             % proc.stderr.strip().splitlines()[-1:])
        return
    with open(out, encoding="utf-8") as fh:
        page = fh.read()
    if "data-palette" in page:
        fail("the offline build carries the palette, which would offer "
             "routes that have no server")
    if "/palette" in page:
        fail("the offline build references the palette index")


def check_markup_is_one_dialog_with_a_labelled_input():
    markup = palette.palette_markup()
    for needed, why in (
            ('role="dialog"', "the overlay must be a dialog"),
            ('aria-modal="true"', "the overlay must be modal"),
            ('role="listbox"', "the results must be a listbox"),
            ('aria-label="Search', "the input must carry its own label"),
            ("Escape closes", "the overlay must say how to leave it")):
        if needed not in markup:
            fail("%s (%r missing)" % (why, needed))
    if markup.count('role="dialog"') != 1:
        fail("the palette must render exactly one dialog")
    if re.search(r"eval\(|new Function", markup):
        fail("the palette client evaluates code")


def main():
    check_every_go_entry_resolves()
    check_every_run_entry_names_a_real_command()
    check_no_entry_settles_anything()
    check_markup_is_one_dialog_with_a_labelled_input()
    check_offline_build_carries_no_palette()
    if FAILURES:
        print("PALETTE: %d failure(s)" % len(FAILURES))
        return 1
    index = palette.index(ROOT, {"sample_bank": "fixtures/sample_bank.md"})
    print("ok: palette -- %d entries, every go target a served route, every "
          "run entry a real command copied and never run, and nothing "
          "offered that settles anything" % len(index["entries"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
