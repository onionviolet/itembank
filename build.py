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
import hashlib
import os
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
    "schema_validate.py", "resources.py",
)
STAGE_DIRS = ("surfaces", "schemas")

# Four lines, no logic -- a later plan adds the update handoff here, and a
# template that already carries branches is a template that gets edited badly.
MAIN_TEMPLATE = (
    "import os, sys\n"
    "sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))\n"
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


def main():
    ap = argparse.ArgumentParser(description="Build the itembank release artifact.")
    ap.add_argument("--out", default="dist", help="output directory (default: dist)")
    a = ap.parse_args()

    artifact = build(a.out)
    print("%d bytes -> %s" % (os.path.getsize(artifact), artifact))
    checksums = sha256sums(a.out)
    print("checksums -> %s" % checksums)
    return 0


if __name__ == "__main__":
    sys.exit(main())
