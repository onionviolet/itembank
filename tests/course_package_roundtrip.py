#!/usr/bin/env python3
"""PORT-03, asserted: a synthetic course is exported as a package, restored on
a destination that never saw the original, validated entry by entry against
its manifest by recomputation, and every loss is named rather than dropped.

The requirement's own sentence is the bar this file holds: "Export is not
complete until a clean-machine, offline restore validates a manifest and
reports every loss, restoring all supported canonical objects and evidence."

An export that has never been restored is a promise, not a backup. So the
restore here runs against a destination with no shared journal, no shared
registry, no shared evidence store, and no shared settings, with `HOME`,
`APPDATA`, and `XDG_DATA_HOME` pointed at a second empty directory for the
duration, and it recomputes every payload fingerprint rather than reading the
manifest's own claim back to itself.

The archive assertions cover the one place in Phase 14B where the project's
single-local-user posture stops applying: a package received from another
person is untrusted input the moment it crosses a machine boundary.

Standard library only, runnable as `python tests/course_package_roundtrip.py`.
"""
import json, os, shutil, subprocess, sys, tempfile, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import course                                                # noqa: E402
import course_package                                        # noqa: E402
import evidence                                              # noqa: E402
import graph                                                 # noqa: E402
import identity                                              # noqa: E402
import journal                                               # noqa: E402
import fixtures.corpus_14b as corpus_14b                     # noqa: E402


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def eq(got, want, what):
    if got != want:
        fail("%s: want %r, got %r" % (what, want, got))


def raises(fn, exc_type, code, what):
    try:
        fn()
    except exc_type as err:
        if getattr(err, "code", None) != code:
            fail("%s: want code %r, got %r (%s)"
                 % (what, code, getattr(err, "code", None), err))
        return err
    except Exception as err:                                 # noqa: BLE001
        fail("%s: want %s, got %s: %s"
             % (what, exc_type.__name__, type(err).__name__, err))
    fail("%s: nothing was raised" % what)


def rows_for(manifest, category):
    return [r for r in manifest["loss_report"] if r["category"] == category]


def only_row(manifest, category, target, what):
    got = [r for r in rows_for(manifest, category) if r["target"] == target]
    if len(got) != 1:
        fail("%s: want exactly one %s row for %s, got %d"
             % (what, category, target, len(got)))
    return got[0]


# ------------------------------------------------------------------ task 2

