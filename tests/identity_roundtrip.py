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
import discovery                                             # noqa: E402
import evidence                                              # noqa: E402
import authoring                                              # noqa: E402
import model                                                  # noqa: E402
import fixtures.corpus_14a as corpus_14a                     # noqa: E402

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


def _snapshot(roots):
    """(relative path, size, mtime_ns) for every regular file under
    `roots`, access time deliberately excluded because reading a file
    legitimately updates it."""
    rows = []
    for root in roots:
        for dirpath, dirs, files in os.walk(root, followlinks=False):
            dirs.sort()
            for f in sorted(files):
                p = os.path.join(dirpath, f)
                try:
                    st = os.lstat(p)
                except OSError:
                    continue
                rel = os.path.relpath(p, root).replace(os.sep, "/")
                rows.append((root, rel, st.st_size, st.st_mtime_ns))
    return sorted(rows)


def check_discovery():
    d = tempfile.mkdtemp()
    try:
        corpus = corpus_14a.build_corpus(d, size="1k")
        roots = corpus["roots"]
        if len(roots) != 3:
            fail("build_corpus did not produce exactly three roots")

        report = discovery.run_report(roots)
        for key in ("roots", "counts", "entries", "complete", "cancelled",
                    "denied", "refused", "unavailable"):
            if key not in report:
                fail("run_report() is missing key %r" % key)
        if report["complete"] is not True:
            fail("an uninterrupted run did not report complete True")

        for entry in report["entries"]:
            if entry["state"] not in discovery.ENTRY_STATES:
                fail("entry has an unrecognized state: %r" % entry["state"])

        fps_by_relname = {}
        for e in report["entries"]:
            if e["path"].endswith("duplicate_a.md") or e["path"].endswith("duplicate_b.md"):
                fps_by_relname[e["path"]] = e
        names = list(fps_by_relname.keys())
        if len(names) != 2:
            fail("expected exactly two duplicate-pair entries, found %r" % names)
        e_a, e_b = fps_by_relname[names[0]], fps_by_relname[names[1]]
        if e_a["fingerprint"] != e_b["fingerprint"]:
            fail("the duplicate-fingerprint pair did not fingerprint identically")
        if e_a["path"] == e_b["path"]:
            fail("the duplicate-fingerprint pair reported the same path")
        rec_a = identity.mint_object("source", e_a["path"], None, "human", "w", "mint")
        rec_a["fingerprint"] = e_a["fingerprint"]
        rec_b = identity.mint_object("source", e_b["path"], None, "human", "w", "mint")
        rec_b["fingerprint"] = e_b["fingerprint"]
        if len(identity.copy_candidates([rec_a, rec_b])) != 1:
            fail("identity.copy_candidates() did not report the duplicate pair")

        before = _snapshot(roots)
        discovery.run_report(roots)
        after = _snapshot(roots)
        if before != after:
            fail("discovery mutated the corpus: before/after snapshot differs")

        gen = discovery.inventory(roots)
        first_five = [next(gen) for _ in range(5)]
        if len(first_five) != 5:
            fail("consuming five yields of inventory() did not return five entries")

        count_box = {"n": 0}

        def cancel_after_ten():
            count_box["n"] += 1
            return count_box["n"] > 10

        cancelled_report = discovery.run_report(roots, cancel=cancel_after_ten)
        if cancelled_report["cancelled"] is not True or cancelled_report["complete"] is not False:
            fail("a cancel firing after ten entries did not report cancelled True, complete False")
        expected_reason = ("cancelled by caller; the entries after %s were "
                            "not inventoried" % cancelled_report["entries"][-1]["path"])
        if cancelled_report["omitted_reason"] != expected_reason:
            fail("omitted_reason did not match the expected exact string: %r"
                 % cancelled_report["omitted_reason"])

        last_path = cancelled_report["entries"][-1]["path"]
        resumed_report = discovery.run_report(roots, resume_after=last_path)
        full_report = discovery.run_report(roots)
        concatenated = [e["path"] for e in cancelled_report["entries"]] + \
            [e["path"] for e in resumed_report["entries"]]
        full_paths = [e["path"] for e in full_report["entries"]]
        if concatenated != full_paths:
            fail("the concatenation of the cancelled and resumed runs did "
                 "not equal one uninterrupted run's entry list")

        if corpus["symlinks"]:
            out_link_entries = [e for e in report["entries"]
                                 if e["state"] == "symlink_out_of_root"]
            if not out_link_entries:
                fail("the out-of-root symlink was not reported as symlink_out_of_root")
            if out_link_entries[0]["path"] not in report["refused"]:
                fail("the out-of-root symlink's path is not listed in report['refused']")
            if out_link_entries[0]["fingerprint"] is not None:
                fail("the out-of-root symlink entry carries a fingerprint; its target was read")
            outside_mtime_before = os.stat(corpus["outside_target"]).st_mtime_ns
            discovery.run_report(roots)
            outside_mtime_after = os.stat(corpus["outside_target"]).st_mtime_ns
            if outside_mtime_before != outside_mtime_after:
                fail("the out-of-root symlink target's mtime changed; it was read")

            cycle_entries = [e for e in report["entries"] if e["state"] == "symlink_cycle"]
            if not cycle_entries:
                fail("the symlink cycle was not reported as symlink_cycle")
        else:
            print("SKIP: symlink assertions (os.symlink unavailable on this platform)")

        if corpus["denied_mode"] == "read":
            denied_rel = os.path.relpath(corpus["denied_path"],
                                          [r for r in roots if corpus["denied_path"].startswith(r)][0])
            denied_rel = denied_rel.replace(os.sep, "/")
            denied_entries = [e for e in report["entries"] if e["state"] == "denied"]
            if not denied_entries:
                fail("the permission-denied pocket was not reported as denied")
            if denied_rel not in report["denied"]:
                fail("the denied path is not listed in report['denied']")
        else:
            print("SKIP: read-denial assertion (os.chmod cannot deny read on "
                  "this platform); write refusal is proven in tests/journal_roundtrip.py")

        missing_root = os.path.join(d, "does_not_exist_root")
        mixed_report = discovery.run_report(roots + [missing_root])
        if missing_root not in mixed_report["unavailable"]:
            fail("a missing root was not reported in unavailable")
        if not any(e["state"] == "readable" for e in mixed_report["entries"]):
            fail("a missing root among valid roots stopped the rest of the inventory")

        empty_report = discovery.run_report([])
        if empty_report["entries"] != [] or empty_report["complete"] is not True:
            fail("discovery.inventory([], ...) did not return an empty, complete result")

        if discovery.inside_any_root("/etc/passwd", roots):
            fail("inside_any_root() reported /etc/passwd as inside the corpus roots")

        try:
            discovery.run_report(["/some/path/outside"], approved_roots=roots)
            fail("run_report() with an unapproved root did not raise")
        except discovery.DiscoveryError as exc:
            if exc.code != "discovery.root_unapproved":
                fail("run_report() with an unapproved root raised the wrong code: %r"
                     % exc.code)

        if hasattr(discovery, "journal") or hasattr(discovery, "subprocess") or \
                hasattr(discovery, "urllib"):
            fail("discovery module carries a write/execute/network-capable attribute")

        print("OK check_discovery")
    finally:
        corpus_14a.teardown_corpus(d)


