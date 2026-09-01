#!/usr/bin/env python3
"""Dev-time release build: stage this repository's shippable contents, zip
them into a runnable `.pyz` with stdlib `zipapp`, and write a checksum file
covering everything the release directory holds -- one command, so the
artifact filename, `SHA256SUMS.txt` and `itembank.__version__` are emitted
together and cannot drift apart from each other (D-08).

The release tag format is plain `vX.Y.Z` with no pre-release or build suffix
(D-07), because the updater compares version components as integers.

Dev-time tooling only: imported by nothing at runtime, and therefore not
staged into the artifact it builds.
"""
import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import zipapp

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

import itembank                                                              # noqa: E402


# Explicit allowlists, never a walk of the working tree -- this is what keeps
# learner evidence and any private bank out of the artifact (T-02.1-01).
STAGE_FILES = (
    "itembank.py", "model.py", "runtime.py", "server.py", "evidence.py",
    "schema_validate.py", "selection.py", "retention.py", "resources.py",
    "auditor.py", "authoring.py", "audit_writer.py",
    "runner.py", "subjects.py",
    # Phase 14A and 14B, added 2026-08-27 by plan 14C-01 Task 4. These
    # shipped without ever entering the artifact: nothing in `surfaces/`
    # imported them at module scope, so the built .pyz stayed importable and
    # the omission stayed invisible. `surfaces/cli.py` now imports identity,
    # journal, and source_adapters for `itembank source import`, which turned
    # the latent gap into a hard ImportError inside the .pyz and is how it was
    # found. discovery is journal's own dependency; course, graph, and
    # course_package are staged with them so the same class of gap does not
    # reappear the first time a surface reaches for a course.
    "identity.py", "journal.py", "discovery.py", "source_adapters.py",
    "course.py", "graph.py", "course_package.py",
    "model_adapter.py", "tier_gate.py",
    # Phase 16A, added 2026-08-28 by plan 16A-04 Task 3. `surfaces/lesson.py`
    # now imports `capabilities` at module scope, so that the inline check's
    # static instructional copy has one home instead of two. Omitting it here
    # is a hard ImportError inside the built .pyz, which is exactly the class
    # of gap the 14A and 14B entry above records; it is caught by
    # tests/packaging_roundtrip.py and tests/math_offline_roundtrip.py.
    "capabilities.py",
    # Phase 16B, added 2026-08-28 by plan 16B-09 Task 1. `surfaces/daemon.py`
    # and `surfaces/ia.py` both import `sample_course` at module scope so the
    # bundled sample course's bytes have one home. Omitting it here is the
    # same hard ImportError inside the built .pyz that the 14A/14B and 16A
    # entries above record, caught by tests/packaging_roundtrip.py and
    # tests/math_offline_roundtrip.py.
    "sample_course.py",
    # Phase 15B, added 2026-08-30 by plan 15B-02 Task 1. `authoring.py` now
    # imports `blueprint` at module scope for ACTIVITY-02's gate 4, so
    # omitting it is a hard ImportError inside the built .pyz. Caught by
    # tests/packaging_roundtrip.py and tests/math_offline_roundtrip.py, which
    # is the third time the entries above record this same class of gap.
    "blueprint.py",
    # Staged with it, and NOT because anything imports them at module scope
    # today. These are shipped root modules that the 14A/14B entry's own
    # reasoning covers: `course`, `graph` and `course_package` were staged
    # proactively "so the same class of gap does not reappear the first time a
    # surface reaches for a course", and these are in exactly that position.
    # Each has been shipped and frozen without ever entering the artifact, so
    # the omission is invisible until the first surface imports one, which is
    # how it went unnoticed twice before.
    #
    # Phase 15A: the agent-client tier.
    "director.py",
    # Phase 16C: notes, strategies, progress claims, the note-output trio, and
    # the legacy-upgrade contract.
    "notes.py", "strategies.py", "progress_claims.py", "note_outputs.py",
    "upgrade_audit.py",
)
STAGE_DIRS = ("surfaces", "schemas", "styles", "fonts", "vendor")

LAUNCHER_DIR = os.path.join(ROOT, "launchers")

# The stable name every launcher shim resolves at double-click time
# (launchers/itembank.bat|.command|.desktop all name `itembank.pyz`). The
# canonical, updater-picked artifact stays versioned (`itembank-<version>.pyz`,
# see surfaces/update.py:_ASSET_RE); this is the same bytes under the name a
# fresh download expects, so the two cannot drift.
STABLE_ARTIFACT_NAME = "itembank.pyz"

# One branch, no more: the update handoff attempt, guarded so a broken
# updater can never stop the tool from starting. Every launch of the built
# artifact first offers a newer, already-verified sibling the chance to take
# over as a fresh process (surfaces/update.py:handoff) before falling
# through to the CLI exactly as before.
MAIN_TEMPLATE = (
    "import os, sys\n"
    "sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))\n"
    "try:\n"
    "    from surfaces.update import handoff\n"
    "    handoff(sys.argv[1:])\n"
    "except Exception:\n"
    "    pass\n"
    "from surfaces.cli import main\n"
    "main()\n"
)