def check_manifest_and_losses():
    """The manifest shape, the packaging rights gate, and every named loss."""
    tmp = tempfile.mkdtemp(prefix="course_package_")
    try:
        built = corpus_14b.build_three_domains(tmp)
        meridian = built["domains"][0]
        lantern = built["domains"][2]
        root = meridian["root"]

        granted = corpus_14b.packaged_source(root, "carried-source")
        transform_only = corpus_14b.register_source(
            root, "transform-only", {"transform": "granted"})
        linked = corpus_14b.linked_source(root, "kept-where-it-lives")
        component = corpus_14b.component_object(root, "gated-block")
        vanished = corpus_14b.unreachable_root_case(root)

        manifest = course_package.build_manifest(root, root)

        eq(set(manifest.keys()), set(course_package.MANIFEST_KEYS),
           "the manifest key set")
        eq(len(course_package.MANIFEST_KEYS), 7, "the manifest carries seven keys")
        eq(manifest["schema_version"], course_package.PACKAGE_SCHEMA_VERSION,
           "the manifest schema version")
        eq(course_package.PACKAGE_SCHEMA_VERSION, 1, "PACKAGE_SCHEMA_VERSION")
        for entry in manifest["entries"]:
            eq(set(entry.keys()), set(course_package.MANIFEST_ENTRY_KEYS),
               "the manifest entry key set")

        ids = [e["object_id"] for e in manifest["entries"]]
        if meridian["source_object_id"] in ids:
            fail("a source whose rights are all unknown must not be packaged")
        if transform_only in ids:
            fail("a granted transform right must not imply a package right")
        if linked in ids:
            fail("a linked source is never copied into a package")
        if component in ids:
            fail("an unsupported kind must not be packaged")
        if vanished in ids:
            fail("an unreachable source must not be packaged")
        if granted not in ids:
            fail("a source granted the package right must be packaged")

        # RIGHTS-01: unknown and denied are both restrictive, and both named.
        row = only_row(manifest, "rights-restricted",
                       meridian["source_object_id"], "the all-unknown source")
        for want in ("package", "unknown"):
            if want not in row["reason"]:
                fail("the rights-restricted reason must name %r" % want)
        only_row(manifest, "rights-restricted", transform_only,
                 "the transform-granted, package-unknown source")

        # `lantern-computing` carries package: denied.
        lantern_manifest = course_package.build_manifest(lantern["root"],
                                                         lantern["root"])
        denied = only_row(lantern_manifest, "rights-restricted",
                          lantern["source_object_id"], "the denied source")
        if "denied" not in denied["reason"]:
            fail("a denied right must be named as denied, not as unknown")
        if lantern["source_object_id"] in [e["object_id"] for e
                                            in lantern_manifest["entries"]]:
            fail("a denied package right must exclude the payload")

        # Every loss category, named.
        eq(course_package.LOSS_CATEGORIES,
           ("external-link", "rights-restricted", "machine-local",
            "unreachable-source", "unsupported-kind"), "LOSS_CATEGORIES")
        link_row = only_row(manifest, "external-link", linked,
                            "the linked source")
        if "linked, not imported" not in link_row["reason"]:
            fail("the external-link reason must say linked, not imported")
        machine = only_row(manifest, "machine-local", "settings",
                           "machine-local settings")
        if "not included by design" not in machine["reason"]:
            fail("the machine-local reason must say not included by design")
        only_row(manifest, "unreachable-source", vanished,
                 "the vanished source")
        only_row(manifest, "unsupported-kind", component,
                 "the component object")

        text = course_package.loss_report_text(manifest)
        lines = text.split("\n")
        eq(lines[0], "# Package loss report", "the loss report heading")
        eq(lines[1], "", "a blank line follows the loss report heading")
        eq(lines[2], "| category | target | reason |",
           "the loss report column headers")
        eq(lines[3], "|---|---|---|", "the loss report rule row")
        empty = course_package.loss_report_text({"loss_report": []})
        eq(empty, "# Package loss report\n\nNo losses.\n",
           "a zero-loss report still says so in words")

        # Ordering is specified and stable when elements compare equal.
        eq(manifest["entries"],
           sorted(manifest["entries"], key=lambda e: (e["kind"], e["object_id"])),
           "manifest entries are sorted by kind then object id")
        eq(manifest["loss_report"],
           sorted(manifest["loss_report"],
                  key=lambda r: (r["category"], r["target"])),
           "loss rows are sorted by category then target")

        registry_file = journal.registry_path(root)
        data = json.load(open(registry_file, encoding="utf-8"))
        shuffled = {"schema_version": data["schema_version"],
                    "objects": {k: data["objects"][k]
                                for k in reversed(list(data["objects"]))}}
        open(registry_file, "w", encoding="utf-8").write(
            json.dumps(shuffled, ensure_ascii=False, indent=2) + "\n")
        second = course_package.build_manifest(root, root)
        for key in ("package_id", "created"):
            manifest.pop(key)
            second.pop(key)
        eq(json.dumps(second, sort_keys=True), json.dumps(manifest, sort_keys=True),
           "two manifests of an unchanged course are identical apart from "
           "package_id and created")

        # Two ids are two objects, never one deduplicated payload.
        twin_root = os.path.join(tmp, "twins")
        os.makedirs(twin_root)
        course.create_course(twin_root, "Twin Payloads", "agent", "corpus-14b")
        first_twin, second_twin = corpus_14b.duplicate_fingerprint_sources(
            twin_root)
        twin_manifest = course_package.build_manifest(twin_root, twin_root)
        twin_entries = [e for e in twin_manifest["entries"]
                        if e["object_id"] in (first_twin, second_twin)]
        eq(len(twin_entries), 2, "two byte-identical sources are two entries")
        eq(twin_entries[0]["fingerprint"], twin_entries[1]["fingerprint"],
           "the twin fixture really is byte-identical")
        twin_pkg = os.path.join(tmp, "twin_package")
        course_package.export_package(twin_root, twin_root, twin_pkg,
                                      manifest=twin_manifest)
        payloads = sorted(os.listdir(os.path.join(
            twin_pkg, course_package.PAYLOAD_DIRNAME)))
        eq(len(payloads), 3, "three payload files: the course and both twins")

        # A duplicate relative path is refused before anything is written.
        clash = course_package.build_manifest(root, root)
        clash["entries"] = list(clash["entries"]) + [dict(clash["entries"][0])]
        raises(lambda: course_package.export_package(
                   root, root, os.path.join(tmp, "clash_package"),
                   manifest=clash),
               course_package.PackageError, "package.duplicate_relpath",
               "two entries claiming the same payload path")

        # A real export writes the manifest, the payload, the evidence file,
        # and the loss report.
        pkg = os.path.join(tmp, "package")
        applied = course_package.export_package(root, root, pkg)
        eq(applied["state"], "applied", "a finished export is applied")
        report_path = os.path.join(pkg, course_package.LOSS_REPORT_FILENAME)
        eq(open(report_path, encoding="utf-8").read(),
           course_package.loss_report_text(applied),
           "LOSS-REPORT.md holds the loss report text")
        for entry in applied["entries"]:
            payload = os.path.join(pkg, course_package.PAYLOAD_DIRNAME,
                                   entry["object_id"] + ".md")
            if not os.path.exists(payload):
                fail("every manifest entry needs a payload file")
            raw = open(payload, "rb").read()
            eq(entry["fingerprint"],
               identity.object_fingerprint(raw, entry["kind"]),
               "the entry fingerprint is the payload's own")

        check_empty_course(tmp)
        check_interrupted_export(tmp)
        print("ok  manifest, rights gate, and named losses")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check_empty_course(tmp):
    """A course with nothing in it still exports and still restores."""
    root = os.path.join(tmp, "empty_course")
    os.makedirs(root)
    course.create_course(root, "Empty Course", "agent", "corpus-14b")
    pkg = os.path.join(tmp, "empty_package")
    manifest = course_package.export_package(root, root, pkg)
    eq(len(manifest["entries"]), 1,
       "an empty course packages exactly its own sidecar")
    eq(len(manifest["loss_report"]), 1,
       "an empty course loses exactly the machine-local settings row")
    eq(manifest["loss_report"][0]["category"], "machine-local",
       "the one loss row of an empty course")

    exported = os.path.join(pkg, course_package.EVIDENCE_DIRNAME,
                            course_package.EVIDENCE_FILENAME)
    if not os.path.exists(exported):
        fail("the evidence export must be present even when it is empty; "
             "absent and empty are two different claims")
    eq(os.path.getsize(exported), 0, "an empty evidence export is zero bytes")

    dest = os.path.join(tmp, "empty_restore")
    os.makedirs(dest)
    restored = course_package.restore_package(pkg, dest, "human", "weibao")
    eq(restored["entries_verified"], 1, "the empty package restores one entry")
    eq(restored["restore_losses"], [], "an empty package loses nothing on restore")