def check_regressions():
    bank_raw = b"CORRECT: B \n"
    bank_stripped = b"CORRECT: B\n"
    if identity.object_fingerprint(bank_raw, "bank") == \
            identity.object_fingerprint(bank_stripped, "bank"):
        fail("the keyed-content carve-out did not hold: a trailing space "
             "inside a CORRECT: line did not change the bank fingerprint")
    if identity.object_fingerprint(bank_raw, "course") != \
            identity.object_fingerprint(bank_stripped, "course"):
        fail("the same text fingerprinted as kind course was not "
             "trailing-whitespace normalized")

    fixture_path = os.path.join(ROOT, "fixtures", "lesson_bank.md")
    qs = model.load(fixture_path)
    before_fp = model.content_fingerprint(qs[0])
    with open(fixture_path, "rb") as fh:
        raw = fh.read()
    identity.object_fingerprint(raw, "bank")   # side-effect-free by construction
    qs_again = model.load(fixture_path)
    after_fp = model.content_fingerprint(qs_again[0])
    if before_fp != after_fp:
        fail("calling identity.object_fingerprint() changed "
             "model.content_fingerprint()'s scoring-relevant digest")

    rec_empty = identity.mint_object("source", "s.md", b"x", "human", "w", "mint",
                                      rights={})
    rec_none = identity.mint_object("source", "s.md", b"x", "human", "w", "mint",
                                     rights=None)
    if rec_empty["rights"] != identity.rights_default() or \
            rec_none["rights"] != identity.rights_default():
        fail("rights={} and rights=None did not both default to rights_default()")

    r1 = identity.mint_object("bank", "a.md", b"1", "human", "w", "mint")
    r2 = identity.mint_object("bank", "b.md", b"2", "human", "w", "mint")
    r3 = identity.mint_object("course", "c.md", b"3", "human", "w", "mint")
    shuffled = [r3, r1, r2]
    import random
    random.shuffle(shuffled)
    rows1 = identity.registry_rows(shuffled)
    random.shuffle(shuffled)
    rows2 = identity.registry_rows(shuffled)
    if [r["object_id"] for r in rows1] != [r["object_id"] for r in rows2]:
        fail("registry_rows() ordering was not stable across a shuffled input")

    same_a = identity.mint_object("source", "x.md", b"same", "human", "w", "mint")
    same_b = identity.mint_object("source", "y.md", b"same", "human", "w", "mint")
    pairs = identity.copy_candidates([same_a, same_b])
    if len(pairs) != 1:
        fail("copy_candidates() did not return the pair for equal "
             "fingerprints with different ids")
    if identity.copy_candidates([r1, r2]):
        fail("copy_candidates() returned candidates for differing fingerprints")

    print("OK check_regressions")


def main():
    check_identity()
    check_discovery()
    check_regressions()
    print("OK identity_roundtrip")


if __name__ == "__main__":
    main()