def stage(tmpdir):
    for name in STAGE_FILES:
        shutil.copy2(os.path.join(ROOT, name), os.path.join(tmpdir, name))
    for name in STAGE_DIRS:
        shutil.copytree(
            os.path.join(ROOT, name), os.path.join(tmpdir, name),
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    with open(os.path.join(tmpdir, "__main__.py"), "w", encoding="utf-8") as fh:
        fh.write(MAIN_TEMPLATE)


def build(out_dir):
    """Stage into a fresh temp directory and zipapp it into
    `<out_dir>/itembank-<itembank.__version__>.pyz`. Uncompressed, so every
    member stays plain, readable Python (DEL-02). Returns the artifact path.
    """
    os.makedirs(out_dir, exist_ok=True)
    stage_dir = tempfile.mkdtemp()
    try:
        stage(stage_dir)
        target = os.path.join(out_dir, "itembank-%s.pyz" % itembank.__version__)
        zipapp.create_archive(stage_dir, target, interpreter="/usr/bin/env python3")
    finally:
        shutil.rmtree(stage_dir, ignore_errors=True)
    return target


def sha256sums(out_dir):
    """Write SHA256SUMS.txt with one '<64 hex>  <filename>' line per file in
    out_dir other than SHA256SUMS.txt itself, sorted by filename so the file
    is byte-stable across runs.
    """
    target = os.path.join(out_dir, "SHA256SUMS.txt")
    names = sorted(
        f for f in os.listdir(out_dir)
        if f != "SHA256SUMS.txt" and os.path.isfile(os.path.join(out_dir, f)))
    with open(target, "w", encoding="utf-8") as fh:
        for name in names:
            digest = hashlib.sha256(
                open(os.path.join(out_dir, name), "rb").read()).hexdigest()
            fh.write("%s  %s\n" % (digest, name))
    return target


def latest_json(out_dir, tag, installer_name, signature):
    """Write the `latest.json` tauri-plugin-updater manifest beside
    SHA256SUMS.txt (13-RESEARCH section 2 table): one GitHub Releases
    channel, two consumers -- the Python updater reads SHA256SUMS.txt, the
    Tauri updater reads this manifest, both from the same tag (D-08).

    `signature` is the base64 minisign signature over the installer bytes,
    produced by the release pipeline's signing step (key material is a build
    secret, never committed).
    """
    payload = {
        "version": tag.lstrip("v"),
        "notes": "",
        "pub_date": datetime.datetime.now(datetime.timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"),
        "platforms": {
            "windows-x86_64": {
                "signature": signature,
                "url": "https://github.com/onionviolet/itembank/releases/"
                       "download/%s/%s" % (tag, installer_name),
            },
        },
    }
    target = os.path.join(out_dir, "latest.json")
    with open(target, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)
        fh.write("\n")
    return target


def latest_json_hook(out_dir):
    """The release-step wiring for `latest_json`: when the NSIS installer and
    its minisign signature are both present in out_dir, publish latest.json
    for the same tag beside SHA256SUMS.txt. Before the signing step produces
    them (or when makensis is absent and no installer exists), it writes
    nothing and returns None -- the CLI updater's SHA256SUMS.txt channel
    remains the only manifest, honestly.
    """
    installers = sorted(f for f in os.listdir(out_dir)
                        if f.endswith("-setup.exe"))
    sigs = sorted(f for f in os.listdir(out_dir) if f.endswith(".sig"))
    if not installers or not sigs:
        return None
    installer = installers[0]
    m = re.match(r"itembank-([^-]+)-setup\.exe$", installer)
    if not m:
        return None
    tag = "v" + m.group(1)
    signature = open(os.path.join(out_dir, sigs[0]),
                     encoding="utf-8").read().strip()
    return latest_json(out_dir, tag, installer, signature)


def capabilities_json_hook(out_dir):
    """Publish the checked-in capabilities.json (18-CONTEXT D-03) beside
    SHA256SUMS.txt from the same tag, the same release-step wiring shape
    latest_json_hook uses. The manifest is generated by
    tools/capabilities_manifest.py and committed; this copies those exact
    bytes, so the release asset and the repo file cannot diverge. Runs
    before sha256sums() in main() so the checksum file covers it.
    """
    src = os.path.join(ROOT, "capabilities.json")
    if not os.path.isfile(src):
        return None
    dst = os.path.join(out_dir, "capabilities.json")
    shutil.copy2(src, dst)
    return dst


def copy_launchers(out_dir):
    """Copy every file in launchers/ alongside the .pyz, so SHA256SUMS.txt
    covers the launcher shims too -- a release asset set whose checksum file
    names only one of its files certifies nothing about the rest.
    """
    for name in sorted(os.listdir(LAUNCHER_DIR)):
        src = os.path.join(LAUNCHER_DIR, name)
        dst = os.path.join(out_dir, name)
        shutil.copy2(src, dst)
        if os.name == "posix":
            # shutil.copy2() preserves mode on POSIX already, but make the
            # intent explicit: a shipped .command with the executable bit
            # stripped is not double-clickable at all.
            os.chmod(dst, os.stat(src).st_mode)


def copy_stable_artifact(artifact, out_dir):
    """Ship a stable `itembank.pyz` alongside the versioned artifact, so the
    launcher shims -- which name one file that does not change between
    releases -- resolve real bytes in a fresh release directory. Must run
    before sha256sums() so the checksum file covers both names.
    """
    dst = os.path.join(out_dir, STABLE_ARTIFACT_NAME)
    shutil.copy2(artifact, dst)
    return dst


def main():
    ap = argparse.ArgumentParser(description="Build the itembank release artifact.")
    ap.add_argument("--out", default="dist", help="output directory (default: dist)")
    a = ap.parse_args()

    artifact = build(a.out)
    print("%d bytes -> %s" % (os.path.getsize(artifact), artifact))
    copy_launchers(a.out)
    copy_stable_artifact(artifact, a.out)
    capabilities_json_hook(a.out)
    sha256sums(a.out)
    latest_json_hook(a.out)
    n = sum(1 for f in os.listdir(a.out)
            if f != "SHA256SUMS.txt" and os.path.isfile(os.path.join(a.out, f)))
    print("%d artifacts -> %s" % (n, a.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