def check_interrupted_export(tmp):
    """An export killed between the prepared manifest and the payload leaves
    a manifest a restore refuses, never one that looks complete."""
    root = os.path.join(tmp, "interrupted_course")
    os.makedirs(root)
    course.create_course(root, "Interrupted Course", "agent", "corpus-14b")
    pkg = os.path.join(tmp, "interrupted_package")
    proc = subprocess.run([sys.executable, os.path.abspath(__file__),
                           "--kill-export", root, pkg],
                          capture_output=True)
    if proc.returncode == 0:
        fail("the interrupt harness exited cleanly; it did not interrupt")
    manifest_path = os.path.join(pkg, course_package.MANIFEST_FILENAME)
    if not os.path.exists(manifest_path):
        fail("the prepared manifest must be on disk before any payload")
    eq(json.load(open(manifest_path, encoding="utf-8"))["state"], "prepared",
       "an interrupted export leaves the manifest prepared")
    dest = os.path.join(tmp, "interrupted_restore")
    os.makedirs(dest)
    raises(lambda: course_package.restore_package(pkg, dest, "human", "weibao"),
           course_package.PackageError, "package.not_applied",
           "restoring an interrupted export")


# ------------------------------------------------------------------ task 3

def check_clean_restore():
    """The clean-machine, offline restore drill, honestly simulated."""
    tmp = tempfile.mkdtemp(prefix="course_package_restore_")
    saved_env = {k: os.environ.get(k)
                 for k in ("HOME", "APPDATA", "XDG_DATA_HOME")}
    try:
        built = corpus_14b.build_three_domains(tmp)
        meridian = built["domains"][0]
        root = meridian["root"]
        corpus_14b.packaged_source(root, "carried-source")
        seeded = [corpus_14b.seed_objective_evidence(root, objective_id)
                  for objective_id in meridian["objectives"][:2]]

        pkg = os.path.join(tmp, "package")
        manifest = course_package.export_package(root, root, pkg)
        sidecar_raw = open(course.sidecar_path(root), "rb").read()

        exported = os.path.join(pkg, course_package.EVIDENCE_DIRNAME,
                                course_package.EVIDENCE_FILENAME)
        lines = [ln for ln in open(exported, encoding="utf-8").read().split("\n")
                 if ln.strip()]
        eq(len(lines), len(seeded),
           "the evidence export carries this course's own events")

        # A package a restore validates must survive an untouched check first.
        verified = course_package.verify_manifest(pkg)
        eq(set(verified.keys()),
           {"entries_verified", "mismatches", "missing", "complete"},
           "the verify_manifest key set")
        eq(verified["complete"], True, "an untouched package verifies complete")
        eq(verified["mismatches"], [], "an untouched package has no mismatch")
        eq(verified["missing"], [], "an untouched package is missing nothing")
        eq(verified["entries_verified"], len(manifest["entries"]),
           "every manifest entry was verified by recomputation")

        clean = corpus_14b.clean_machine_dest(tmp)
        dest = clean["dest"]
        if os.path.exists(os.path.join(dest, journal.JOURNAL_DIRNAME)):
            fail("the clean destination must share no journal")
        if os.listdir(dest):
            fail("the clean destination must start empty")

        for key, value in clean["env"].items():
            os.environ[key] = value
        restored = course_package.restore_package(pkg, dest, "human", "weibao")
        for key, value in saved_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

        if not os.path.exists(os.path.join(dest, journal.JOURNAL_DIRNAME)):
            fail("a restore mints the destination's own journal")
        eq(restored["entries_verified"], len(manifest["entries"]),
           "every entry was verified on restore")
        eq(restored["complete"], True, "the restore reports itself complete")

        restored_sidecar = os.path.join(dest, course.COURSE_SIDECAR_FILENAME)
        eq(open(restored_sidecar, "rb").read(), sidecar_raw,
           "the restored sidecar is byte-identical")
        original_ids = [r["id"] for r in graph.parse_course(
            sidecar_raw.decode("utf-8"))["objectives"]]
        restored_ids = [r["id"] for r in graph.parse_course(
            open(restored_sidecar, encoding="utf-8").read())["objectives"]]
        eq(restored_ids, original_ids, "the restored objective ids")

        registry = journal.read_registry(dest)
        eq(len(registry), len(manifest["entries"]),
           "the destination registry holds one row per restored object")
        if not any(e.get("operation") == "restore"
                   for e in journal.entries(dest)):
            fail("a restore must journal operation=restore")

        # Both loss reports come back, and neither replaces the other.
        eq(restored["losses"], manifest["loss_report"],
           "the export-time loss report travels with the package")
        eq(restored["restore_losses"], [],
           "restore-time losses are their own, separate list")

        # Evidence goes through the one writer, so a restore is idempotent.
        dest_log = evidence.log_path(dest)
        eq(restored["evidence_recorded"], len(seeded),
           "every exported event was recorded in the destination")
        eq(restored["evidence_already_recorded"], 0,
           "a first restore records nothing twice")
        before = len(list(evidence.events(dest_log)))
        again = course_package.restore_package(pkg, dest, "human", "weibao")
        eq(again["evidence_recorded"], 0,
           "a second restore records no new event")
        eq(again["evidence_already_recorded"], len(seeded),
           "a second restore reports every event as already recorded")
        eq(len(list(evidence.events(dest_log))), before,
           "a second restore leaves the destination's event count unchanged")

        # A restore gap is reported against the manifest, never accepted.
        entry = manifest["entries"][0]
        payload = os.path.join(pkg, course_package.PAYLOAD_DIRNAME,
                               entry["object_id"] + ".md")
        raw = open(payload, "rb").read()
        open(payload, "wb").write(raw + b"tampered\n")
        gap = course_package.verify_manifest(pkg)
        eq(gap["complete"], False, "a corrupted payload is not complete")
        eq(len(gap["mismatches"]), 1, "the corrupted entry is reported once")
        eq(gap["mismatches"][0]["expected"], entry["fingerprint"],
           "the mismatch names the expected fingerprint")
        if gap["mismatches"][0]["found"] == entry["fingerprint"]:
            fail("the mismatch must name what was actually found")
        dest2 = os.path.join(tmp, "restore_corrupt")
        os.makedirs(dest2)
        raises(lambda: course_package.restore_package(pkg, dest2, "human",
                                                      "weibao"),
               course_package.PackageError, "package.fingerprint_mismatch",
               "restoring a corrupted payload")
        open(payload, "wb").write(raw)

        os.remove(payload)
        absent = course_package.verify_manifest(pkg)
        eq(len(absent["missing"]), 1, "the deleted payload is reported missing")
        eq(absent["missing"][0]["object_id"], entry["object_id"],
           "the missing report names the entry")
        dest3 = os.path.join(tmp, "restore_missing")
        os.makedirs(dest3)
        raises(lambda: course_package.restore_package(pkg, dest3, "human",
                                                      "weibao"),
               course_package.PackageError, "package.missing_payload",
               "restoring a package with a missing payload")
        open(payload, "wb").write(raw)

        manifest_path = os.path.join(pkg, course_package.MANIFEST_FILENAME)
        saved = open(manifest_path, encoding="utf-8").read()
        open(manifest_path, "w", encoding="utf-8").write("{not json at all")
        raises(lambda: course_package.read_manifest(pkg),
               course_package.PackageError, "package.manifest_unreadable",
               "an unreadable manifest")
        raises(lambda: course_package.restore_package(
                   pkg, os.path.join(tmp, "restore_unreadable"), "human",
                   "weibao"),
               course_package.PackageError, "package.manifest_unreadable",
               "restoring a package with an unreadable manifest")
        open(manifest_path, "w", encoding="utf-8").write(saved)

        # A restore is offline by construction, not by intention.
        for name in ("urllib", "socket", "http", "subprocess"):
            if hasattr(course_package, name):
                fail("course_package.py must not reach %s; a restore is an "
                     "offline operation" % name)
        print("ok  clean-machine restore, validated by recomputation")
    finally:
        for key, value in saved_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        shutil.rmtree(tmp, ignore_errors=True)


