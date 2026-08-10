#!/usr/bin/env python3
"""The [!KEY] Anki export path (plan 03.1-03 Task 2): a multi-directive TSV
whose #guid column carries each block's minted [ID:], so re-export after a
body edit is an update, never a duplicate -- proven by round-trip, not
asserted (D-22).

Standard library only, runnable as `python tests/anki_keys_roundtrip.py`.
"""
import json, os, re, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import itembank                                            # noqa: E402


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def run(args, cwd=None):
    r = subprocess.run([sys.executable, os.path.join(ROOT, "itembank.py")]
                       + list(args), cwd=cwd, capture_output=True, text=True)
    return r


def key_bank(tmp, lesson_body):
    """A bank whose lesson body carries `> [!KEY]` callouts -- no items
    needed, because the keys export path reads only the lesson machinery."""
    bank = os.path.join(tmp, "keys_bank.md")
    open(bank, "w", encoding="utf-8").write(
        "# Keys bank\n\n## LESSON\n\n%s\n" % lesson_body.strip())
    return bank


def read_tsv(path):
    text = open(path, encoding="utf-8").read()
    lines = [l for l in text.splitlines() if l.strip()]
    directives = [l for l in lines if l.startswith("#")]
    body = [l for l in lines if not l.startswith("#")]
    return directives, body


def test_export_keys_header_and_rows():
    """`itembank export keys <bank>` writes `<bank>_keys.tsv` beside the bank
    with the exact multi-directive header and one row per key block."""
    tmp = tempfile.mkdtemp()
    bank = key_bank(
        tmp,
        "### Airway\n\n"
        "> [!KEY] OPA indications\n"
        "> [ID: 1111111111111111]\n"
        "> [HASH: sha256:abc]\n"
        "> The OPA is {{indicated when the tongue obstructs}}.\n\n"
        "> [!KEY] OPA cautions\n"
        "> [ID: 2222222222222222]\n"
        "> [HASH: sha256:def]\n"
        "> Do not force it past resistance.\n")
    res = run(["export", bank, "--format", "keys"])
    if res.returncode != 0:
        fail("export keys failed: " + res.stdout + res.stderr)
    out = os.path.join(tmp, "keys_bank_keys.tsv")
    if not os.path.exists(out):
        fail("export keys did not write <bank>_keys.tsv at %s" % out)
    directives, rows = read_tsv(out)
    for want in ("#separator:tab", "#html:true", "#guid column:1",
                 "#notetype column:2", "#deck column:3", "#tags column:6"):
        if want not in directives:
            fail("missing directive %r in %r" % (want, directives))
    if len(rows) != 3:                       # header row + 2 key rows
        fail("expected header + 2 key rows, got %r" % rows)
    header = rows[0]
    if header != "Guid\tNotetype\tDeck\tFront\tBack\tTags":
        fail("header row wrong: %r" % header)
    if not rows[1].startswith("1111111111111111\tCloze\tkeys_bank\t"):
        fail("cloze key row wrong: %r" % rows[1])
    if not rows[2].startswith("2222222222222222\tBasic\tkeys_bank\t"
                              "OPA cautions\t"):
        fail("basic key row wrong: %r" % rows[2])


def test_export_keys_guid_round_trip():
    """Export, edit a key body keeping its [ID:], export again: the second
    file's guid column for that block is byte-identical (D-22's literal
    round-trip)."""
    tmp = tempfile.mkdtemp()
    bank = key_bank(
        tmp,
        "### Airway\n\n"
        "> [!KEY] OPA indications\n"
        "> [ID: 1111111111111111]\n"
        "> [HASH: sha256:abc]\n"
        "> The OPA is indicated when the tongue obstructs.\n")
    if run(["export", bank, "--format", "keys"]).returncode != 0:
        fail("first export failed")
    out = os.path.join(tmp, "keys_bank_keys.tsv")
    _, rows1 = read_tsv(out)
    guid1 = rows1[1].split("\t")[0]
    if guid1 != "1111111111111111":
        fail("guid column must be the block's [ID:], got %r" % guid1)

    text = open(bank, encoding="utf-8").read()
    edited = text.replace("indicated when the tongue obstructs",
                          "indicated when the tongue obstructs the airway")
    if edited == text:
        fail("test fixture edit produced no change")
    open(bank, "w", encoding="utf-8").write(edited)
    if run(["export", bank, "--format", "keys"]).returncode != 0:
        fail("second export failed")
    _, rows2 = read_tsv(out)
    guid2 = rows2[1].split("\t")[0]
    if guid2 != guid1:
        fail("guid did not round-trip after a body edit: %r -> %r"
             % (guid1, guid2))


def test_export_keys_cloze_and_basic_derivation():
    """A body carrying {{...}} compiles to Anki-native {{c1::...}} cloze
    syntax; a titled non-cloze body uses Basic with the title as Front; a
    body with neither is refused as key.no_front."""
    tmp = tempfile.mkdtemp()
    bank = key_bank(
        tmp,
        "### Airway\n\n"
        "> [!KEY] OPA indications\n"
        "> [ID: 1111111111111111]\n"
        "> [HASH: sha256:abc]\n"
        "> The OPA is {{indicated when the tongue obstructs}}, then "
        "{{2::lubricated}}.\n")
    if run(["export", bank, "--format", "keys"]).returncode != 0:
        fail("cloze export failed")
    _, rows = read_tsv(os.path.join(tmp, "keys_bank_keys.tsv"))
    front = rows[1].split("\t")[3]
    if "{{c1::indicated when the tongue obstructs}}" not in front:
        fail("simple cloze did not compile to {{c1::...}}: %r" % front)
    if "{{c2::lubricated}}" not in front:
        fail("numbered cloze must keep its number: %r" % front)

    bank2 = key_bank(
        tmp,
        "### Airway\n\n"
        "> [!KEY]\n"
        "> [ID: 2222222222222222]\n"
        "> [HASH: sha256:def]\n"
        "> Just a body with no cloze.\n")
    res = run(["export", bank2, "--format", "keys"])
    if res.returncode == 0:
        fail("a body with neither title nor cloze must refuse export")
    if "key.no_front" not in res.stdout + res.stderr:
        fail("the refusal must name key.no_front: %r"
             % (res.stdout + res.stderr))


def test_export_keys_lint_refusal_and_force():
    """A bank whose key blocks carry lint errors refuses `export keys`
    without --force, matching the item export's behavior."""
    tmp = tempfile.mkdtemp()
    bank = key_bank(
        tmp,
        "### Airway\n\n"
        "> [!KEY]\n"
        "> [ID: 1111111111111111]\n"
        "> [HASH: sha256:abc]\n"
        "> A body with no title and no cloze.\n")
    res = run(["export", bank, "--format", "keys"])
    if res.returncode == 0:
        fail("export without --force must refuse a key-error bank")
    if "refusing to export a bank with key errors" not in res.stdout + res.stderr:
        fail("refusal copy missing: %r" % (res.stdout + res.stderr))
    forced = run(["export", bank, "--format", "keys", "--force"])
    if forced.returncode != 0:
        fail("--force must allow the export: " + forced.stdout)
    if not os.path.exists(os.path.join(tmp, "keys_bank_keys.tsv")):
        fail("--force export did not write the TSV")


test_export_keys_header_and_rows()
test_export_keys_guid_round_trip()
test_export_keys_cloze_and_basic_derivation()
test_export_keys_lint_refusal_and_force()
print("ok: anki keys roundtrip (multi-directive header, guid round-trip, "
      "cloze/basic derivation, no-front refusal, lint refusal + --force)")
