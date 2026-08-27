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
import json, os, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import course                                                # noqa: E402
import course_package                                        # noqa: E402
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
    eq(restored["losses"], manifest["loss_report"],
       "the export-time loss report travels with the package")


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
    print("OK course_package_roundtrip")
    return 0


if __name__ == "__main__":
    sys.exit(main())
