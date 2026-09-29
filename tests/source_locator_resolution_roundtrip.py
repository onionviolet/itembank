"""An exact citation resolves a repeated passage without searching its text."""

import json
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import identity
import journal
import source_adapters


class SourceLocatorResolutionTest(unittest.TestCase):
    def test_second_duplicate_and_changed_revision(self):
        with tempfile.TemporaryDirectory(prefix="locator-resolution-") as base:
            raw_path = os.path.join(base, "passages.md")
            with open(raw_path, "w", encoding="utf-8") as stream:
                stream.write("First context\nSame sentence.\nSecond context\nSame sentence.\n")
            rights = {operation: "granted" for operation in identity.RIGHTS_OPERATIONS}
            raw_id = journal.op_link(base, "source", "passages.md", "human",
                                     "tester", rights=rights)["object_id"]
            imported = source_adapters.import_source(base, "markdown", raw_id,
                                                      "human", "tester")
            self.assertEqual(imported["status"], "ok")
            with open(os.path.join(base, imported["sidecar_rel_path"]),
                      encoding="utf-8") as stream:
                sidecar = json.load(stream)
            source_id = imported["source_id"]
            fingerprint = sidecar["fingerprint"]
            first = source_adapters.resolve_locator(base, source_id, "L2", fingerprint)
            second = source_adapters.resolve_locator(base, source_id, "L4", fingerprint)
            self.assertEqual(first["status"], "ok", first)
            self.assertEqual(second["status"], "ok", second)
            self.assertEqual(first["text"], second["text"])
            self.assertNotEqual(first["span_id"], second["span_id"])
            self.assertEqual(second["origin"]["line"], 4)
            self.assertEqual(source_adapters.resolve_locator(
                base, source_id, "L4", "sha256:" + "0" * 64)["status"],
                "stale")
            journal.op_grant_rights(base, source_id, {"read": "denied"},
                                    fingerprint, "human", "tester")
            self.assertEqual(source_adapters.resolve_locator(
                base, source_id, "L4", fingerprint)["status"], "unsupported")
            journal.op_grant_rights(base, source_id, {"read": "granted"},
                                    fingerprint, "human", "tester")

            with open(os.path.join(base, imported["md_rel_path"]), "a",
                      encoding="utf-8") as stream:
                stream.write("Changed\n")
            stale = source_adapters.resolve_locator(base, source_id, "L4", fingerprint)
            self.assertEqual(stale["status"], "stale")

    def test_missing_locator_and_sidecar_conflict(self):
        with tempfile.TemporaryDirectory(prefix="locator-resolution-") as base:
            with open(os.path.join(base, "passages.md"), "w", encoding="utf-8") as stream:
                stream.write("A sentence.\n")
            rights = {operation: "granted" for operation in identity.RIGHTS_OPERATIONS}
            raw_id = journal.op_link(base, "source", "passages.md", "human",
                                     "tester", rights=rights)["object_id"]
            imported = source_adapters.import_source(base, "markdown", raw_id,
                                                      "human", "tester")
            source_id = imported["source_id"]
            sidecar_path = os.path.join(base, imported["sidecar_rel_path"])
            with open(sidecar_path, encoding="utf-8") as stream:
                sidecar = json.load(stream)
            fingerprint = sidecar["fingerprint"]
            self.assertEqual(source_adapters.resolve_locator(
                base, source_id, "L99", fingerprint)["status"], "unsupported")
            sidecar["source_id"] = "0" * 16
            with open(sidecar_path, "w", encoding="utf-8") as stream:
                json.dump(sidecar, stream)
            self.assertEqual(source_adapters.resolve_locator(
                base, source_id, "L1", fingerprint)["status"], "stale")


if __name__ == "__main__":
    unittest.main()