def check_archive_containment():
    """A package archive is untrusted input the moment it crosses a machine
    boundary, so every entry is contained before anything is written.

    The oversized-entry assertion lowers `MAX_ENTRY_BYTES` for the duration
    rather than writing a genuine hundred-megabyte declared size. The guard
    under test is the comparison and its refusal, and the shipped ceiling is
    asserted separately as a constant; building a real bomb here would cost a
    hundred megabytes of memory per run to prove the same comparison.
    """
    tmp = tempfile.mkdtemp(prefix="course_package_zip_")
    try:
        eq(course_package.ARCHIVE_FORMATS, (None, "zip"), "ARCHIVE_FORMATS")
        eq(course_package.MAX_ENTRY_BYTES, 104857600,
           "the shipped uncompressed-entry ceiling")

        for name in ("../escape.md", "payload/../../escape.md"):
            archive = os.path.join(tmp, "traversing.zip")
            corpus_14b.build_traversing_archive(archive, name)
            dest = os.path.join(tmp, "extract_dest")
            os.makedirs(dest, exist_ok=True)
            raises(lambda: course_package.extract_archive(archive, dest),
                   course_package.PackageError, "package.path_escape",
                   "the traversing archive entry %r" % name)
            escaped = os.path.join(dest, "..", "escape.md")
            if os.path.exists(escaped):
                fail("a refused entry must never be written: %s exists" % escaped)
            os.remove(archive)

        absolute = os.path.join(tmp, "absolute.zip")
        corpus_14b.build_traversing_archive(
            absolute, "/" + os.path.join(tmp, "escape.md").lstrip("/"))
        raises(lambda: course_package.extract_archive(
                   absolute, os.path.join(tmp, "extract_dest")),
               course_package.PackageError, "package.path_escape",
               "an absolute archive entry name")
        if os.name == "nt":
            drive = os.path.join(tmp, "drive.zip")
            corpus_14b.build_traversing_archive(drive, "C:\\escape.md")
            raises(lambda: course_package.extract_archive(
                       drive, os.path.join(tmp, "extract_dest")),
                   course_package.PackageError, "package.path_escape",
                   "an archive entry naming a drive")

        symlink = corpus_14b.build_symlink_archive(
            os.path.join(tmp, "symlink.zip"))
        if symlink is None:
            print("SKIP: symlink archive assertion (this platform cannot "
                  "write a symlink zip entry)")
        else:
            raises(lambda: course_package.extract_archive(
                       symlink, os.path.join(tmp, "extract_dest")),
                   course_package.PackageError, "package.symlink_payload",
                   "a symbolic-link archive entry")

        raises(lambda: course_package.extract_archive(
                   absolute, os.path.join(tmp, "extract_dest"), "tar"),
               course_package.PackageError, "package.unsupported_archive",
               "an archive format outside ARCHIVE_FORMATS")
        raises(lambda: course_package.extract_archive(
                   absolute, os.path.join(tmp, "extract_dest"), None),
               course_package.PackageError, "package.unsupported_archive",
               "extracting with no archive format at all")

        big = os.path.join(tmp, "oversized.zip")
        with zipfile.ZipFile(big, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("payload/big.md", "x" * 4096)
        ceiling = course_package.MAX_ENTRY_BYTES
        course_package.MAX_ENTRY_BYTES = 16
        try:
            err = raises(lambda: course_package.extract_archive(
                             big, os.path.join(tmp, "extract_big")),
                         course_package.PackageError,
                         "package.unsupported_archive",
                         "an entry declaring more than the ceiling")
            if "payload/big.md" not in err.message:
                fail("an oversized entry must be refused by name")
            if os.path.exists(os.path.join(tmp, "extract_big",
                                           "payload", "big.md")):
                fail("an oversized entry must be refused before it is written")
        finally:
            course_package.MAX_ENTRY_BYTES = ceiling

        # The optional zip transport round trips: tree, archive, tree again.
        root = os.path.join(tmp, "transport_course")
        os.makedirs(root)
        course.create_course(root, "Transport Course", "agent", "corpus-14b")
        corpus_14b.packaged_source(root, "carried-source")
        pkg = os.path.join(tmp, "transport_package")
        manifest = course_package.export_package(root, root, pkg,
                                                  archive="zip")
        archive = pkg + ".zip"
        if not os.path.exists(archive):
            fail("archive='zip' must write the optional transport archive")
        unpacked = os.path.join(tmp, "unpacked_package")
        course_package.extract_archive(archive, unpacked)
        dest = os.path.join(tmp, "transport_restore")
        os.makedirs(dest)
        restored = course_package.restore_package(unpacked, dest, "human",
                                                  "weibao")
        eq(restored["entries_verified"], len(manifest["entries"]),
           "a package that travelled as a zip still restores every entry")

        raises(lambda: course_package.export_package(
                   root, root, os.path.join(tmp, "bad_format"), archive="tar"),
               course_package.PackageError, "package.unsupported_archive",
               "exporting with an unsupported archive format")
        print("ok  archive containment and the optional zip transport")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def kill_export(root, pkg):
    """Run one export in this process and die inside the first payload write.

    The interruption is deterministic rather than timed: a `sleep`-and-kill
    harness races the interpreter's own startup, and what this assertion is
    about is the ordering of the prepared manifest against the first payload,
    not the scheduler.
    """
    def die(path, raw):
        os._exit(9)

    course_package._write_bytes_atomic = die
    course_package.export_package(root, root, pkg)
    return 0


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--kill-export":
        return kill_export(sys.argv[2], sys.argv[3])
    check_manifest_and_losses()
    check_clean_restore()
    check_archive_containment()
    print("OK course_package_roundtrip")
    return 0


if __name__ == "__main__":
    sys.exit(main())
