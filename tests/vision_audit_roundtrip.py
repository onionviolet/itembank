#!/usr/bin/env python3
"""Synthetic regressions for exact vision references and conservative coverage."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "vision_audit.py"


def entry(title, paths=""):
    return (f"### 2099-01-01: {title}\n\n"
            "#### Interpretation recorded 2099-01-01\n\n"
            f"**Planning effect:** {paths}\n\n"
            "**Relationship to prior entries:** Independent input.\n\n")


class VisionAuditTests(unittest.TestCase):
    def run_audit(self, vision, files):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            files = {".planning/USER-VISION.md": vision, **files}
            for name, content in files.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
            before = {p.relative_to(root): p.read_bytes()
                      for p in root.rglob("*") if p.is_file()}
            result = subprocess.run([sys.executable, str(SCRIPT)], cwd=root,
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(before, {p.relative_to(root): p.read_bytes()
                                     for p in root.rglob("*") if p.is_file()})
            return result.stdout

    def test_unrelated_basename_and_date_do_not_resolve(self):
        out = self.run_audit(entry("absent direction", "`missing/ghost.md`"), {
            "elsewhere/ghost.md": "unrelated",
            ".planning/unrelated.md": "2099-01-01",
        })
        self.assertIn("Named files that do not exist: 1", out)
        self.assertIn("Entries nothing downstream mentions: 1", out)

    def test_exact_roots_and_ambiguous_basename(self):
        out = self.run_audit(entry("paths", "`ok.md` `src/code.py` `both.md`"), {
            ".planning/ok.md": "ok", "src/code.py": "# ok",
            "both.md": "one", ".planning/both.md": "two",
        })
        self.assertIn("Named files structurally resolved: 2", out)
        self.assertIn("Named files with ambiguous roots: 1", out)
        self.assertIn("Named files that do not exist: 0", out)

    def test_same_date_entries_need_distinct_links(self):
        out = self.run_audit(entry("first direction") + entry("second direction"), {
            ".planning/nested/plan.md":
                "[first](../USER-VISION.md#2099-01-01-first-direction)\n"
                "second direction was discussed on 2099-01-01",
        })
        self.assertIn("Entries with structurally verified downstream links: 1", out)
        self.assertIn("Entries nothing downstream mentions: 1", out)
        self.assertIn("Unverified title-text candidates: 1", out)

    def test_wrong_target_and_unknown_anchor_remain_unresolved(self):
        out = self.run_audit(entry("direction"), {
            ".planning/plan.md":
                "[wrong](missing/USER-VISION.md#2099-01-01-direction)\n"
                "[unknown](USER-VISION.md#2099-01-01-other)\n"
                "[legacy][vision]\n[vision]: USER-VISION.md\n",
        })
        self.assertIn("Unresolved local vision links: 2", out)
        self.assertIn("Entries nothing downstream mentions: 1", out)
        self.assertIn("reference-style", out)

    def test_duplicate_heading_anchors(self):
        out = self.run_audit(entry("same") + entry("same"), {
            ".planning/plan.md":
                "[second](USER-VISION.md#2099-01-01-same-1)",
        })
        self.assertIn("Entries with structurally verified downstream links: 1", out)
        self.assertIn("Entries nothing downstream mentions: 1", out)


if __name__ == "__main__":
    unittest.main()
