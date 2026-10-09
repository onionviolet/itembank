#!/usr/bin/env python3
"""Synthetic native restore consent, governance, conflicts and offline reopen.

Primitive process-exit and publication coverage stays in
merged_copy_restore_roundtrip.py. These tests cover the native calling layer.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import course
import course_package
import evidence
import identity
import journal
import workspace
from fixtures import corpus_14b
from surfaces import course_ops, ia, restore_workspace


def files(root):
    return {str(path.relative_to(root)): path.read_bytes()
            for path in Path(root).rglob("*") if path.is_file()}


class Forms(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.forms = []
        self.current = None
        self.feed(html)

    def handle_starttag(self, tag, attributes):
        attributes = dict(attributes)
        if tag == "form":
            self.current = {"action": attributes.get("action"), "fields": {}}
            self.forms.append(self.current)
        elif tag == "input" and self.current is not None and attributes.get("type") == "hidden":
            self.current["fields"][attributes["name"]] = attributes.get("value", "")

    def handle_endtag(self, tag):
        if tag == "form":
            self.current = None


def request(url, fields=None, headers=None):
    data = urllib.parse.urlencode(fields, doseq=True).encode() if fields is not None else None
    req = urllib.request.Request(url, data=data, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status, response.read().decode()
    except urllib.error.HTTPError as error:
        try:
            return error.code, error.read().decode()
        finally:
            error.close()


class NativeRestore(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="native-restore-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        exported = corpus_14b.build_three_domains(str(self.root / "donor"))["domains"][0]
        original = exported["root"]
        corpus_14b.packaged_source(original, "fictional-source")
        corpus_14b.seed_objective_evidence(original, exported["objectives"][0])
        stage = self.root / "export"
        self.manifest = course_package.export_package(original, original, str(stage))
        course_package.ensure_package_namespace(str(self.root))
        self.package = Path(course_package.workspace_package_path(str(self.root), self.manifest["package_id"]))
        stage.rename(self.package)
        self.source = self.root / "original"
        self.source.mkdir()
        # An unrelated accepted object and private files form the populated
        # source, with no competing course sidecar at the package's path.
        self.other_id = identity.new_object_id()
        journal.commit_operation(str(self.source), self.other_id, "lesson", "other.md", "mint",
                                 b"# Fictional unrelated lesson\n", None, "human", "test",
                                 create_if_missing=True, rights={right: "granted" for right in identity.RIGHTS_OPERATIONS})
        (self.source / "private.txt").write_bytes(b"Fictional private draft\n")
        (self.source / "empty").mkdir()
        # Register both roots through the existing accepted workspace owner.
        doc = {"schema_version": 1, "workspace_object_id": identity.new_object_id(),
               "roots": [str(self.root), str(self.source)], "courses": []}
        journal.commit_operation(str(self.root), doc["workspace_object_id"], "workspace", workspace.WORKSPACE_REL_PATH,
            "mint", workspace._serialize(doc), None, "human", "test", create_if_missing=True)
        self.selection = {"package_id": self.manifest["package_id"], "source_choice": "root:1",
                          "destination_root": "0", "destination_name": "restored-fiction"}
        self.dest = self.root / "_packages" / "_restore" / "restored-fiction"

    def preview(self):
        return restore_workspace.apply(str(self.root), dict(self.selection, operation="preview"))

    def accepted_fields(self, preview=None):
        preview = preview or self.preview()
        return dict(self.selection, operation="restore", confirm_copy="yes", confirm_private="yes",
                    **{"expected_" + name: preview[name] for name in
                       ("package_fingerprint", "source_fingerprint", "scope_fingerprint")})

    def restore(self, fields=None):
        return restore_workspace.apply(str(self.root), fields or self.accepted_fields())

    def reopen(self, result):
        return course_ops.reopen_merged_restore(str(self.root), result["destination_root"],
            result["destination_name"], result["course_object_id"], result["course_fingerprint"],
            result["destination_identity"])

    def test_preview_changes_nothing_and_names_exact_private_scope(self):
        before = files(self.root)
        preview = self.preview()
        self.assertEqual(files(self.root), before)
        self.assertFalse(self.dest.exists())
        self.assertIn("private.txt", preview["private_files"])
        self.assertNotIn("other.md", preview["private_files"])
        self.assertEqual(preview["destination"], str(self.dest))
        html = restore_workspace.panel(str(self.root), preview)
        self.assertIn('name="confirm_private" value="yes" required', html)
        self.assertIn('name="confirm_copy" value="yes" required', html)
        self.assertIn('name="expected_scope_fingerprint"', html)
        self.assertIn("private.txt", html)
        self.assertNotIn("<script", html)

    def test_restore_and_explicit_read_only_reopen_preserve_original_and_shelf(self):
        before = files(self.source)
        shelf = ia.course_shelf_state(str(self.root))["cards"]
        result = self.restore()
        self.assertEqual(result["publication"], "whole-root-copy")
        self.assertEqual(files(self.source), before)
        self.assertEqual((self.dest / "private.txt").read_bytes(), b"Fictional private draft\n")
        self.assertEqual(ia.course_shelf_state(str(self.root))["cards"], shelf)
        reopened = self.reopen(result)
        self.assertEqual(reopened["status"], "reopened")
        self.assertEqual(reopened["course_object_id"], self.manifest["course_object_id"])
        html = restore_workspace.panel(str(self.root), result)
        self.assertIn('action="/restore/open"', html)
        self.assertIn('name="destination_device"', html)
        self.assertIn('name="destination_inode"', html)
        self.assertNotIn('href="/course/' + result["course_object_id"], html)
        self.assertIn("Recovered course", restore_workspace.panel(str(self.root), reopened))
        payload = json.dumps(dict(result, course_view=None))
        process = subprocess.run([sys.executable, __file__, "--reopen", str(self.root), payload],
                                 capture_output=True, text=True, timeout=30)
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(process.stdout.strip(), "unchanged")

    def test_cancel_and_missing_consent_do_not_write(self):
        fields = self.accepted_fields()
        before = files(self.root)
        self.assertEqual(restore_workspace.apply(str(self.root), {"operation": ["cancel"]})["status"], "canceled")
        for name in ("confirm_copy", "confirm_private"):
            missing = dict(fields)
            missing.pop(name)
            with self.assertRaises(course_package.PackageError) as raised:
                self.restore(missing)
            self.assertEqual(raised.exception.code, "package.consent_required")
        self.assertEqual(files(self.root), before)

    def test_paths_authority_fields_and_unapproved_roots_refuse(self):
        for name, value in (("destination_name", "../escape"), ("destination_name", "/tmp/escape"),
                            ("destination_root", "99"), ("source_choice", str(self.source)),
                            ("package_id", str(self.package))):
            fields = dict(self.selection, operation="preview")
            fields[name] = value
            with self.assertRaises((ValueError, course_package.PackageError)):
                restore_workspace.apply(str(self.root), fields)
        for name in ("root", "path", "grants", "score"):
            with self.assertRaises(ValueError):
                restore_workspace.apply(str(self.root), dict(self.selection, operation="preview", **{name: "anything"}))
        with self.assertRaises(ValueError):
            restore_workspace.apply(str(self.root), dict(self.selection, operation=["preview", "restore"]))
        self.assertFalse(self.dest.exists())

    def test_unknown_and_denied_rights_refuse_before_source_bytes(self):
        for grant in ("unknown", "denied"):
            row = journal.read_registry(str(self.source))[self.other_id]
            journal.op_grant_rights(str(self.source), self.other_id, {"export": grant},
                                    row["fingerprint"], "human", "test")
            read = course_package._read_relative
            def refuse_source(directory, relative):
                if relative == "private.txt":
                    raise AssertionError("Read private bytes before rights admission")
                return read(directory, relative)
            with mock.patch.object(course_package, "_read_relative", side_effect=refuse_source):
                with self.assertRaises(course_package.PackageError) as raised:
                    self.preview()
            self.assertEqual(raised.exception.code, "package.rights_restricted")
        self.assertFalse(self.dest.exists())

    def test_stale_source_package_and_root_governance_refuse(self):
        fields = self.accepted_fields()
        (self.source / "private.txt").write_bytes(b"Changed fictional draft\n")
        with self.assertRaises(course_package.PackageError) as raised:
            self.restore(fields)
        self.assertEqual(raised.exception.code, "package.preview_changed")
        fields = self.accepted_fields()
        manifest = self.package / "manifest.json"
        manifest.write_bytes(manifest.read_bytes() + b"\n")
        with self.assertRaises(course_package.PackageError) as raised:
            self.restore(fields)
        self.assertEqual(raised.exception.code, "package.preview_changed")
        fields = self.accepted_fields()
        row = workspace.read_workspace(str(self.root))
        doc = row["doc"]
        doc["roots"] = list(reversed(doc["roots"]))
        journal.commit_operation(str(self.root), doc["workspace_object_id"], "workspace", workspace.WORKSPACE_REL_PATH,
            "edit_in_place", workspace._serialize(doc), row["fingerprint"], "human", "test")
        with self.assertRaises(course_package.PackageError):
            self.restore(fields)
        self.assertFalse(self.dest.exists())

    def test_identity_and_immutable_evidence_conflicts_show_recovery(self):
        target = self.source / self.manifest["entries"][0]["relpath"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"Different owner\n")
        before = files(self.source)
        with self.assertRaises(course_package.PackageError) as raised:
            self.preview()
        self.assertEqual(raised.exception.code, "package.object_conflict")
        self.assertEqual(files(self.source), before)
        target.unlink()
        event = dict(course_package.package_snapshot(str(self.package))["evidence"][0])
        event["ts"] = "2026-01-01T00:00:00Z"
        evidence.append_event(evidence.log_path(str(self.source)), event)
        before = files(self.source)
        with self.assertRaises(course_package.PackageError) as raised:
            self.preview()
        self.assertEqual(raised.exception.code, "package.evidence_identity_conflict")
        self.assertEqual(files(self.source), before)

    def test_disk_publication_failure_and_racing_destination_preserve_original(self):
        fields = self.accepted_fields()
        before = files(self.source)
        for name in ("_write_bytes_atomic", "publish_directory"):
            fields = self.accepted_fields()
            with mock.patch.object(course_package, name, side_effect=OSError("injected failure")):
                with self.assertRaises(OSError):
                    self.restore(fields)
            self.assertFalse(self.dest.exists())
            self.assertEqual(files(self.source), before)
        publish = course_package.publish_directory
        fields = self.accepted_fields()
        def race(*args):
            self.dest.mkdir()
            (self.dest / "racer").write_bytes(b"Competing destination\n")
            return publish(*args)
        with mock.patch.object(course_package, "publish_directory", side_effect=race):
            with self.assertRaises(course_package.PackageError):
                self.restore(fields)
        self.assertEqual((self.dest / "racer").read_bytes(), b"Competing destination\n")
        self.assertEqual(files(self.source), before)

    def test_reading_transport_and_links_remain_unsupported(self):
        snapshot = course_package.package_snapshot(str(self.package))
        snapshot["reading_transport_raw"] = b"{}"
        with mock.patch.object(course_package, "package_snapshot", return_value=snapshot):
            with self.assertRaises(course_package.PackageError) as raised:
                self.preview()
        self.assertEqual(raised.exception.code, "package.atomic_merge_unsupported")
        (self.source / "link").symlink_to(self.package)
        with self.assertRaises(course_package.PackageError) as raised:
            self.preview()
        self.assertEqual(raised.exception.code, "package.symlink_payload")
        self.assertFalse(self.dest.exists())

    def test_package_race_uses_exact_preview_bytes_and_reopen_refuses_changed_identity(self):
        fields = self.accepted_fields()
        merge = course_package.restore_merged_copy
        def replace_input(*args, **kwargs):
            # A later live-path edit cannot change the privately pinned input.
            (self.package / "manifest.json").write_bytes(b"broken later package")
            return merge(*args, **kwargs)
        with mock.patch.object(course_package, "restore_merged_copy", side_effect=replace_input):
            result = self.restore(fields)
        self.assertEqual(result["status"], "restored")
        self.assertEqual(self.reopen(result)["status"], "reopened")
        changed = dict(result, destination_identity=[0, 0])
        with self.assertRaises(course_package.PackageError) as raised:
            self.reopen(changed)
        self.assertEqual(raised.exception.code, "package.destination_changed")

    def test_native_http_preview_cancel_restore_exact_reopen_and_restart(self):
        sys.path.insert(0, str(ROOT / "tests"))
        from daemon_roundtrip import start_daemon
        before = files(self.source)
        def stop(process):
            process.terminate()
            process.wait(timeout=10)
            process.stdout.close()
        process, url, _lines = start_daemon(str(self.root))
        self.addCleanup(lambda: stop(process) if process.poll() is None else None)
        status, html = request(url + "restore")
        self.assertEqual(status, 200)
        self.assertIn("Preview exact restore scope", html)
        status, html = request(url + "restore", dict(self.selection, operation="preview"))
        self.assertEqual(status, 200)
        restore_form = next(form for form in Forms(html).forms if form["fields"].get("operation") == "restore")
        accepted = dict(restore_form["fields"], confirm_copy="yes", confirm_private="yes")
        status, _html = request(url + "restore", accepted, {"Origin": "https://untrusted.invalid"})
        self.assertEqual(status, 403)
        self.assertFalse(self.dest.exists())
        status, html = request(url + "restore", {"operation": "cancel"})
        self.assertEqual(status, 200)
        self.assertIn("Nothing was copied", html)
        status, html = request(url + "restore", dict(accepted, confirm_private="no"))
        self.assertEqual(status, 400)
        self.assertIn("Confirm the exact destination", html)
        status, html = request(url + "restore", accepted)
        self.assertEqual(status, 200, html)
        reopened_form = next(form for form in Forms(html).forms if form["action"] == "/restore/open")
        status, html = request(url + "restore/open", reopened_form["fields"])
        self.assertEqual(status, 200, html)
        self.assertIn("Opened the validated recovery copy", html)
        self.assertIn("Objectives", html)
        status, html = request(url + "restore/open", dict(reopened_form["fields"], destination_root="99"))
        self.assertEqual(status, 400)
        status, html = request(url + "restore", dict(self.selection, operation="preview", destination_name=["first", "second"]))
        self.assertEqual(status, 400)
        self.assertEqual(files(self.source), before)
        self.assertEqual(ia.course_shelf_state(str(self.root))["cards"], [])
        stop(process)
        process, url, _lines = start_daemon(str(self.root))
        self.addCleanup(lambda: stop(process) if process.poll() is None else None)
        status, html = request(url + "restore/open", reopened_form["fields"])
        self.assertEqual(status, 200, html)
        self.assertEqual(files(self.source), before)

    def test_separate_process_opens_exact_recovered_course_and_preserves_unknown_rights(self):
        sys.path.insert(0, str(ROOT / "tests"))
        from daemon_roundtrip import start_daemon
        result = self.restore()
        before = files(self.source)
        copy_before = files(self.dest)
        process, url, _lines = start_daemon(str(self.dest))
        try:
            for path in ("courses", "course/" + result["course_object_id"],
                         "course/" + result["course_object_id"] + "/learn",
                         "course/" + result["course_object_id"] + "/sources"):
                status, html = request(url + path)
                self.assertEqual(status, 200, html)
                self.assertIn(course.read_course(str(self.dest))["doc"]["header"]["title"], html)
            copied = journal.read_registry(str(self.dest))
            for entry in self.manifest["entries"]:
                self.assertFalse(identity.rights_granted(copied[entry["object_id"]].get("rights"), "export"))
            self.assertEqual(files(self.source), before)
            # Native views may refresh disposable state, but accepted bytes and
            # the private file never change just by opening the copy.
            for path, raw in copy_before.items():
                self.assertEqual((self.dest / path).read_bytes(), raw)
        finally:
            process.terminate()
            process.wait(timeout=10)
            process.stdout.close()
        self.assertEqual(ia.course_shelf_state(str(self.root))["cards"], [])

    def test_copied_workspace_references_need_review_before_broader_reopen(self):
        doc = {"schema_version": 1, "workspace_object_id": identity.new_object_id(),
               "roots": [str(self.source)], "courses": []}
        journal.commit_operation(str(self.source), doc["workspace_object_id"], "workspace", workspace.WORKSPACE_REL_PATH,
            "mint", workspace._serialize(doc), None, "human", "test", create_if_missing=True,
            rights={right: "granted" for right in identity.RIGHTS_OPERATIONS})
        before = files(self.source)
        preview = self.preview()
        references = preview['workspace_references']
        self.assertEqual(references['proposed_document']['roots'], [str(self.dest)])
        self.assertTrue(references['read_only'])
        self.assertIn('Workspace reference proposal', restore_workspace.panel(str(self.root), preview))
        self.assertEqual(files(self.source), before)
        result = self.restore()
        self.assertFalse(result["direct_course_reopen"])
        html = restore_workspace.panel(str(self.root), result)
        self.assertIn("Review its approved-root references", html)
        self.assertNotIn("itembank daemon", html)
        self.assertEqual(self.reopen(result)["status"], "reopened")
        self.assertEqual(files(self.source), before)

    def test_reference_preview_remaps_internal_and_names_disabled_external_courses(self):
        outside = str(self.root / 'external-not-read')
        doc = {'schema_version': 1, 'workspace_object_id': identity.new_object_id(),
               'roots': [outside, str(self.source), str(self.source / 'nested')],
               'courses': [{'course_object_id': 'external-course', 'root_index': 0, 'path': 'course', 'name': 'External'},
                           {'course_object_id': 'inside-course', 'root_index': 2, 'path': 'course', 'name': 'Inside'}]}
        journal.commit_operation(str(self.source), doc['workspace_object_id'], 'workspace', workspace.WORKSPACE_REL_PATH,
            'mint', workspace._serialize(doc), None, 'human', 'test', create_if_missing=True)
        before = files(self.source)
        preview = workspace.recovery_root_preview(str(self.source), str(self.source), str(self.dest))
        self.assertEqual(preview['roots'][0]['state'], 'requires_reapproval')
        self.assertEqual(preview['proposed_document']['roots'], [str(self.dest), str(self.dest / 'nested')])
        self.assertEqual(preview['proposed_document']['courses'][0]['root_index'], 1)
        self.assertEqual(preview['disabled_courses'][0]['course_object_id'], 'external-course')
        self.assertEqual(files(self.source), before)
        self.assertFalse(Path(outside).exists())

    def test_reference_error_is_actionable_and_preserves_restore_inputs(self):
        before = files(self.source)
        with mock.patch.object(workspace, 'recovery_root_preview', side_effect=workspace.WorkspaceError(
                'workspace.conflict', 'Reconcile the workspace record before previewing recovery references.')):
            with self.assertRaises(course_package.PackageError) as error:
                self.preview()
        self.assertEqual(error.exception.code, 'workspace.conflict')
        self.assertEqual(files(self.source), before)
        self.assertFalse(self.dest.exists())


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--reopen":
        root, raw = sys.argv[2:]
        result = json.loads(raw)
        course_ops.reopen_merged_restore(root, result["destination_root"], result["destination_name"],
            result["course_object_id"], result["course_fingerprint"], result["destination_identity"])
        retry = course_package.restore_package(result["package_path"], result["destination"],
                                               "human", "test", require_root_atomic=True)
        print(retry["publication"])
    else:
        unittest.main()
