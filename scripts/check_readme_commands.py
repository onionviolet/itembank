#!/usr/bin/env python3
"""CI claim-word gate (plan 999.5-02): the README's command index must name
only subcommands that `python itembank.py --help` actually registers.

Precedent: 05-07's claim-word gate and 999.5-01's mirror/path gates -- the
README documents the shipped surface only, so a command line that names a
subcommand absent from `--help` is drift that fails the build instead of
rotting silently.

Mechanism: run `python itembank.py --help`, collect the registered
subcommand names, scan every fenced code block in README.md for bare command
tokens (`itembank <name>` / `python itembank.py <name>`), and fail if any
token is not a registered subcommand. Flags (`--port`, `--format`, ...) are
not checked; only the bare command name that follows `itembank` or
`itembank.py`.

Standard library only, self-contained:
    python scripts/check_readme_commands.py
"""
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
README = os.path.join(ROOT, "README.md")

# `itembank <name>` at line start, or `python itembank.py <name>`: the bare
# command token is the word right after the binary name, anchored to a line
# start so prose ("an Anki deck into itembank candidates") and the Layout
# tree ("itembank.py   entry point; ..." -- a bare module line, not a
# command) never match. `itembank.py` requires the `python ` prefix; the
# unqualified form is `itembank <name>`. A token that starts with `-` is a
# flag, not a subcommand, and is skipped.
TOKEN_RE = re.compile(
    r"(?m)^\s*(?:python\s+itembank\.py|itembank)\s+([A-Za-z][A-Za-z0-9-]*)")
FLAG_RE = re.compile(r"^--?[A-Za-z]")


def registered_subcommands():
    """The ground truth: the subcommand names `itembank.py --help` prints."""
    r = subprocess.run([sys.executable, os.path.join(ROOT, "itembank.py"),
                        "--help"], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("check_readme_commands: itembank.py --help failed:\n%s"
                 % r.stderr[-500:])
    m = re.search(r"\{([a-z][a-z0-9-]*(?:,[a-z0-9-]+)*)\}", r.stdout)
    if not m:
        sys.exit("check_readme_commands: could not parse --help subcommand list")
    return set(m.group(1).split(","))


def code_blocks(text):
    """Yield the contents of every fenced code block (``` ... ```)."""
    fence = re.compile(r"^```.*$", re.MULTILINE)
    spans = [s.span() for s in fence.finditer(text)]
    for i in range(0, len(spans) - 1, 2):
        yield text[spans[i][1]:spans[i + 1][0]]


def main():
    with open(README, encoding="utf-8") as fh:
        text = fh.read()
    registered = registered_subcommands()
    unknown = []
    for block in code_blocks(text):
        for m in TOKEN_RE.finditer(block):
            token = m.group(1)
            if FLAG_RE.match(token):
                continue
            if token not in registered:
                unknown.append(token)
    if unknown:
        print("FAIL: README names subcommands absent from `itembank.py --help`:")
        for t in sorted(set(unknown)):
            print("  - %s" % t)
        sys.exit(1)
    print("ok: every README command token is a registered subcommand "
          "(%d registered)" % len(registered))


if __name__ == "__main__":
    main()
