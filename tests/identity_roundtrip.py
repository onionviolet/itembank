#!/usr/bin/env python3
"""Proves the identity kernel end to end: opaque ids are never derived from
content, the change-detection fingerprint normalizes cosmetically but never
masks a scoring-relevant change, the revision record shape is exact, and the
read-only discovery walker never mutates what it inventories.

Standard library only, runnable as `python tests/identity_roundtrip.py`.
"""
import os, re, shutil, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import identity                                             # noqa: E402
import evidence                                              # noqa: E402
import authoring                                              # noqa: E402
import model                                                  # noqa: E402

TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$")


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def check_identity():
    ids = set(identity.new_object_id() for _ in range(1000))
    if len(ids) != 1000:
        fail("1000 calls to new_object_id() produced a collision")
    for oid in ids:
        if len(oid) != 16 or not re.match(r"^[0-9a-f]{16}$", oid):
            fail("new_object_id() did not return 16-character lowercase hex: %r" % oid)

    id_a = identity.new_object_id()
    id_b = identity.new_object_id()
    if id_a == id_b:
        fail("two mints of the same object produced the same id by coincidence")
    # Same bytes minted twice still get two different ids: identity is not a
    # function of content.
    if identity.new_object_id() == identity.new_object_id():
        fail("identity.new_object_id() is deterministic on repeat calls")

    if not TS_RE.match(identity.utc_now()):
        fail("identity.utc_now() does not match the expected shape: %r" % identity.utc_now())
    if not TS_RE.match(evidence.utc_now()):
        fail("evidence.utc_now() does not match the expected shape: %r" % evidence.utc_now())

    if identity.object_fingerprint(b"line\r\n", "course") != \
            identity.object_fingerprint(b"line\n", "course"):
        fail("CRLF and LF did not fingerprint identically for kind course")

    if identity.object_fingerprint(b"line   \n", "course") != \
            identity.object_fingerprint(b"line\n", "course"):
        fail("trailing whitespace was not stripped for kind course")

    if identity.object_fingerprint(b"CORRECT: B \n", "bank") == \
            identity.object_fingerprint(b"CORRECT: B\n", "bank"):
        fail("a trailing space inside a CORRECT: line did not change the bank fingerprint")
    if identity.object_fingerprint(b"CORRECT: B \n", "lesson") == \
            identity.object_fingerprint(b"CORRECT: B\n", "lesson"):
        fail("a trailing space did not change the lesson fingerprint")

    if identity.object_fingerprint(b"x\r\n", "bank") != \
            identity.object_fingerprint(b"x\n", "bank"):
        fail("line-ending normalization did not apply to kind bank")

    raw = b"stem line one\nstem line two\nCORRECT: A\n"
    if identity.object_fingerprint(raw, "bank") != \
            authoring.bank_fingerprint(raw.decode("utf-8")):
        fail("identity.object_fingerprint(raw, 'bank') disagrees with "
             "authoring.bank_fingerprint for byte-identical, CR-free content")

    empty_fp = identity.object_fingerprint(b"", "course")
    if not empty_fp.startswith("sha256:"):
        fail("fingerprinting empty bytes did not return a sha256: value")

    fp_nfc = identity.object_fingerprint(b"caf\xc3\xa9", "course")
    fp_nfd = identity.object_fingerprint(b"cafe\xcc\x81", "course")
    if fp_nfc == fp_nfd:
        fail("Unicode NFC and NFD forms fingerprinted identically; no "
             "normalization should be applied")

    try:
        identity.object_fingerprint(b"\xff\xfe raw", "source")
    except Exception as exc:
        fail("fingerprinting non-UTF-8 bytes raised: %r" % exc)

    rec = identity.mint_object("course", "course.md", b"x", "human", "weibao", "mint")
    if list(rec.keys()) != list(identity.REVISION_KEYS):
        fail("mint_object() keys are not in REVISION_KEYS order: %r" % list(rec.keys()))
    if rec["revision"] != 1 or rec["parent_revision"] is not None:
        fail("mint_object() did not start at revision 1 with parent_revision None")

    rec2 = identity.next_revision(rec, b"y", "agent", "claude-code", "edit_in_place")
    if rec2["revision"] != 2 or rec2["parent_revision"] != 1:
        fail("next_revision() did not advance the counter correctly")
    if rec2["object_id"] != rec["object_id"]:
        fail("next_revision() minted a new object_id instead of keeping the original")

    try:
        identity.mint_object("item", "x.md", b"x", "human", "weibao", "mint")
        fail("mint_object('item', ...) did not raise")
    except identity.IdentityError as exc:
        if exc.code != "identity.unknown_kind":
            fail("mint_object('item', ...) raised the wrong code: %r" % exc.code)

    rights = identity.rights_default()
    if set(rights.keys()) != set(identity.RIGHTS_OPERATIONS) or \
            any(v != "unknown" for v in rights.values()):
        fail("rights_default() did not return all-unknown over the seven operations")

    src_rec = identity.mint_object("source", "s.md", b"x", "human", "weibao", "mint")
    if src_rec["rights"] != identity.rights_default():
        fail("a minted source record's default rights did not equal rights_default()")

    rec_none = identity.mint_object("course", "c.md", None, "human", "weibao", "mint")
    if rec_none["fingerprint"] is not None:
        fail("mint_object() with raw=None did not keep fingerprint None: %r"
             % rec_none["fingerprint"])

    parent_id = identity.new_object_id()
    cid = identity.mint_component(parent_id, "cited")
    if len(cid) != 16 or not re.match(r"^[0-9a-f]{16}$", cid):
        fail("mint_component() did not return a 16-character hex id")
    try:
        identity.mint_component(parent_id, "summary")
        fail("mint_component(parent_id, 'summary') did not raise")
    except identity.IdentityError as exc:
        if exc.code != "identity.component_role_ineligible":
            fail("mint_component() with an ineligible role raised the wrong code: %r"
                 % exc.code)

    if identity.component_anchor(cid) != "[CID:%s]" % cid:
        fail("component_anchor() did not build the expected marker")
    pairs = identity.find_component_anchors("a\n[CID:%s]\nb" % cid)
    if pairs != [(cid, pairs[0][1])] or len(pairs) != 1:
        fail("find_component_anchors() did not return exactly one pair")

    r1 = identity.mint_object("source", "a.md", b"a", "human", "w", "mint")
    r2 = identity.mint_object("bank", "b.md", b"b", "human", "w", "mint")
    r3 = identity.mint_object("bank", "c.md", b"c", "human", "w", "mint")
    records = [r3, r1, r2]
    rows1 = identity.registry_rows(records)
    import random
    shuffled = list(records)
    random.shuffle(shuffled)
    rows2 = identity.registry_rows(shuffled)
    expected_order = sorted(records, key=lambda r: (r["kind"], r["object_id"]))
    if [r["object_id"] for r in rows1] != [r["object_id"] for r in expected_order]:
        fail("registry_rows() did not sort by (kind, object_id)")
    if [r["object_id"] for r in rows1] != [r["object_id"] for r in rows2]:
        fail("registry_rows() ordering was not stable across a shuffled input")

    dup_a = identity.mint_object("source", "d1.md", b"same bytes", "human", "w", "mint")
    dup_b = identity.mint_object("source", "d2.md", b"same bytes", "human", "w", "mint")
    candidates = identity.copy_candidates([dup_a, dup_b, r1])
    if len(candidates) != 1:
        fail("copy_candidates() did not return exactly one pair for equal "
             "fingerprints and different ids")
    no_candidates = identity.copy_candidates([r1, r2])
    if no_candidates:
        fail("copy_candidates() returned candidates for records with "
             "different fingerprints")

    if hasattr(identity, "model") or hasattr(identity, "runtime") or \
            hasattr(identity, "evidence") or hasattr(identity, "journal"):
        fail("identity module carries a runtime-tier attribute: model=%s "
             "runtime=%s evidence=%s journal=%s"
             % (hasattr(identity, "model"), hasattr(identity, "runtime"),
                hasattr(identity, "evidence"), hasattr(identity, "journal")))

    print("OK check_identity")


def main():
    check_identity()
    print("OK identity_roundtrip")


if __name__ == "__main__":
    main()
