#!/usr/bin/env python3
"""Recompute every checksum VENDORED.md records and fail on a mismatch.

`.planning/SUPPLY-CHAIN-POLICY.md` section 2.3 requires CI to recompute and
compare, and section 5 says a threat table may no longer accept supply-chain
risk on the grounds that no dependency is installed. This script is the
mitigation that replaces that stale one, so a tampered or accidentally edited
vendored artifact is a build failure rather than a promise in a policy
document.

Three row kinds, because the table records three different things:

  a file path      recompute its SHA-256 and compare
  a pointer        the SHA-256 cell reads `see <manifest>`; follow it and
                   verify every file that manifest names, so one fact has one
                   record instead of two that drift
  a package pin    the wheel is installed from PyPI and is not committed, so
                   verify the row against its pin line in
                   deps/source-adapter-pins.txt instead of against bytes

A row naming a parked package fails outright: PyMuPDF and ebooklib are parked
on an explicit AGPL decision (D-14C-2), and the parking must not be
bypassable by quietly adding a table row.

Stdlib only, exit 0 on success, exit 1 with a named artifact on any failure.
"""
import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, "VENDORED.md")
# Every pins file under deps/ is searched for a package row's pin line.
# Hardcoding one file broke the first time a second surface adopted a pinned
# package (17A-04's dev-only Playwright harness beside 14C's adapters).
PINS_DIR = os.path.join(ROOT, "deps")

PARKED = ("pymupdf", "fitz", "ebooklib")

_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def fail(message):
    print("FAIL: " + message)
    sys.exit(1)


def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def table_rows(text):
    """Every data row of every pipe table in the document, as cell lists."""
    rows = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        if set(stripped) <= set("|- :"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) < 8:
            continue
        if cells[0].lower() == "artifact":
            continue
        rows.append(cells)
    return rows


def check_pointer(artifact, pointer, verified):
    match = re.search(r"`?([\w./-]+\.json)`?", pointer)
    if not match:
        fail("%s: the SHA-256 cell is a pointer this checker cannot follow: "
             "%r" % (artifact, pointer))
    manifest_rel = match.group(1)
    manifest_path = os.path.join(ROOT, manifest_rel)
    if not os.path.isfile(manifest_path):
        fail("%s: points at %s, which does not exist"
             % (artifact, manifest_rel))
    with open(manifest_path, encoding="utf-8") as fh:
        data = json.load(fh)
    directory = os.path.join(ROOT, artifact)
    if not os.path.isdir(directory):
        fail("%s: the pointed-at directory does not exist" % artifact)
    checked = 0
    for family in (data.get("families") or {}).values():
        for entry in family.get("files") or []:
            name = entry.get("name")
            recorded = entry.get("sha256")
            if not name or not recorded:
                continue
            path = os.path.join(directory, name)
            if not os.path.isfile(path):
                continue
            computed = sha256_of(path)
            if computed != recorded:
                fail("%s/%s: recorded %s but computed %s"
                     % (artifact, name, recorded, computed))
            checked += 1
    if not checked:
        fail("%s: the manifest named no file inside it, so this row verifies "
             "nothing" % artifact)
    verified.append("%s (%d files via %s)" % (artifact, checked, manifest_rel))


def check_pin(artifact, pin, verified):
    pin_files = sorted(
        name for name in os.listdir(PINS_DIR)
        if name.endswith("-pins.txt")) if os.path.isdir(PINS_DIR) else []
    if not pin_files:
        fail("%s: no deps/*-pins.txt exists, so no package row can be "
             "verified" % artifact)
    wanted = "%s==%s" % (artifact, pin)
    for name in pin_files:
        with open(os.path.join(PINS_DIR, name), encoding="utf-8") as fh:
            if wanted in fh.read():
                verified.append("%s (pin %s, deps/%s)" % (artifact, pin, name))
                return
    fail("%s: no pin line reading %r in any deps/*-pins.txt"
         % (artifact, wanted))


def main():
    if not os.path.isfile(MANIFEST):
        fail("VENDORED.md is missing")
    with open(MANIFEST, encoding="utf-8") as fh:
        text = fh.read()

    verified = []
    for cells in table_rows(text):
        artifact = cells[0].strip("`")
        pin = cells[1].strip("`")
        recorded = cells[4].strip("`")
        lowered = artifact.lower()
        for parked in PARKED:
            if parked in lowered:
                fail("%s: this package is parked on an explicit AGPL decision "
                     "(D-14C-2) and must not carry a VENDORED.md row"
                     % artifact)

        path = os.path.join(ROOT, artifact)
        if recorded.lower().startswith("see"):
            check_pointer(artifact, recorded, verified)
            continue
        if os.path.sep in artifact or "/" in artifact:
            if not os.path.exists(path):
                fail("%s: recorded in VENDORED.md but missing from the tree"
                     % artifact)
            if not _SHA256.match(recorded):
                fail("%s: the SHA-256 cell is not a hash: %r"
                     % (artifact, recorded))
            computed = sha256_of(path)
            if computed != recorded:
                fail("%s: recorded %s but computed %s"
                     % (artifact, recorded, computed))
            verified.append(artifact)
            continue
        check_pin(artifact, pin, verified)

    for name in verified:
        print("ok: " + name)
    print("%d vendored artifacts match their recorded checksums"
          % len(verified))
    return 0


if __name__ == "__main__":
    sys.exit(main())
