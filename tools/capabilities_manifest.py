#!/usr/bin/env python3
"""Generate capabilities.json, the agent-facing capability disclosure
manifest (Phase 18, 18-CONTEXT D-03).

The manifest is static and local: generating it and reading it are never
network events, and this module contains no network code of any kind. The
existing disclosure-gated updater is the only network path that ever
fetches a newer one. Consumers: any coding agent onboarding cold (README
step 0 points here), and the promoted Phase 999.3 MCP surface
(server/discover payload) as a named future consumer.

Commands and routes are enumerated by importing the live modules and
walking their registrations, never by parsing source text and never from a
second hand-written list, so the manifest cannot drift from what the CLI
and daemon actually serve. Regeneration is byte-stable
(tests/capabilities_roundtrip.py fails on any drift).

Usage: python tools/capabilities_manifest.py [OUT_PATH]
OUT_PATH defaults to <repo root>/capabilities.json.
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import itembank                                             # noqa: E402
import model                                                # noqa: E402
import model_adapter                                        # noqa: E402
import source_adapters                                      # noqa: E402

# Starts at 1; bumped only when the manifest's own shape changes, never
# when a release merely adds commands or changelog entries.
SCHEMA_VERSION = 1

# The version a command first appeared in, keyed by subcommand name. Every
# command registered today predates this manifest, so every seed value is
# the current release. A registered command missing from this table makes
# generate() raise with the command's name, so a future command cannot
# ship undisclosed: adding the command and adding its SINCE row are the
# same commit or the roundtrip test fails.
SINCE = {
    "spec": "0.3.0", "lint": "0.3.0", "build": "0.3.0", "serve": "0.3.0",
    "daemon": "0.3.0", "sidecar": "0.3.0", "cli-twin": "0.3.0",
    "disclosure": "0.3.0", "stats": "0.3.0", "coverage": "0.3.0",
    "start": "0.3.0", "override": "0.3.0", "select": "0.3.0",
    "next": "0.3.0", "submit": "0.3.0", "hint": "0.3.0", "teach": "0.3.0",
    "rubric-review": "0.3.0", "interact": "0.3.0", "report": "0.3.0",
    "evidence": "0.3.0", "trends": "0.3.0", "retract": "0.3.0",
    "render": "0.3.0", "mark": "0.3.0", "marks": "0.3.0",
    "id-assign": "0.3.0", "study": "0.3.0", "lesson": "0.3.0",
    "render-style": "0.3.0", "gloss": "0.3.0", "key-review": "0.3.0",
    "lesson-check": "0.3.0", "lesson-skip": "0.3.0", "export": "0.3.0",
    "day": "0.3.0", "schema": "0.3.0", "usage": "0.3.0", "config": "0.3.0",
    "activity": "0.3.0", "help-code": "0.3.0", "shelf": "0.3.0",
    "source": "0.3.0", "theme": "0.3.0", "migrate": "0.3.0",
    "update": "0.3.0", "import": "0.3.0", "seed": "0.3.0", "guard": "0.3.0",
    "calibrate": "0.3.0", "audit": "0.3.0", "lti": "0.3.0",
    # The first course-shaped command, added 2026-09-05 to fill the surface
    # grid's `source binding / create` cell. Still 0.3.0: it lands inside the
    # same unreleased version every command above did.
    "bind": "0.3.0",
    # Phase 19A's dispatch spine and its first operation family, added
    # 2026-09-05: the CLI twin of POST /api/course/<operation>. Still 0.3.0,
    # the same unreleased version every command above lands in.
    "course": "0.3.0",
    # Phase 19E's generated MCP tool table ships in the same unreleased version.
    "mcp": "0.3.0",
}

# The two byte-identical skill mirrors (CI enforces the diff); the index
# below is the union of directory names found under them.
SKILL_ROOTS = (".claude/skills", ".agents/skills")

# One entry per release describing what an agent must know that release
# notes for humans would bury. Each release appends one entry.
CHANGED_FOR_AGENTS = [
    {"version": "0.3.0",
     "changes": [
         "capabilities.json introduced: a static, local, machine-readable "
         "index of this install (version, format contract version, every "
         "CLI command with its since-version, served routes, skill index, "
         "and this changelog). Reading it is not a network event.",
     ]},
    {"version": "unreleased",
     "changes": [
         "The current checkout publishes the generated MCP tool table through "
         "the mcp command and token-gated /mcp route, and exposes course "
         "source-registration and agent-operation routes.",
         "Lesson readers now disclose authored comparison interactions and "
         "guided progressive-reading controls while retaining static and "
         "offline fallbacks; accessibility review remains a human gate.",
     ]},
]


class _ParserCaptured(Exception):
    """Raised by the parse_args stand-in so cli.main() hands over its fully
    built parser without ever parsing arguments or running a command."""


def capture_cli_parser():
    """Import surfaces.cli and capture the argparse parser main() builds.

    main() constructs the parser and immediately parses; swapping
    parse_args for a capturing raiser walks the real registrations (never
    a regex over source, never a second list) while running nothing.
    """
    from surfaces import cli
    captured = {}
    real_parse_args = argparse.ArgumentParser.parse_args

    def _capture(self, *args, **kwargs):
        captured["parser"] = self
        raise _ParserCaptured()

    argparse.ArgumentParser.parse_args = _capture
    try:
        try:
            cli.main()
        except _ParserCaptured:
            pass
    finally:
        argparse.ArgumentParser.parse_args = real_parse_args
    return captured["parser"]


def collect_commands():
    """One entry per registered CLI subcommand: name, one-line help, and
    the release it first appeared in (from SINCE)."""
    parser = capture_cli_parser()
    sub_actions = [a for a in parser._actions
                   if isinstance(a, argparse._SubParsersAction)]
    commands = []
    for pseudo in sub_actions[0]._choices_actions:
        name = pseudo.dest
        if name not in SINCE:
            raise SystemExit(
                "capabilities_manifest: command %r has no SINCE entry; add "
                "one so the release it appears in is disclosed" % name)
        commands.append({
            "name": name,
            "help": " ".join((pseudo.help or "").split()),
            "since": SINCE[name],
        })
    return commands


def collect_routes():
    """The daemon's served routes, straight from surfaces.daemon.ROUTES.

    Parameterised routes are recorded by their regex pattern string. Every
    route is token-gated in sidecar mode except the probe marker
    /__itembank__, mirroring DaemonHandler._sidecar_token_ok exactly.
    """
    from surfaces import daemon
    routes = []
    for method, pattern, _handler in daemon.ROUTES:
        path = pattern if isinstance(pattern, str) else pattern.pattern
        routes.append({
            "method": method,
            "path": path,
            "token_gated": path != daemon.MARKER_PATH,
        })
    return routes


def collect_skills():
    """The union of skill directory names under the mirrored skill roots,
    sorted; an empty list when no root exists."""
    names = set()
    for root in SKILL_ROOTS:
        full = os.path.join(ROOT, root)
        if not os.path.isdir(full):
            continue
        for entry in os.listdir(full):
            if os.path.isdir(os.path.join(full, entry)):
                names.add(entry)
    return sorted(names)


def capability_diagnostics(registries, configured=None, available=None,
                           disabled=None):
    """Return an explicit status view over first-party registrations.

    Registration comes from the live registry keys. The other states are
    caller facts and are never inferred from metadata, package names, or
    descriptor presence. Unknown state stays false in this compact view.
    """
    configured = None if configured is None else set(configured)
    available = None if available is None else set(available)
    disabled = None if disabled is None else set(disabled)
    rows = []
    for family, registry in registries:
        for name in registry:
            key = "%s:%s" % (family, name)
            rows.append({
                "name": name,
                "family": family,
                "registered": True,
                "configured": None if configured is None else key in configured,
                "available": None if available is None else key in available,
                "disabled": None if disabled is None else key in disabled,
            })
    return rows


def collect_capabilities():
    """Disclose registrations without claiming installation or activation."""
    return capability_diagnostics((
        ("source_adapter", source_adapters.ADAPTER_REGISTRY),
        ("model_transport", model_adapter.TRANSPORT_REGISTRY),
    ))


def generate():
    """Build the manifest dict with exactly the D-03 contents."""
    return {
        "schema_version": SCHEMA_VERSION,
        # The same constant `itembank --version` prints
        # (surfaces/cli.py registers version="%(prog)s " +
        # itembank.__version__); one constant, never a second copy.
        "itembank_version": itembank.__version__,
        # The model layer's published spec version: model.py exposes
        # SEMANTIC_PROFILE_VERSION as the versioned, additive format
        # contract profile (PORT-01); model.SPEC itself carries no
        # version number, so this is the model-layer source of record.
        "format_contract_version": model.SEMANTIC_PROFILE_VERSION,
        "commands": collect_commands(),
        "routes": collect_routes(),
        "skills": collect_skills(),
        "capabilities": collect_capabilities(),
        "changed_for_agents": CHANGED_FOR_AGENTS,
    }


def render():
    """The manifest as bytes-stable text: sorted keys, two-space indent,
    UTF-8 verbatim, one trailing newline."""
    return json.dumps(generate(), ensure_ascii=False, indent=2,
                      sort_keys=True) + "\n"


def main(argv):
    out_path = argv[1] if len(argv) > 1 else os.path.join(
        ROOT, "capabilities.json")
    text = render()
    with open(out_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    commands = json.loads(text)["commands"]
    print("%s (%d commands)" % (out_path, len(commands)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
